"""
文件移动模块

该模块提供了文件移动和复制功能，用于将解压后的账单文件移动到指定位置。
支持微信支付和支付宝的账单文件处理。
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict
import pandas as pd
from src.core.log_core.logging_config import get_logger

# 获取当前模块的日志器
logger = get_logger(__name__)


class FileMover:
    """文件移动器类，用于处理账单文件的移动和重命名"""
    
    def __init__(self, source_dir: str, target_dir: str, payment_platform: str) -> None:
        """
        初始化文件移动器
        
        Args:
            source_dir: 源目录
            target_dir: 目标目录
            payment_platform: 支付平台类型
        """
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.payment_platform = payment_platform
        
        # 确保目标目录存在
        Path(self.target_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"FileMover initialized for platform: {payment_platform}")

    def find_latest_file(self) -> str:
        """
        查找最新的账单文件
        
        Returns:
            str: 最新文件的路径，如果没有找到则返回空字符串
        """
        latest_file = ""
        latest_time = 0
        name_patterns = {"alipay": "支付宝交易明细", "wechatpay": "微信支付账单"}
        
        pattern = name_patterns.get(self.payment_platform)
        if not pattern:
            logger.error(f"Unknown payment platform: {self.payment_platform}")
            return ""
        
        if not os.path.exists(self.source_dir):
            logger.warning(f"Source directory does not exist: {self.source_dir}")
            return ""
        
        try:
            for foldername, subfolders, filenames in os.walk(self.source_dir):
                for filename in filenames:
                    if filename.startswith(pattern):
                        file_path = os.path.join(foldername, filename)
                        file_time = os.path.getmtime(file_path)
                        if file_time > latest_time:
                            latest_time = file_time
                            latest_file = file_path
                            
            if latest_file:
                logger.info(f"Found latest file: {latest_file}")
            else:
                logger.warning(f"No files found matching pattern: {pattern}")
                
            return latest_file
            
        except Exception as e:
            logger.error(f"Error finding latest file: {e}")
            return ""

    def copy_file(self) -> None:
        """
        复制和重命名文件到目标目录
        """
        file_name_mapping = {"alipay": "alipay_raw", "wechatpay": "wechatpay_raw"}
        source_file = self.find_latest_file()
        
        if not source_file:
            logger.warning("No file found to copy.")
            return
            
        try:
            logger.info(f"Processing file: {source_file}")
            
            if self.payment_platform == "wechatpay":
                # 微信账单需要转换为csv
                self._excel_to_csv(source_file)
            else:
                # 支付宝账单直接复制
                self._copy_and_rename_file(source_file, file_name_mapping[self.payment_platform])
                
        except Exception as e:
            logger.error(f"Error copying file: {e}")

    def _copy_and_rename_file(self, source_file: str, new_name: str) -> None:
        """
        复制文件并重命名
        
        Args:
            source_file: 源文件路径
            new_name: 新文件名（不含扩展名）
        """
        try:
            # 复制文件到目标目录
            shutil.copy2(source_file, self.target_dir)
            logger.info(f"File copied to: {self.target_dir}")
            
            # 获取文件扩展名并创建新的文件路径
            extension = os.path.splitext(source_file)[1]
            new_file_path = os.path.join(self.target_dir, new_name + extension)
            old_file_path = os.path.join(self.target_dir, os.path.basename(source_file))
            
            # 如果目标文件已存在，先删除它
            if os.path.exists(new_file_path):
                os.remove(new_file_path)
                logger.debug(f"Removed existing file: {new_file_path}")
            
            # 重命名文件
            os.rename(old_file_path, new_file_path)
            logger.info(f"File renamed to: {new_file_path}")
            
        except Exception as e:
            logger.error(f"Error copying and renaming file: {e}")
            raise

    def _excel_to_csv(self, source_file: str) -> None:
        """
        将Excel文件转换为CSV文件（专门处理微信账单）
        
        Args:
            source_file: 源Excel文件路径
        """
        if self.payment_platform != "wechatpay":
            logger.error("This method is only for WeChat Pay bills.")
            return
            
        try:
            logger.info(f"Converting Excel to CSV: {source_file}")
            df = pd.read_excel(source_file)
            
            csv_path = os.path.join(self.target_dir, "wechatpay_raw.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8')
            logger.info(f"Successfully converted {source_file} to {csv_path}")
            
        except Exception as e:
            logger.error(f"Error converting Excel to CSV: {e}")
            raise


def main() -> None:
    """主函数，用于测试文件移动功能"""
    csv_csv_path = "bill_csv_raw"
    target_path = "./"
    
    # 测试微信支付
    logger.info("Testing WeChat Pay file processing...")
    mover = FileMover(csv_csv_path, target_path, "wechatpay")
    mover.copy_file()
    
    # 测试支付宝
    logger.info("Testing Alipay file processing...")
    mover_alipay = FileMover(csv_csv_path, target_path, "alipay")
    mover_alipay.copy_file()


if __name__ == "__main__":
    main()
