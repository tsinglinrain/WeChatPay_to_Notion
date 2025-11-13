"""Bill import service for orchestrating the complete import workflow."""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from src.config.settings import load_config
from src.config import constants
from src.adapters.factory import AdapterFactory
from src.adapters.base import PaymentAdapter
from src.email_client.client import MailClient
from src.file_utils.unzip_att import FileExtractor
from src.file_utils.move_file import FileMover
from src.file_utils.csv_transformer import CsvTransformer
from src.data_processing.data_processor import DataProcessor
from src.notion_client.client import NotionClient
from src.utils.logger import get_logger
from src.core.exceptions import (
    ConfigurationError,
    PasswordNotFoundError,
    AttachmentNotFoundError,
    ExtractionError,
    DataProcessingError,
    NotionUploadError,
)


@dataclass
class ImportResult:
    """Result of a bill import operation."""
    
    success: bool
    platform: str
    records_processed: int = 0
    error_message: Optional[str] = None
    
    def __str__(self):
        if self.success:
            return f"✓ {self.platform}: Successfully imported {self.records_processed} records"
        else:
            return f"✗ {self.platform}: Failed - {self.error_message}"


class BillImportService:
    """Service for orchestrating the complete bill import workflow.
    
    This service encapsulates the entire business logic for importing bills
    from email attachments and uploading them to Notion.
    """
    
    def __init__(self, config: tuple, logger=None):
        """Initialize the service with configuration.
        
        Args:
            config: Tuple of (username, password, imap_url, data_source_id, token)
            logger: Logger instance (will create one if not provided)
        """
        self.username, self.password, self.imap_url, self.data_source_id, self.token = config
        self.logger = logger or get_logger()
        
        # Ensure directories exist
        constants.ensure_dirs()
    
    @classmethod
    def from_env(cls, logger=None):
        """Create service instance from environment variables.
        
        Args:
            logger: Logger instance (optional)
            
        Returns:
            BillImportService instance
            
        Raises:
            ConfigurationError: If configuration is invalid or missing
        """
        try:
            config = load_config()
            return cls(config, logger)
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def import_bill(self, platform: str) -> ImportResult:
        """Execute the complete bill import workflow for a platform.
        
        Args:
            platform: Payment platform ('alipay' or 'wechatpay')
            
        Returns:
            ImportResult with operation status and details
        """
        self.logger.info(f"Starting bill import for platform: {platform}")
        
        try:
            # 1. Prepare adapter
            adapter = self._prepare_adapter(platform)
            
            # 2. Fetch from email
            password, attachment_downloaded = self._fetch_from_email(adapter)
            
            # 3. Process bill file
            csv_file = self._process_bill_file(password, platform, adapter)
            
            # 4. Process data
            processed_data = self._process_data(csv_file, adapter)
            
            # 5. Upload to Notion
            records_count = self._upload_to_notion(processed_data, adapter)
            
            self.logger.info(f"Successfully completed bill import for {platform}")
            return ImportResult(
                success=True,
                platform=platform,
                records_processed=records_count
            )
            
        except Exception as e:
            self.logger.exception(f"Failed to import bills for {platform}: {e}")
            return ImportResult(
                success=False,
                platform=platform,
                error_message=str(e)
            )
    
    def _prepare_adapter(self, platform: str) -> PaymentAdapter:
        """Create and prepare payment platform adapter.
        
        Args:
            platform: Payment platform name
            
        Returns:
            PaymentAdapter instance
        """
        self.logger.info(f"Creating adapter for {platform}")
        adapter = AdapterFactory.create(platform)
        self.logger.info(f"Created adapter for {adapter.get_notion_display_name()}")
        return adapter
    
    def _fetch_from_email(self, adapter: PaymentAdapter) -> tuple[str, bool]:
        """Fetch password and bill attachment from email.
        
        Args:
            adapter: Payment platform adapter
            
        Returns:
            Tuple of (password, attachment_downloaded_flag)
            
        Raises:
            PasswordNotFoundError: If password email not found
            AttachmentNotFoundError: If bill attachment not found
        """
        self.logger.info("Connecting to email server...")
        
        email_client = MailClient(
            self.username,
            self.password,
            self.imap_url,
            adapter,
            attachment_dir=str(constants.ATTACHMENT_DIR),
        )
        
        try:
            email_client.connect()
            email_client.fetch_mail()
        except Exception as e:
            raise ConfigurationError(f"Failed to connect to email server: {e}")
        
        # Find password email
        self.logger.info("Searching for password email...")
        password_found = False
        for num in reversed(email_client.email_list):
            email_client.get_mail_info(num)
            if email_client.get_passwd():
                password_found = True
                break
        
        if not password_found or not email_client.paswd:
            raise PasswordNotFoundError(
                f"Password email not found for {adapter.platform_name}. "
                f"Please send password email to yourself with subject: "
                f"{adapter.platform_name}解压密码XXXXXX"
            )
        
        # Find bill attachment email
        self.logger.info("Searching for bill attachment email...")
        attachment_found = False
        for num in reversed(email_client.email_list):
            email_client.get_mail_info(num)
            if email_client.fetch_mail_attachment():
                attachment_found = True
                break
        
        if not attachment_found:
            raise AttachmentNotFoundError(
                f"Bill attachment email not found for {adapter.platform_name}"
            )
        
        return email_client.paswd, attachment_found
    
    def _process_bill_file(self, password: str, platform: str, adapter: PaymentAdapter) -> str:
        """Extract and process the bill file.
        
        Args:
            password: Extraction password
            platform: Payment platform name
            adapter: Payment platform adapter
            
        Returns:
            Path to processed CSV file
            
        Raises:
            ExtractionError: If file extraction fails
        """
        self.logger.info("Extracting bill file...")
        
        extractor = FileExtractor(
            str(constants.ATTACHMENT_DIR),
            str(constants.BILL_RAW_DIR),
            password,
            platform
        )
        
        try:
            files = extractor.search_files()
            result = extractor.unzip_earliest_file(files)
            if "No zip files" in result:
                raise ExtractionError(result)
        except Exception as e:
            raise ExtractionError(f"Failed to extract bill file: {e}")
        
        self.logger.info("Moving and processing bill file...")
        
        mover = FileMover(
            str(constants.BILL_RAW_DIR),
            str(constants.PROJECT_ROOT),
            adapter
        )
        
        try:
            mover.copy_file()
        except Exception as e:
            raise ExtractionError(f"Failed to move bill file: {e}")
        
        self.logger.info("Transforming CSV to standard format...")
        
        transformer = CsvTransformer(adapter)
        try:
            transformer.transform_to_standard_csv()
        except Exception as e:
            raise DataProcessingError(f"Failed to transform CSV: {e}")
        
        return transformer.path_std
    
    def _process_data(self, csv_file: str, adapter: PaymentAdapter):
        """Process and validate bill data.
        
        Args:
            csv_file: Path to CSV file
            adapter: Payment platform adapter
            
        Returns:
            Processed DataFrame
            
        Raises:
            DataProcessingError: If data processing fails
        """
        self.logger.info("Processing data fields...")
        
        try:
            processor = DataProcessor(csv_file, adapter)
            processor.process_mandatory_fields()
            return processor.get_processed_data()
        except Exception as e:
            raise DataProcessingError(f"Failed to process data: {e}")
    
    def _upload_to_notion(self, data, adapter: PaymentAdapter) -> int:
        """Upload processed data to Notion.
        
        Args:
            data: Processed DataFrame
            adapter: Payment platform adapter
            
        Returns:
            Number of records uploaded
            
        Raises:
            NotionUploadError: If upload fails
        """
        self.logger.info("Uploading to Notion...")
        
        try:
            notion_client = NotionClient(self.data_source_id, self.token, adapter)
            data.apply(notion_client.process_row, axis=1)
            return len(data)
        except Exception as e:
            raise NotionUploadError(f"Failed to upload to Notion: {e}")
