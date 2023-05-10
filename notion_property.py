# 用于notion property的自定义
# 如果自己想改就可以在这里修改
    # 需要保证与Notion Database中的property一致

def notion_property(content, price, category, date, remarks=""):
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
        
    }
    return properties