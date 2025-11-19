import shutil
import pandas as pd
from pathlib import Path
from src.config.constants import RAW_FILENAME_PREFIX
from src.adapters.base import PaymentAdapter
from src.utils.logger import get_logger

class FileMover:
    def __init__(self, source_dir, target_dir, adapter: PaymentAdapter):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.adapter = adapter
        self.logger = get_logger()

    def find_latest_file(self):
        base_dir = Path(self.source_dir)
        files = [
            f for f in base_dir.glob("*")
            if f.is_file() and f.name.startswith(self.adapter.get_bill_file_prefix())
        ]
        if not files:
            return ""
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        return str(latest_file)

    def copy_file(self):
        source_file = Path(self.find_latest_file())
        
        if not source_file.exists():
            self.logger.warning("No file found to copy")
            return
        
        # 处理需要Excel转CSV的情况（如微信支付）
        if self.adapter.needs_excel_conversion():
            self.excel_to_csv()
            return

        target_dir = Path(self.target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)  # 确保目标目录存在

        new_file_path = target_dir / f"{RAW_FILENAME_PREFIX[self.adapter.platform_name]}{source_file.suffix}"

        # 复制并覆盖旧文件
        shutil.copy2(source_file, new_file_path)
        self.logger.info(f"Copied and renamed to: {new_file_path}")

    def excel_to_csv(self):
        """处理需要从Excel转换为CSV的账单（如微信支付）"""

        source_file = self.find_latest_file()
        if source_file:
            df = pd.read_excel(source_file)
            csv_path = Path(self.target_dir) / (RAW_FILENAME_PREFIX[self.adapter.platform_name] + ".csv")
            df.to_csv(csv_path, index=False)
            self.logger.info(f"Converted {source_file} to {csv_path}")
        else:
            self.logger.warning("No file found to convert")


