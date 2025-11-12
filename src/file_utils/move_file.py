import shutil
import pandas as pd
from pathlib import Path

class FileMover:
    def __init__(self, source_dir, target_dir, payment_platform):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.payment_platform = payment_platform

    def find_latest_file(self):
        name = {"alipay": "支付宝交易明细", "wechatpay": "微信支付账单"}
        base_dir = Path(self.source_dir)
        files = [
            f for f in base_dir.glob("*")
            if f.is_file() and f.name.startswith(name[self.payment_platform])
        ]
        if not files:
            return ""
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        return str(latest_file)

    def copy_file(self):
        name = {"alipay": "alipay_raw", "wechatpay": "wechatpay_raw"}
        source_file = Path(self.find_latest_file())
        
        if not source_file.exists():
            print("No file found to copy.")
            return
        
        # 处理微信支付的特殊情况
        if self.payment_platform == "wechatpay":
            self.excel_to_csv()
            return

        target_dir = Path(self.target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)  # 确保目标目录存在

        new_file_path = target_dir / f"{name[self.payment_platform]}{source_file.suffix}"

        # 复制并覆盖旧文件
        shutil.copy2(source_file, new_file_path)
        print(f"Copied and renamed to: {new_file_path}")

    def excel_to_csv(self):
        """专门处理微信账单的excel转csv"""
        if self.payment_platform != "wechatpay":
            print("This method is only for WeChat Pay bills.")
            return
        
        name = {"alipay": "alipay_raw", "wechatpay": "wechatpay_raw"}
        source_file = self.find_latest_file()
        if source_file:
            df = pd.read_excel(source_file)
            csv_path = Path(self.target_dir) / (name[self.payment_platform] + ".csv")
            df.to_csv(csv_path, index=False)
            print(f"Converted {source_file} to {csv_path}")
        else:
            print("No file found to convert.")


