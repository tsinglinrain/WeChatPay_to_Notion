from src.utils import config_env
from typing import Tuple, Optional
from src.core.mail_client.mail_client import MailClient, PaymentPlatform, Directories
from src.core.file_handler.unzip_att import FileExtractor
from src.core.file_handler.move_file import FileMover
from src.core.log_core.logging_config import get_logger

# 获取当前模块的日志器
logger = get_logger(__name__)


def launch_signal(client: MailClient) -> None:
    """
    检测是否有发射信号邮件
    
    Args:
        client: 邮件客户端实例
    """
    if not client.email_list:
        logger.warning("No emails found for launch signal check")
        return
        
    for num in reversed(client.email_list):
        client.get_mail_info(num)
        if client.from_addr == client.username and client.subject == "原神启动!":
            logger.info("Launch signal detected successfully")
            logger.info("时机已到,今日起兵!")
            break


def config_loader() -> Tuple[str, str, str, str, str]:
    """
    从环境变量加载配置
    
    Returns:
        Tuple[str, str, str, str, str]: (username, password, imap_url, database_id, token)
    """
    return config_env.config_loader()


def get_attachment(client: MailClient) -> None:
    """
    获取邮件附件（使用新的静态方法和传统方法的混合实现）
    
    Args:
        client: 邮件客户端实例
        
    Raises:
        Exception: 当无法获取密码时
    """
    if not client.payment_platform:
        raise ValueError("Payment platform not specified in client")
    
    # 方法1：使用新的静态方法（推荐）
    try:
        logger.info("Attempting to use new static method for email processing")
        success, password = MailClient.process_payment_platform_emails(client.payment_platform)
        
        if success:
            logger.info(f"Successfully processed emails using static method. Password: {password}")
            client.passwd = password  # 设置密码以供后续使用
            return
        else:
            logger.warning("Static method failed, falling back to traditional method")
            
    except Exception as e:
        logger.error(f"Static method error: {e}")
        logger.info("Falling back to traditional method")
    
    # 方法2：传统方法作为备用
    logger.info("Using traditional email processing method")
    if not client.email_list:
        raise Exception("No emails found in client")
    
    # 查找密码邮件
    for num in reversed(client.email_list):
        client.get_mail_info(num)
        if client.get_passwd():
            logger.info("Get password successfully using traditional method")
            break
    
    if not client.passwd:
        raise Exception(
            "Can't get password, maybe you forget to send the password email."
        )
    
    # 下载附件
    logger.info("Searching for attachments...")
    for num in reversed(client.email_list):
        client.get_mail_info(num)
        if client.fetch_mail_attachment():
            logger.info("Download attachment successfully using traditional method")
            break


def unzip_attachment(path_att: str, path_target: str, password: str, payment_platform: str) -> str:
    """
    解压附件文件
    
    Args:
        path_att: 附件路径
        path_target: 目标路径
        password: 解压密码
        payment_platform: 支付平台类型
        
    Returns:
        str: 解压结果消息
    """
    extractor = FileExtractor(path_att, path_target, password, payment_platform)
    files = extractor.search_files()
    msg = extractor.unzip_earliest_file(files)
    return msg


def move_file(csv_csv_path: str, target_path: str, payment_platform: str) -> None:
    """
    移动CSV文件到目标位置
    
    Args:
        csv_csv_path: CSV文件源路径
        target_path: 目标路径
        payment_platform: 支付平台类型
    """
    mover = FileMover(csv_csv_path, target_path, payment_platform)
    mover.copy_file()


def main() -> None:
    """
    主函数：执行完整的邮件处理流程
    """
    try:
        # 加载配置文件
        username, password, imap_url, database_id, token = config_loader()

        # 连接邮箱,获取附件
        # payment_platform = PaymentPlatform.ALIPAY  # 使用常量而不是字符串
        payment_platform = PaymentPlatform.WECHATPAY  # 微信支付选项
        
        logger.info(f"Starting email processing for platform: {payment_platform}")
        
        with MailClient(username, password, imap_url, payment_platform) as client:
            client.connect()
            client.fetch_mail()
            get_attachment(client)

            # 解压附件
            path_att = Directories.ATTACHMENT
            path_target = Directories.BILL_CSV_RAW
            msg = unzip_attachment(path_att, path_target, client.passwd, payment_platform)
            logger.info(f"Unzip result: {msg}")

            # 移动文件
            csv_csv_path = Directories.BILL_CSV_RAW
            target_path = Directories.BILL_CSV_PROCESSED
            move_file(csv_csv_path, target_path, payment_platform)
            logger.info("File processing completed successfully")
            
    except Exception as e:
        logger.error(f"Main function error: {e}")
        raise


if __name__ == "__main__":
    main()
