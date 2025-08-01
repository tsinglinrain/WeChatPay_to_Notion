import os
import sys
import imaplib
import email
import re
from pathlib import Path
from typing import Optional, List, Tuple, Dict
from email.header import decode_header
from email.utils import parseaddr
from email.message import Message

import requests
from lxml import html
from urllib.parse import unquote

from src.core.log_core.logging_config import get_logger
from src.utils.config_env import get_email_config

# 模块导出
__all__ = [
    'MailClient',
    'PaymentPlatform', 
    'EmailSenders',
    'SubjectPatterns',
    'ContentTypes',
    'Directories'
]

# 获取当前模块的日志器
logger = get_logger(__name__)

# 常量定义
class PaymentPlatform:
    """支付平台常量"""
    ALIPAY = "alipay"
    WECHATPAY = "wechatpay"
    
    @classmethod
    def get_all_platforms(cls) -> List[str]:
        """获取所有支持的支付平台"""
        return [cls.ALIPAY, cls.WECHATPAY]
    
    @classmethod
    def is_valid_platform(cls, platform: str) -> bool:
        """检查是否为有效的支付平台"""
        return platform in cls.get_all_platforms()


class EmailSenders:
    """邮件发送者地址常量"""
    ALIPAY = "service@mail.alipay.com"
    WECHATPAY = "wechatpay@tencent.com"
    
    @classmethod
    def get_sender_for_platform(cls, platform: str) -> Optional[str]:
        """根据支付平台获取对应的发送者地址"""
        mapping = {
            PaymentPlatform.ALIPAY: cls.ALIPAY,
            PaymentPlatform.WECHATPAY: cls.WECHATPAY,
        }
        return mapping.get(platform)


class SubjectPatterns:
    """邮件主题模式常量"""
    ALIPAY_PASSWORD = r"^alipay解压密码[0-9]{6}$"
    WECHATPAY_PASSWORD = r"^wechatpay解压密码[0-9]{6}$"
    
    @classmethod
    def get_pattern_for_platform(cls, platform: str) -> Optional[str]:
        """根据支付平台获取对应的密码邮件主题模式"""
        mapping = {
            PaymentPlatform.ALIPAY: cls.ALIPAY_PASSWORD,
            PaymentPlatform.WECHATPAY: cls.WECHATPAY_PASSWORD,
        }
        return mapping.get(platform)


class ContentTypes:
    """内容类型常量"""
    TEXT_HTML = "text/html"
    TEXT_PLAIN = "text/plain"
    MULTIPART_MIXED = "multipart/mixed"
    MULTIPART_ALTERNATIVE = "multipart/alternative"


class Directories:
    """目录常量"""
    ATTACHMENT = "data/raw/attachments"
    BILL_CSV_RAW = "data/raw/bills"
    BILL_CSV_PROCESSED = "data/processed"


