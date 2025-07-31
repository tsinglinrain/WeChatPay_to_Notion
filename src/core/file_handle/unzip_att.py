"""
文件解压模块

该模块提供了文件解压功能，专门用于处理微信支付和支付宝的账单压缩包。
支持密码保护的ZIP文件解压。
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
import zipfile
import pyzipper
from log_core.logging_config import get_logger

# 获取当前模块的日志器
logger = get_logger(__name__)


class FileExtractor:
    """文件解压器类，专门处理支付平台的账单压缩包"""
    
    def __init__(
        self,
        path_attachment_file: str,
        path_target_folder: str,
        attachment_password: str,
        payment_platform: str,
    ) -> None:
        """
        初始化文件解压器
        
        Args:
            path_attachment_file: 附件文件路径
            path_target_folder: 目标文件夹路径
            attachment_password: 解压密码
            payment_platform: 支付平台类型
        """
        self.attachment_path = path_attachment_file
        self.target_folder_path = path_target_folder
        self.attachment_password = attachment_password
        self.payment_platform = payment_platform
        
        # 确保目标目录存在
        Path(self.target_folder_path).mkdir(parents=True, exist_ok=True)
        logger.debug(f"FileExtractor initialized for platform: {payment_platform}")

    def search_files(self) -> List[str]:
        """
        搜索指定支付平台的压缩文件
        
        Returns:
            List[str]: 找到的压缩文件列表
        """
        text_start = {"alipay": "支付宝交易明细", "wechatpay": "微信支付账单"}
        
        if not os.path.exists(self.attachment_path):
            logger.warning(f"Attachment path does not exist: {self.attachment_path}")
            return []
        
        try:
            files = [
                f
                for f in os.listdir(self.attachment_path)
                if os.path.isfile(os.path.join(self.attachment_path, f))
            ]
            
            zip_files = [
                f
                for f in files
                if f.endswith(".zip") and f.startswith(text_start[self.payment_platform])
            ]
            
            logger.info(f"Found {len(zip_files)} zip files for {self.payment_platform}: {zip_files}")
            return zip_files
            
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return []

    @staticmethod
    def extract_date_from_filename(filename: str) -> Optional[datetime]:
        """
        从文件名中提取日期（备用方法）
        
        Args:
            filename: 文件名
            
        Returns:
            Optional[datetime]: 提取的日期，失败时返回None
        """
        try:
            # 假设文件名格式为 'alipay_record_YYYYMMDD_HHMMSS.csv'
            date_str = filename.split("_")[2]
            logger.debug(f"Extracted date string from filename: {date_str}")
            return datetime.strptime(date_str, "%Y%m%d")
        except (IndexError, ValueError) as e:
            logger.warning(f"Failed to extract date from filename {filename}: {e}")
            return None

    def check_zip_compatibility(self, zip_path: str) -> Tuple[bool, str]:
        """
        检查ZIP文件的兼容性
        
        Args:
            zip_path: ZIP文件路径
            
        Returns:
            Tuple[bool, str]: (是否兼容, 解压方法)
        """
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # 检查所有文件的压缩方法
                for info in zip_ref.infolist():
                    if info.compress_type not in [0, 8]:  # ZIP_STORED, ZIP_DEFLATED
                        logger.debug(f"Unsupported compression method: {info.compress_type}")
                        return False, f"不支持的压缩方法: {info.compress_type}"
                logger.debug(f"ZIP file {zip_path} is compatible with standard zipfile")
                return True, "兼容"
        except Exception as e:
            logger.debug(f"ZIP compatibility check failed: {e}")
            return False, str(e)

    def extract_with_zipfile(self, zip_path: str, file_name: str) -> Tuple[bool, str]:
        """
        使用标准zipfile解压
        
        Args:
            zip_path: ZIP文件路径
            file_name: 文件名
            
        Returns:
            Tuple[bool, str]: (是否成功, 结果消息)
        """
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(
                    self.target_folder_path,
                    pwd=(
                        self.attachment_password.encode()
                        if self.attachment_password
                        else None
                    ),
                )
            message = f"Successfully extracted {file_name} using zipfile"
            logger.info(message)
            return True, message
        except Exception as e:
            message = f"zipfile extraction failed: {e}"
            logger.error(message)
            return False, message

    def extract_with_pyzipper(self, zip_path: str, file_name: str) -> Tuple[bool, str]:
        """
        使用pyzipper解压不兼容的ZIP文件
        
        Args:
            zip_path: ZIP文件路径
            file_name: 文件名
            
        Returns:
            Tuple[bool, str]: (是否成功, 结果消息)
        """
        try:
            with pyzipper.AESZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(
                    self.target_folder_path,
                    pwd=(
                        self.attachment_password.encode()
                        if self.attachment_password
                        else None
                    ),
                )
            message = f"Successfully extracted {file_name} using pyzipper (AES)"
            logger.info(message)
            return True, message
        except Exception as e:
            logger.warning(f"AES extraction failed: {e}, trying standard pyzipper")
            # 如果AES失败，尝试传统ZIP
            try:
                with pyzipper.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(
                        self.target_folder_path,
                        pwd=(
                            self.attachment_password.encode()
                            if self.attachment_password
                            else None
                        ),
                    )
                message = f"Successfully extracted {file_name} using pyzipper"
                logger.info(message)
                return True, message
            except Exception as e2:
                message = f"pyzipper extraction failed: AES error: {e}, Standard error: {e2}"
                logger.error(message)
                return False, message

    def unzip_earliest_file(self, files: List[str]) -> str:
        """
        解压最新的ZIP文件
        
        Args:
            files: ZIP文件列表
            
        Returns:
            str: 解压结果消息
        """
        if not files:
            message = "No zip files found in directory."
            logger.warning(message)
            return message

        # 按修改时间排序文件（最新的在前）
        try:
            sorted_files = sorted(
                files,
                key=lambda f: os.path.getmtime(os.path.join(self.attachment_path, f)),
                reverse=True,
            )
            earliest_file = sorted_files[0]
            zip_path = os.path.join(self.attachment_path, earliest_file)
            logger.info(f"Processing latest file: {earliest_file}")

            # 尝试用标准zipfile解压
            success, message = self.extract_with_zipfile(zip_path, earliest_file)
            if success:
                return message
            else:
                logger.warning(f"Standard zipfile extraction failed: {message}")

            # 如果标准zipfile失败，尝试pyzipper
            success, message = self.extract_with_pyzipper(zip_path, earliest_file)
            if success:
                return message
            else:
                logger.error(f"pyzipper extraction also failed: {message}")
                return message
                
        except Exception as e:
            error_message = f"Error during file extraction: {e}"
            logger.error(error_message)
            return error_message
            print(f"zipfile解压失败: {message}")

        # 如果标准zipfile失败，尝试pyzipper
        success, message = self.extract_with_pyzipper(zip_path, earliest_file)
        if success:
            return message
        else:
            logger.error(f"pyzipper extraction also failed: {message}")

        return "No zip files could be extracted with any method."


def main() -> None:
    """主函数，用于测试文件解压功能"""
    path_att = "./attachment"
    path_target = "./bill_csv_raw"

    payment_platform = "wechatpay"
    # password = "473396"  # alipay
    password = "047409"  # wechatpay
    extractor = FileExtractor(path_att, path_target, password, payment_platform)
    files = extractor.search_files()
    logger.info(f"Found files: {files}")
    
    if files:
        msg = extractor.unzip_earliest_file(files)
        logger.info(f"Extraction result: {msg}")
    else:
        logger.warning("No files found to extract")


if __name__ == "__main__":
    main()
