from src.core import BillImportService
from src.utils.logger import setup_logger
import logging

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
        # Create service instance from environment configuration
        service = BillImportService.from_env(logger)
        
        # Get user input for platform selection
        flag = int(input("Select platform (0: wechatpay, 1: alipay, 2: all): "))
        platforms = {0: ("wechatpay",), 1: ("alipay",), 2: ("alipay", "wechatpay")}
        
        if flag not in platforms:
            logger.error("Invalid input received")
            raise ValueError("Invalid input. Please enter 0, 1, or 2.")
        
        results = []
        
        # Process each selected platform
        for platform in platforms[flag]:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing {platform}...")
            logger.info(f"{'='*60}")
            
            result = service.import_bill(platform)
            results.append(result)
            
            # Print result to console
            print(f"\n{result}")
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        
        success_count = sum(1 for r in results if r.success)
        total_records = sum(r.records_processed for r in results if r.success)
        
        for result in results:
            logger.info(str(result))
        
        logger.info(f"\nTotal: {success_count}/{len(results)} platforms succeeded")
        logger.info(f"Total records imported: {total_records}")
            
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"\nError: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        logger.info("=" * 60)
        logger.info("Bill2Notion Application Finished")
        logger.info("=" * 60)

if __name__ == "__main__":
    main()
