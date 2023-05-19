import csv
import yaml

from get_standard_csv import *
from get_need_data import *
from post_preparation import *
from notion_property import *

def main():
    # 基本信息
    with open("config_private.yaml", "r", encoding="utf-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    database_id = config["database_id"]
    token = config["token"]

    path_raw = "wechat_raw.csv"
    path_st = "wechat_standard.csv"

    get_standard_csv(path_raw, path_st)

    df =get_need_data(path_st)
    content = df["商品"][0]
    price = df["金额(元)"][0]
    category =  df["交易类型"][0]
    date = df["交易时间"][0]
    
    properties = notion_property(content, price, category, date)    # price必须是float类型
    response = post_notion(properties, database_id, token)
    response_result(response)

if __name__ == "__main__":
    main()
