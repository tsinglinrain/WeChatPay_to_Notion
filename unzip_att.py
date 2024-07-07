import os
import zipfile
from datetime import datetime


class FileExtractor:
    def __init__(
        self,
        path_attachment_file,
        path_target_folder,
        attachment_password,
        payment_platform,
    ):
        self.attachment_path = path_attachment_file
        self.target_folder_path = path_target_folder
        self.attachment_password = attachment_password
        self.payment_platform = payment_platform

    def search_files(self):
        text_start = {"alipay": "交易流水证明", "wechatpay": "微信支付账单"}
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
        return zip_files

    @staticmethod
    def extract_date_from_filename(filename):
        """备用"""
        date_str = filename.split("_")[
            2
        ]  # Assumes filename format is 'alipay_record_YYYYMMDD_HHMMSS.csv'
        # print(date_str)
        return datetime.strptime(date_str, "%Y%m%d")

    def unzip_earliest_file(self, files):
        if not files:
            return "No zip files found in directory."

        # latest_file = max(zip_files, key=self.extract_date_from_filename)
        latest_file = max(
            files, key=lambda f: os.path.getmtime(os.path.join(self.attachment_path, f))
        )
        with zipfile.ZipFile(
            os.path.join(self.attachment_path, latest_file), "r"
        ) as zip_ref:
            zip_ref.extractall(
                self.target_folder_path,
                pwd=self.attachment_password and self.attachment_password.encode(),
            )
        return f"Extracted {latest_file} to {self.target_folder_path}."


def main():
    path_att = "./attachment"
    path_target = "./bill_csv_raw"

    payment_platform = "alipay"
    # password = "473396" # wechatpay
    password = "749350"  # alipay
    extractor = FileExtractor(path_att, path_target, password, payment_platform)
    files = extractor.search_files()
    msg = extractor.unzip_earliest_file(files)
    print(msg)


if __name__ == "__main__":
    main()
