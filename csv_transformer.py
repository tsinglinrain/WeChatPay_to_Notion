
# 另外因为是导出账单，可能出现日期与上次导入Notion有重复的情况，
    # 这里可以在 alipay_raw.csv 中直接删除某一些日期。当然你也可以用程序进行筛选

import re

class CsvTransformer:
    def __init__(self, payment_platform):

        self.path_raw = f"{payment_platform}_raw.csv"
        self.path_std = f"{payment_platform}_standard.csv"
        encoding_dict = {"alipay": "gbk", "wechatpay": "utf-8"}
        self.encoding = encoding_dict[payment_platform]

    def transform_to_standard_csv(self):
        '''读取原始文件，截取并得到新的文件'''

        with open(self.path_raw, encoding=self.encoding, newline="") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("交易时间"):
                    with open(self.path_std, "w", encoding="utf-8", newline="") as f2: # encoding="utf-8"为便于读写
                        # 将该行之后的所有行写入新文件并且用re删除每一行中的空格
                        f2.writelines(re.sub(r"\s+,", ",", line) for line in lines[lines.index(line):])

        print(f"The original csv file has been changed to a standard csv file: {self.path_std}")

def main():
    # 全部统一,alipay,wechatpay
    csvp_alipay = CsvTransformer("alipay")
    csvp_alipay.transform_to_standard_csv()

    # csv_wechat = CsvTransformer("wechatpay")
    # csv_wechat.transform_to_standard_csv()

if __name__ == "__main__":
    main()