class MailClient:
    """邮件客户端类，用于连接邮箱并处理账单邮件"""
    
    def __init__(self, username: str, password: str, imap_url: str, payment_platform: Optional[str] = None) -> None:
        """
        初始化邮件客户端
        
        Args:
            username: 邮箱用户名
            password: 邮箱密码
            imap_url: IMAP服务器地址
            payment_platform: 支付平台类型 ('alipay' 或 'wechatpay')
            
        Raises:
            ValueError: 当支付平台类型无效时
        """
        # 验证输入参数
        if not username or not password or not imap_url:
            raise ValueError("Username, password, and imap_url cannot be empty")
            
        if payment_platform and not PaymentPlatform.is_valid_platform(payment_platform):
            raise ValueError(f"Unsupported payment platform: {payment_platform}. "
                           f"Supported platforms: {PaymentPlatform.get_all_platforms()}")
            
        self.username = username
        self.password = password
        self.imap_url = imap_url
        self.payment_platform = payment_platform
        
        # 邮件相关属性
        self.mail: Optional[imaplib.IMAP4_SSL] = None
        self.email_list: Optional[List[bytes]] = None
        self.email_message: Optional[Message] = None
        self.from_addr: Optional[str] = None
        self.passwd: Optional[str] = None
        self.subject: Optional[str] = None

    def connect(self) -> None:
        """
        连接到IMAP邮件服务器
        
        Raises:
            imaplib.IMAP4.error: 连接或登录失败时
        """
        try:
            # 连接到服务器
            self.mail = imaplib.IMAP4_SSL(self.imap_url)
            logger.info(f"Connected to IMAP server: {self.imap_url}")

            # 163邮箱需要特殊处理
            if self.imap_url == "imap.163.com":
                self._setup_163_imap()

            # 验证登录
            self.mail.login(self.username, self.password)
            logger.info(f"Successfully logged in as: {self.username}")

            # 选择收件箱
            result_sel, data_sel = self.mail.select("inbox")
            logger.info(f"Inbox selection status: {result_sel}, {data_sel}")
            
            if result_sel != 'OK':
                raise imaplib.IMAP4.error(f"Failed to select inbox: {data_sel}")
                
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            raise

    def _setup_163_imap(self) -> None:
        """设置163邮箱的特殊IMAP配置"""
        imaplib.Commands["ID"] = "NONAUTH"
        self.mail._simple_command("ID", '("name" "test" "version" "0.0.1")')
        logger.info("Applied 163.com IMAP configuration")

    def fetch_mail(self) -> None:
        """
        获取邮箱中的所有邮件列表
        
        Raises:
            imaplib.IMAP4.error: 搜索邮件失败时
        """
        if not self.mail:
            raise RuntimeError("Mail client not connected. Call connect() first.")
            
        try:
            result_search, data_search = self.mail.uid("search", None, "ALL")
            if result_search != 'OK':
                raise imaplib.IMAP4.error(f"Failed to search emails: {data_search}")
                
            self.email_list = data_search[0].split()
            logger.info(f"Found {len(self.email_list)} emails in inbox")
            
        except imaplib.IMAP4.error as e:
            logger.error(f"Error fetching emails: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching emails: {e}")
            raise

    def get_mail_info(self, num: bytes) -> None:
        """
        获取指定邮件的信息，包括发件人和主题
        
        Args:
            num: 邮件的UID
            
        Raises:
            imaplib.IMAP4.error: 获取邮件失败时
        """
        if not self.mail:
            raise RuntimeError("Mail client not connected. Call connect() first.")
            
        try:
            result, data = self.mail.uid("fetch", num, "(BODY.PEEK[])")
            if result != 'OK':
                raise imaplib.IMAP4.error(f"Failed to fetch email {num}: {data}")
                
            raw_email = data[0][1].decode("utf-8")
            self.email_message = email.message_from_string(raw_email)

            # 获取并解码发件人信息
            self.from_addr = self._decode_email_address(self.email_message["From"])
            
            # 获取并解码邮件主题
            self.subject = self._decode_email_subject(self.email_message["Subject"])
            
            logger.debug(f"Email from: {self.from_addr}, subject: {self.subject}")
            
        except (imaplib.IMAP4.error, UnicodeDecodeError) as e:
            logger.error(f"Error getting mail info for {num}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting mail info for {num}: {e}")
            raise

    def _decode_email_address(self, from_header: str) -> str:
        """解码邮件地址"""
        if not from_header:
            return ""
            
        from_header_parts = decode_header(from_header)
        decoded_header = "".join(
            part.decode(encoding if encoding else "utf-8") if isinstance(part, bytes) else part
            for part, encoding in from_header_parts
        )
        _, email_addr = parseaddr(decoded_header)
        return email_addr

    def _decode_email_subject(self, subject_header: str) -> str:
        """解码邮件主题"""
        if not subject_header:
            return ""
            
        subject_parts = decode_header(subject_header)
        return "".join(
            part.decode(encoding if encoding else "utf-8") if isinstance(part, bytes) else part
            for part, encoding in subject_parts
        )

    def get_passwd(self) -> bool:
        """
        从自己发送的邮件中提取解压密码
        
        Returns:
            bool: 是否成功获取密码
        """
        if not self.from_addr or not self.subject or not self.payment_platform:
            return False
            
        # 检查邮件发件邮箱是否是自己的邮箱
        if self.from_addr != self.username:
            return False
            
        logger.info(f"Checking password email from: {self.from_addr}")
        logger.info(f"Subject: {self.subject}")
        
        # 根据支付平台匹配密码模式
        pattern = SubjectPatterns.get_pattern_for_platform(self.payment_platform)
        if not pattern:
            logger.warning(f"No password pattern defined for platform: {self.payment_platform}")
            return False
            
        if re.match(pattern, self.subject):
            self.passwd = self.subject[-6:]  # 提取最后6位数字作为密码
            logger.info(f"Successfully extracted password: {self.passwd}")
            return True
            
        return False

    @staticmethod
    def walk_message(part: Message, count: int = 0) -> None:
        """
        递归遍历邮件消息，下载附件和处理HTML链接
        
        Args:
            part: 邮件消息部分
            count: 递归计数器
        """
        # 确保附件目录存在
        attachment_dir = Path(Directories.ATTACHMENT)
        attachment_dir.mkdir(exist_ok=True)

        logger.debug(f"Processing content type {count}: {part.get_content_type()}")
        
        # 处理附件
        filename = part.get_filename()
        if filename:
            MailClient._download_attachment(part, filename, attachment_dir)

        # 处理HTML内容中的下载链接（主要用于微信）
        if part.get_content_type() == ContentTypes.TEXT_HTML:
            MailClient._process_html_content(part, attachment_dir)

        # 递归处理多部分消息
        if part.is_multipart():
            for subpart in part.get_payload():
                count += 1
                MailClient.walk_message(subpart, count)

    @staticmethod
    def _download_attachment(part: Message, filename: str, attachment_dir: Path) -> None:
        """
        下载邮件附件
        
        Args:
            part: 邮件消息部分
            filename: 附件文件名
            attachment_dir: 附件保存目录
        """
        try:
            # 解码文件名
            decoded_filename = "".join(
                part.decode(encoding if encoding else "utf-8") if isinstance(part, bytes) else part
                for part, encoding in decode_header(filename)
            )
            logger.info(f"Downloading attachment: {decoded_filename}")

            # 获取附件内容并保存
            payload = part.get_payload(decode=True)
            if payload:
                file_path = attachment_dir / decoded_filename
                with open(file_path, "wb") as f:
                    f.write(payload)
                logger.info(f"Attachment saved to: {file_path}")
            else:
                logger.warning(f"No payload found for attachment: {decoded_filename}")
                
        except Exception as e:
            logger.error(f"Error downloading attachment {filename}: {e}")

    @staticmethod
    def _process_html_content(part: Message, attachment_dir: Path) -> None:
        """
        处理HTML内容，提取和下载链接文件
        
        Args:
            part: 邮件消息部分
            attachment_dir: 附件保存目录
        """
        try:
            html_content = part.get_payload(decode=True)
            if not html_content:
                return
                
            tree = html.fromstring(html_content, parser=html.HTMLParser(encoding="utf-8"))
            link_elements = tree.xpath('//a[contains(@href, "http")]')
            
            logger.info(f"Found {len(link_elements)} links in HTML content")
            
            for link in link_elements:
                url = link.get("href")
                if url and MailClient._is_valid_url(url):
                    MailClient._download_from_url(url, attachment_dir)
                    
        except Exception as e:
            logger.error(f"Error processing HTML content: {e}")

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """验证URL是否有效"""
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        return bool(re.match(url_pattern, url))

    @staticmethod
    def _download_from_url(url: str, attachment_dir: Path) -> None:
        """
        从URL下载文件
        
        Args:
            url: 下载链接
            attachment_dir: 保存目录
        """
        try:
            logger.info(f"Downloading from URL: {url}")
            response = requests.get(url, timeout=30)
            
            # 检查响应状态
            if response.status_code != 200:
                raise requests.RequestException(f"HTTP {response.status_code}")

            # 检查微信特定的错误消息
            error_message = "请在微信中重新申请导出"
            if error_message in response.text:
                raise Exception(f"File expired or download limit exceeded: {error_message}")

            # 获取文件名
            filename = MailClient._extract_filename_from_response(response, url)
            
            # 清理文件名中的无效字符
            safe_filename = re.sub(r'[\\/*?:"<>|]', "", filename)
            file_path = attachment_dir / safe_filename
            
            # 保存文件
            with open(file_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Downloaded file saved to: {file_path}")
            
        except requests.RequestException as e:
            logger.error(f"Request error downloading from {url}: {e}")
        except Exception as e:
            logger.error(f"Error downloading from {url}: {e}")

    @staticmethod
    def _extract_filename_from_response(response: requests.Response, url: str) -> str:
        """
        从HTTP响应中提取文件名
        
        Args:
            response: HTTP响应对象
            url: 原始URL
            
        Returns:
            str: 提取的文件名
        """
        if "Content-Disposition" in response.headers:
            try:
                filename_match = re.findall(
                    "filename=([^;]*)", response.headers["Content-Disposition"]
                )
                if filename_match:
                    filename = unquote(filename_match[0])  # 解码文件名
                    logger.debug(f"Extracted filename from headers: {filename}")
                    return filename
            except Exception as e:
                logger.warning(f"Error extracting filename from headers: {e}")
        
        # 如果无法从headers获取，使用URL的最后部分
        fallback_name = url.split("/")[-1][:20]  # 限制长度
        logger.debug(f"Using fallback filename: {fallback_name}")
        return fallback_name

    def fetch_mail_attachment(self) -> bool:
        """
        从指定支付平台的邮件中获取附件
        
        Returns:
            bool: 是否成功获取附件
        """
        if not self.payment_platform:
            logger.warning("No payment platform specified")
            return False
            
        if not self.from_addr:
            logger.warning("No sender address available")
            return False
            
        expected_sender = EmailSenders.get_sender_for_platform(self.payment_platform)
        if not expected_sender:
            logger.warning(f"Unknown payment platform: {self.payment_platform}")
            return False

        if self.from_addr == expected_sender:
            logger.info(f"Processing attachment from {self.payment_platform} platform")
            logger.info(f"Subject: {self.subject}")
            
            try:
                self.walk_message(self.email_message)
                logger.info("Successfully processed email attachments")
                return True
            except Exception as e:
                logger.error(f"Error processing email attachments: {e}")
                return False
        else:
            logger.debug(f"Email not from expected sender. Expected: {expected_sender}, Got: {self.from_addr}")
            return False

    def close(self) -> None:
        """关闭邮件连接"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
                logger.info("Mail connection closed")
            except Exception as e:
                logger.warning(f"Error closing mail connection: {e}")
            finally:
                self.mail = None

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


    @staticmethod
    def process_payment_platform_emails(payment_platform: str) -> Tuple[bool, Optional[str]]:
        """
        处理指定支付平台的邮件，获取密码和附件
        
        Args:
            payment_platform: 支付平台类型
            
        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 密码)
            
        Raises:
            ValueError: 当支付平台类型无效时
        """
        # 验证支付平台参数
        if not PaymentPlatform.is_valid_platform(payment_platform):
            raise ValueError(f"Unsupported payment platform: {payment_platform}. "
                           f"Supported platforms: {PaymentPlatform.get_all_platforms()}")
        
        try:
            username, password, imap_url = get_email_config()
            
            with MailClient(username, password, imap_url, payment_platform) as client:
                client.connect()
                client.fetch_mail()
                
                if not client.email_list:
                    logger.warning("No emails found in inbox")
                    return False, None
                
                # 首先查找密码邮件
                password_found = False
                for num in reversed(client.email_list):
                    client.get_mail_info(num)
                    if client.get_passwd():
                        logger.info("Successfully extracted password from email")
                        password_found = True
                        break
                
                if not password_found:
                    logger.warning("Password email not found. Please send password email first.")
                    return False, None
                
                # 然后查找并下载附件
                for num in reversed(client.email_list):
                    client.get_mail_info(num)
                    if client.fetch_mail_attachment():
                        logger.info("Successfully downloaded attachments")
                        return True, client.passwd
                        
                logger.warning("No attachments found from payment platform emails")
                return False, client.passwd
                
        except Exception as e:
            logger.error(f"Error processing {payment_platform} emails: {e}")
            return False, None


def main() -> None:
    """主函数，演示邮件客户端的使用"""
    try:
        # 示例：处理支付宝邮件
        success, password = MailClient.process_payment_platform_emails(PaymentPlatform.ALIPAY)

        if success:
            logger.info(f"Successfully processed emails. Password: {password}")
        else:
            logger.error("Failed to process emails")
            
    except Exception as e:
        logger.error(f"Main function error: {e}")


if __name__ == "__main__":
    main()
