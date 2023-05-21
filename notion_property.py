# 用于notion property的自定义
# 如果自己想改就可以在这里修改
    # 需要保证与Notion Database中的property一致

def notion_property(content, price, category, date, counterparty, remarks, 
                    transaction_number="",
                    merchant_tracking_number="",
                    payment_method="undefined"):
    """将输入的内容转换为notion的json格式
    Args:
        content (str): 商品名称
        price (float): 价格
        category (str): 交易类型
        date (str): 交易时间
        Counterparty (str): 交易对方
        remarks (str): 备注
        transaction_number (str, optional): 交易单号. Defaults to ""
        merchant_tracking_number (str, optional): 商户单号. Defaults to ""
        payment_method (str, optional): 支付方式. Defaults to ""
    Returns:
        properties: 返回notion的json格式
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
        "Counterparty": {
            "rich_text": [
            {
                "text": {
                    "content": counterparty
                }
            }]
        },
        "Remarks": {
            "rich_text": [
            {
                "text": {
                    "content": remarks
                }
            }]
        },
        "Transaction Number": {
            "rich_text": [
            {
                "text": {
                    "content": transaction_number
                }
            }]
        },
        "Merchant Tracking Number": {
            "rich_text": [
            {
                "text": {
                    "content": merchant_tracking_number
                }
            }]
        },
        "Payment Method": {
            "select": {
                "name": payment_method
            }
        },
    }
    return properties