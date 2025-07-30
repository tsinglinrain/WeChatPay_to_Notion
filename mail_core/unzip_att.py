import os
from datetime import datetime
import zipfile
import pyzipper


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
        text_start = {"alipay": "支付宝交易明细", "wechatpay": "微信支付账单"}
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

    def check_zip_compatibility(self, zip_path):
        """检查ZIP文件是否可以用标准zipfile模块处理"""
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # 检查所有文件的压缩方法
                for info in zip_ref.infolist():
                    if info.compress_type not in [0, 8]:  # ZIP_STORED, ZIP_DEFLATED
                        return False, f"不支持的压缩方法: {info.compress_type}"
                return True, "兼容"
        except Exception as e:
            return False, str(e)

    def extract_with_zipfile(self, zip_path, file_name):
        """使用标准zipfile解压"""
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
            return True, f"Successfully extracted {file_name} using zipfile"
        except Exception as e:
            return False, f"zipfile extraction failed: {e}"

    def extract_with_pyzipper(self, zip_path, file_name):
        """使用pyzipper解压不兼容的ZIP文件"""
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
            return True, f"Successfully extracted {file_name} using pyzipper (AES)"
        except Exception as e:
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
                return True, f"Successfully extracted {file_name} using pyzipper"
            except Exception as e2:
                return (
                    False,
                    f"pyzipper extraction failed: AES error: {e}, Standard error: {e2}",
                )

    def unzip_earliest_file(self, files):
        if not files:
            return "No zip files found in directory."

        # 按修改时间排序文件（最新的在前）
        sorted_files = sorted(
            files,
            key=lambda f: os.path.getmtime(os.path.join(self.attachment_path, f)),
            reverse=True,
        )
        earliest_file = sorted_files[0]
        zip_path = os.path.join(self.attachment_path, earliest_file)

        # 尝试用标准zipfile解压
        success, message = self.extract_with_zipfile(zip_path, earliest_file)
        if success:
            return message
        else:
            print(f"zipfile解压失败: {message}")

        # 如果标准zipfile失败，尝试pyzipper
        success, message = self.extract_with_pyzipper(zip_path, earliest_file)
        if success:
            return message
        else:
            print(f"pyzipper解压失败: {message}")

        return "No zip files could be extracted with any method."


def main():
    path_att = "./attachment"
    path_target = "./bill_csv_raw"

    payment_platform = "wechatpay"
    # password = "473396"  # alipay
    password = "047409"  # wechatpay
    extractor = FileExtractor(path_att, path_target, password, payment_platform)
    files = extractor.search_files()
    print(files)
    msg = extractor.unzip_earliest_file(files)
    print(msg)


if __name__ == "__main__":
    main()
