from src.config.settings import load_config
from src.config import constants
from src.adapters.factory import AdapterFactory
from src.email_client.client import MailClient
from src.file_utils.unzip_att import FileExtractor
from src.file_utils.move_file import FileMover
from src.file_utils.csv_transformer import CsvTransformer
from src.data_processing.data_processor import DataProcessor
from src.notion_client.client import NotionClient
from src.utils.logger import setup_logger
import logging

def bill_to_notion(payment_platform, logger):
    """Fetches, processes, and sends billing data to Notion."""
    logger.info(f"Starting bill import for platform: {payment_platform}")
    
    # Create adapter for the platform
    adapter = AdapterFactory.create(payment_platform)
    logger.info(f"Created adapter for {adapter.get_notion_display_name()}")

    # Load configuration
    username, password, imap_url, data_source_id, token = load_config()
    logger.info("Configuration loaded successfully")

    # ensure default directories exist
    constants.ensure_dirs()
    logger.debug("Ensured directories exist")

    # Fetch and download email attachments
    logger.info("Connecting to email server...")
    email_client = MailClient(
        username,
        password,
        imap_url,
        adapter,
        attachment_dir=str(constants.ATTACHMENT_DIR),
    )
    email_client.connect()
    email_client.fetch_mail()
    
    logger.info("Searching for password email...")
    for num in reversed(email_client.email_list):
        email_client.get_mail_info(num)
        if email_client.get_passwd():
            break
    
    if not email_client.paswd:
        logger.error("Failed to retrieve the password from email")
        raise Exception("Failed to retrieve the password from email.")

    logger.info("Searching for bill attachment email...")
    for num in reversed(email_client.email_list):
        email_client.get_mail_info(num)
        if email_client.fetch_mail_attachment():
            break

    # Unzip and move the bill file
    logger.info("Extracting bill file...")
    extractor = FileExtractor(str(constants.ATTACHMENT_DIR), str(constants.BILL_RAW_DIR), email_client.paswd, payment_platform)
    files = extractor.search_files()
    extractor.unzip_earliest_file(files)
    
    logger.info("Moving and processing bill file...")
    mover = FileMover(str(constants.BILL_RAW_DIR), str(constants.PROJECT_ROOT), adapter)
    mover.copy_file()

    # Process and upload to Notion
    logger.info("Transforming CSV to standard format...")
    transformer = CsvTransformer(adapter)
    transformer.transform_to_standard_csv()
    
    logger.info("Processing data fields...")
    processor = DataProcessor(transformer.path_std, adapter)
    processor.process_mandatory_fields()
    
    logger.info("Uploading to Notion...")
    notion_client = NotionClient(data_source_id, token, adapter)
    df_processed = processor.get_processed_data()
    df_processed.apply(notion_client.process_row, axis=1)
    
    logger.info(f"Successfully completed bill import for {payment_platform}")

def main():
    """Main entry point for the application."""
    # Setup logger with both console and file output
    logger = setup_logger(
        name="bill2notion",
        level=logging.INFO,
        log_file="logs/bill2notion.log",
        console=True
    )
    
    logger.info("=" * 60)
    logger.info("Bill2Notion Application Started")
    logger.info("=" * 60)
    
    try:
        flag = int(input("Select platform (0: wechatpay, 1: alipay, 2: all): "))
        platforms = {0: ("wechatpay",), 1: ("alipay",), 2: ("alipay", "wechatpay")}
        
        if flag not in platforms:
            logger.error("Invalid input received")
            raise ValueError("Invalid input. Please enter 0, 1, or 2.")
            
        for platform in platforms[flag]:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing {platform}...")
            logger.info(f"{'='*60}")
            bill_to_notion(platform, logger)
            logger.info(f"✓ {platform} processed successfully!")
            
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")
    finally:
        logger.info("=" * 60)
        logger.info("Bill2Notion Application Finished")
        logger.info("=" * 60)

if __name__ == "__main__":
    main()
