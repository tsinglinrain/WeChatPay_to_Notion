import csv
import yaml

from get_new_csv import *
from get_need_data import *
from post_preparation import *
from notion_property import *

# 基本信息
with open("config_private.yaml", "r", encoding="utf-8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
database_id = config["database_id"]
token = config["token"]
path_raw = "wechat_raw.csv"
path_new_1 = "wechat_new1.csv"
path_new_2 = "wechat_new2.csv"

def send_notion(path):
    """读取data_new.csv文件
    
    Args:
        path (str): csv文件路径
        
    Returns:
        row: 返回每一行     
    """

    with open(path, encoding="utf-8", newline="") as f:
        csvreader = csv.reader(f)   # 读取csv文件,返回的是一个迭代器,每一行是一个列表
        for row in csvreader:
            properties = notion_property(row[3], float(row[5]), row[1], row[0]) # 注意str
            response = post_notion(properties, database_id, token)
            response_result(response)

def main():
    get_new_data(path_raw, path_new_1)
    get_need_data(path_new_1, path_new_2)
    send_notion(path_new_2)  

if __name__ == "__main__":
    main()
