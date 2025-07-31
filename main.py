import project_init

import main_mail as main_mail
import main_notion as main_notion
from notion_core.notion_client_cus import NotionClient
from mail_core.mail_client import MailClient, PaymentPlatform
import config_duplicate
from log_core.logging_config import get_logger

# 获取当前模块的日志器
logger = get_logger(__name__)


def bill_to_notion(payment_platform: str) -> None:
    """
    处理指定支付平台的账单数据并导入Notion
    
    Args:
        payment_platform: 支付平台类型 ('alipay' 或 'wechatpay')
        
    Raises:
        ValueError: 当支付平台类型无效时
    """
    # 验证支付平台
    if not PaymentPlatform.is_valid_platform(payment_platform):
        raise ValueError(
            f"Invalid payment platform: {payment_platform}. "
            f"Supported platforms: {PaymentPlatform.get_all_platforms()}"
        )

    logger.info(f"Starting bill processing for platform: {payment_platform}")

    # 检查并复制配置文件
    config_duplicate.check_and_copy_config()

    # 加载配置文件
    username, password, imap_url, database_id, token = main_mail.config_loader()
    logger.info("Configuration loaded successfully")

    # 连接邮箱,获取附件
    with MailClient(username, password, imap_url, payment_platform) as client:
        client.connect()
        client.fetch_mail()
        main_mail.get_attachment(client)

        # 解压附件
        path_att = "./attachment"
        path_target = "./bill_csv_raw"
        msg = main_mail.unzip_attachment(
            path_att, path_target, client.passwd, payment_platform
        )
        logger.info(f"Unzip result: {msg}")

        # 移动文件
        csv_csv_path = "bill_csv_raw"
        target_path = "./"
        main_mail.move_file(csv_csv_path, target_path, payment_platform)
        logger.info("Files moved successfully")

    # 初始化 NotionClient 并处理数据
    notionclient = NotionClient(database_id, token, payment_platform)
    main_notion.process_apply(notionclient, payment_platform)
    logger.info(f"Successfully processed {payment_platform} bills to Notion")


def main() -> None:
    """主函数：处理用户输入并执行账单导入流程"""
    try:
        # 获取用户输入
        flag = input(
            "Which platform's billing data do you want to import, or all of them? \n"
            "(0(wechatpay), 1(alipay), 2(all)): "
        )
        flag = int(flag)
        
        # 根据输入确定处理的平台
        if flag == 0:
            platforms = (PaymentPlatform.WECHATPAY,)
        elif flag == 1:
            platforms = (PaymentPlatform.ALIPAY,)
        elif flag == 2:
            platforms = (PaymentPlatform.ALIPAY, PaymentPlatform.WECHATPAY)
        else:
            raise ValueError("Invalid input, please enter 0, 1 or 2.")
            
        logger.info(f"User selected platforms: {platforms}")

        # 处理每个平台
        for platform in platforms:
            logger.info(f"Processing {platform}...")
            bill_to_notion(platform)
            logger.info(f"{platform} processed successfully!")
            logger.info("=" * 40)
            
        logger.info("All platforms processed successfully!")
        
    except ValueError as e:
        logger.error(f"Input validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        raise


if __name__ == "__main__":
    main()
