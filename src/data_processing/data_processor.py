# 进一步分析数据
# 这里自定义程度比较高,可以根据自己的需求进行修改
# 比如我只想要支出，那么我就通过布尔取值，只要支出的数据

# 进一步整理数据
# 这里面的日期必须修改
# 这里面的价格必须修改
# 其他可自行修改

# 这是我示例的一个数据处理过程

import pandas as pd
from src.adapters.base import PaymentAdapter


class DataProcessor:
    def __init__(self, path, adapter: PaymentAdapter):
        self.path = path
        self.adapter = adapter
        self.df = pd.read_csv(self.path, encoding="utf-8")

    def process_mandatory_fields(self):
        self.df["交易时间"] = self.df["交易时间"].map(
            lambda x: "".join([x[:10], "T", x[11:], "Z"])
        )  # ISO 8601
        
        # Use adapter to get column mapping
        col_map = self.adapter.get_csv_column_mapping()
        amount_col = col_map['amount']
        remarks_col = col_map['remarks']
        
        # Process amount using adapter
        self.df[amount_col] = self.df[amount_col].map(self.adapter.process_amount)
        
        # Fill NaN values
        self.df = self.df.fillna("")
        
        # Process remarks using adapter
        self.df[remarks_col] = self.df[remarks_col].map(self.adapter.process_remarks)

    def filter_rows(self, column, values_to_exclude):
        for value in values_to_exclude:
            self.df = self.df[self.df[column] != value]

    def drop_columns(self, columns_to_drop):
        self.df.drop(columns_to_drop, axis=1, inplace=True)

    def custom_drop(self, column, value):
        """Custom drop logic - to be implemented based on specific requirements."""  
        pass

    def get_processed_data(self):
        return self.df


