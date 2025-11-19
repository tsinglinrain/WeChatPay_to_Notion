# 另外因为是导出账单，可能出现日期与上次导入Notion有重复的情况，
# 这里可以在 alipay_raw.csv 中直接删除某一些日期。当然你也可以用程序进行筛选

import re
from pathlib import Path
from src.adapters.base import PaymentAdapter
from src.utils.logger import get_logger


class CsvTransformer:
    def __init__(self, adapter: PaymentAdapter, path_raw: str | Path, path_std: str | Path):
        self.adapter = adapter
        self.path_raw = Path(path_raw)
        self.path_std = Path(path_std)
        self.encoding = adapter.get_csv_encoding()
        self.logger = get_logger()

    def transform_to_standard_csv(self):
        """读取原始文件，截取并得到新的文件"""

        with open(self.path_raw, encoding=self.encoding, newline="") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("交易时间"):
                    with open(
                        self.path_std, "w", encoding="utf-8", newline=""
                    ) as f2:  # encoding="utf-8"为便于读写
                        # 将该行之后的所有行写入新文件并且用re删除每一行中的空格
                        f2.writelines(
                            re.sub(r"\s+,", ",", line)
                            for line in lines[lines.index(line) :]
                        )

        self.logger.info(
            f"Transformed CSV to standard format: {self.path_std}"
        )


