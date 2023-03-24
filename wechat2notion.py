import requests
import csv
import re

# 基本信息
database_id = ""    # 数据库ID, 要填进去哦
token = "secret_" # token, 记得自己填写
raw_path = "wechat_raw.csv"
new_path1 = "wechat_new1.csv"
new_path2 = "wechat_new2.csv"

def get_new_data(raw_path):
    """读取原始文件，截取并得到新的文件
    
    Args:
        raw_path (str): 原始文件路径

    Returns:
       new_path (str): 新的文件路径
    """

    with open(raw_path, encoding="utf-8", newline="") as f: # 注意这里的路径
        lines = f.readlines()   # 读取所有行
        for line in lines:  # 遍历每一行
            if line.startswith("----------------------微信"):   # 找到以"----------------------微信"开头的行
                # 将该行之后的所有行按照每一行写入新文件并且用re删除每一行中的空格
                with open(new_path1, "a", encoding="utf-8", newline="") as f2:
                    f2.writelines(re.sub(r"\s+,", ",", line) for line in lines[lines.index(line) + 1:])

def get_new_data2(new_path1, new_path2):
    """读取新的文件，得到最终的文件

    Args:
        new_path1 (str): 新的文件路径1
        new_path2 (str): 新的文件路径2
    """

    with open(new_path1, encoding="utf-8", newline="") as f:
            # 将每一列的数据读取到一个列表中
            csvreader = csv.reader(f)   # 读取csv文件,返回的是一个迭代器,每一行是一个列表
            for row in csvreader: # 打印测试一下
                if row[4] == "支出":  # 原来是因为有空格, 找了半天bug, 应当第一步就把空格删去
                    print(row[4], row[6], row[1], row[0])
                    with open(new_path2, "a", encoding="utf-8", newline="") as f:
                        csvwriter = csv.writer(f)
                        csvwriter.writerow(row)
                    # print("**")
                # print(row[0])

def in2notion(content, price, category, date, remarks=""):
    """将输入的内容转换为notion的格式
    
    Args:
        content (str): 名称
        price (float): 价格
        category (str): 类别
        date (str): 日期

    Returns:
        properties: 返回notion的格式
    """

    properties = {
        "Name": {
            "title": [
            {
                "text": {
                    "content": content
                }
            }  
            ]
        },
        "Price": {
            "number": price
        },
        "Category": {
            "select": {
                "name": category
            }
        },
        "Date": {
            "date": {
                "start": date,
                "time_zone": "Asia/Shanghai"    # 时区, 参见官方文档
            }
        },
        "From": {
            "select": {
                "name": "Wechat"
            }
        },
        "Remarks": {
            "rich_text": [
            {
                "text": {
                    "content": remarks
                }
            }
        ]
        }
    }
    return properties

# post请求
def post_notion(properties):
    """post请求
    
    Args:
        properties: 需要post的内容
        
    Returns:
        response: 返回response
    """

    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": database_id},
        "properties": properties,
        #"children": ["string"],    # 不需要children
        #"icon": "string",
        #"cover": "string"
    }
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28", # 版本号
        "content-type": "application/json",
        "Authorization": "".join(["Bearer", " ", token]) # 注意空格, 之前没注意空格, 一直报错
    }
    response = requests.post(url, json=payload, headers=headers)
    return response

def result(response):
    """判断是否成功

    Args:
        response: 返回的response
    """

    if response.status_code == 200:
        print("成功...")
    else:
        print("失败...")
        print(response.text)

def get_data_col(new_path3):
    """读取data_new.csv文件
    
    Args:
        new_path3 (str): csv文件路径
        
    Returns:
        row: 返回每一行       
    """
    with open(new_path2, encoding="utf-8", newline="") as f:
        csvreader = csv.reader(f)   # 读取csv文件,返回的是一个迭代器,每一行是一个列表
        for row in csvreader:
            row_5 = float(row[5][1:]) # 价格需要转换为浮点数, 并且去掉前面的￥符号
            row_0 = "".join([row[0][:10], "T", row[0][11:], "Z"])  # 日期需要转换ISO 8601 format date
            if row[3].startswith("KFC"):# 如果row[3]以KFC开头, 则将row[3]的值改为KFC，并且写入remarks, 否则不写入remarks
                row_3 = "KFC"
                properties = in2notion(row_3, row_5, row[1], row_0, remarks=row[3])
            else:
                properties = in2notion(row[3], row_5, row[1], row_0, remarks="")
            response = post_notion(properties)
            result(response)

# 主函数
def main():
    get_new_data(raw_path)
    get_new_data2(new_path1, new_path2)
    get_data_col(new_path2)

if __name__ == "__main__":
    main()
