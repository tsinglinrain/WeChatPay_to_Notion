import os
import shutil


class FileMover:
    def __init__(self, source_dir, target_dir, payment_platform):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.payment_platform = payment_platform

    def find_latest_file(self):
        latest_file = ""
        latest_time = 0
        name = {"alipay": "alipay_record", "wechatpay": "微信支付账单"}
        for foldername, subfolders, filenames in os.walk(self.source_dir):
            for filename in filenames:
                if filename.startswith(name[self.payment_platform]):
                    file_path = os.path.join(foldername, filename)
                    file_time = os.path.getmtime(file_path)
                    if file_time > latest_time:
                        latest_time = file_time
                        latest_file = file_path
        return latest_file

    def copy_file(self):
        name = {"alipay": "alipay_raw", "wechatpay": "wechatpay_raw"}
        source_file = self.find_latest_file()
        if source_file:
            shutil.copy2(source_file, self.target_dir)
            extension = os.path.splitext(source_file)[1]  # 获取源文件的扩展名
            # 创建新的文件路径
            new_file_path = os.path.join(
                self.target_dir, name[self.payment_platform] + extension
            )
            # 如果目标文件已存在，先删除它
            if os.path.exists(new_file_path):
                os.remove(new_file_path)
            # 重命名文件
            os.rename(
                os.path.join(self.target_dir, os.path.basename(source_file)),
                new_file_path,
            )
        else:
            print("No file found to copy.")


def main():
    csv_csv_path = "bill_csv_raw"
    target_path = "./"
    name = {"alipay": "alipay_raw", "wechatpay": "wechatpay_raw"}
    mover = FileMover(csv_csv_path, target_path, "wechatpay")
    mover.copy_file()


if __name__ == "__main__":
    main()
