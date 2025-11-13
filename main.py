from src.config.settings import load_config
from src.config import constants
from src.adapters.factory import AdapterFactory
from src.email_client.client import MailClient
from src.file_utils.unzip_att import FileExtractor
from src.file_utils.move_file import FileMover
from src.file_utils.csv_transformer import CsvTransformer
from src.data_processing.data_processor import DataProcessor
from src.notion_client.client import NotionClient

def bill_to_notion(payment_platform):
    """Fetches, processes, and sends billing data to Notion."""
    # Create adapter for the platform
    adapter = AdapterFactory.create(payment_platform)

    # Load configuration
    username, password, imap_url, data_source_id, token = load_config()

    # ensure default directories exist
    constants.ensure_dirs()

    # Fetch and download email attachments
    email_client = MailClient(
        username,
        password,
        imap_url,
        adapter,
        attachment_dir=str(constants.ATTACHMENT_DIR),
    )
    email_client.connect()
    email_client.fetch_mail()
    
    for num in reversed(email_client.email_list):
        email_client.get_mail_info(num)
        if email_client.get_passwd():
            break
    
    if not email_client.paswd:
        raise Exception("Failed to retrieve the password from email.")

    for num in reversed(email_client.email_list):
        email_client.get_mail_info(num)
        if email_client.fetch_mail_attachment():
            break

    # Unzip and move the bill file
    extractor = FileExtractor(str(constants.ATTACHMENT_DIR), str(constants.BILL_RAW_DIR), email_client.paswd, payment_platform)
    files = extractor.search_files()
    extractor.unzip_earliest_file(files)
    
    mover = FileMover(str(constants.BILL_RAW_DIR), str(constants.PROJECT_ROOT), adapter)
    mover.copy_file()

    # Process and upload to Notion
    transformer = CsvTransformer(adapter)
    transformer.transform_to_standard_csv()
    
    processor = DataProcessor(transformer.path_std, adapter)
    processor.process_mandatory_fields()
    
    notion_client = NotionClient(data_source_id, token, adapter)
    df_processed = processor.get_processed_data()
    df_processed.apply(notion_client.process_row, axis=1)

def main():
    """Main entry point for the application."""
    try:
        flag = int(input("Select platform (0: wechatpay, 1: alipay, 2: all): "))
        platforms = {0: ("wechatpay",), 1: ("alipay",), 2: ("alipay", "wechatpay")}
        
        if flag not in platforms:
            raise ValueError("Invalid input. Please enter 0, 1, or 2.")
            
        for platform in platforms[flag]:
            print(f"Processing {platform}...")
            bill_to_notion(platform)
            print(f"{platform} processed successfully!")
            
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
