# 进一步分析数据
# 这里自定义程度比较高,可以根据自己的需求进行修改
# 比如我只想要支出，那么我就通过布尔取值，只要支出的数据

# 进一步整理数据
# 这里面的日期必须修改
# 这里面的价格必须修改
# 其他可自行修改

# 这是我示例的一个数据处理过程

import pandas as pd


class DataProcessor:
    def __init__(self, path, platform):
        self.path = path
        self.platform = platform
        self.df = pd.read_csv(self.path, encoding="utf-8")

    def process_mandatory_fields(self):
        self.df["交易时间"] = self.df["交易时间"].map(
            lambda x: "".join([x[:10], "T", x[11:], "Z"])
        )  # ISO 8601
        if self.platform == "alipay":
            self.df["金额"] = self.df["金额"].map(lambda x: float(x))
            # self.df["备注"] = self.df["备注"].fillna("")
            # self.df["商家订单号"] = self.df["商家订单号"].fillna("")
            self.df = self.df.fillna("")
        elif self.platform == "wechatpay":
            self.df = self.df.fillna("")
            self.df["金额(元)"] = self.df["金额(元)"].map(lambda x: float(x[1:]))
            # self.df["金额(元)"] = self.df["金额(元)"].map(lambda x: float(x[1:]) if isinstance(x, str) else x)
            self.df["备注"] = self.df["备注"].map(lambda x: "" if x == "/" else x)

    def filter_rows(self, column, values_to_exclude):
        for value in values_to_exclude:
            self.df = self.df[self.df[column] != value]

    def drop_columns(self, columns_to_drop):
        self.df.drop(columns_to_drop, axis=1, inplace=True)

    def custom_drop(self, column, value):
        pass

    def get_processed_data(self):
        pass
        return self.df


