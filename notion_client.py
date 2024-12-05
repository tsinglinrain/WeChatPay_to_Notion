import requests


class NotionClient:
    def __init__(self, database_id, token, payment_platform):
        self.database_id = database_id
        self.token = token

        self.payment_platform = payment_platform

    def create_notion_page(self, properties):

        url = "https://api.notion.com/v1/pages"
        payload = {
            "parent": {"database_id": self.database_id},
            "properties": properties,
            # "children": ["string"],    # 不需要children
            # "icon": "string",
            # "cover": "string"
        }
        headers = {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",  # 版本号
            "content-type": "application/json",
            "Authorization": "".join(
                ["Bearer", " ", self.token]
            ),  # 注意空格, 之前没注意空格, 一直报错
        }
        response = requests.post(url, json=payload, headers=headers)
        return response

    @staticmethod
    def response_result(response):

        if response.status_code == 200:
            print("成功...")
        else:
            print("失败...")
            print(response.text)

    def notion_property(
        self,
        content,
        price,
        category,
        date,
        counterparty,
        remarks,
        transaction_number="",
        merchant_tracking_number="",
        payment_method="undefined",
        time_zone="Asia/Shanghai",
    ):
        """将输入的内容转换为notion的json格式
        Args:
            content (str): 商品名称
            price (float): 价格
            category (str): 交易分类
            date (str): 交易时间
            Counterparty (str): 交易对方
            remarks (str): 备注
            transaction_number (str, optional): 交易订单号. Defaults to ""
            merchant_tracking_number (str, optional): 商家订单号. Defaults to ""
            payment_method (str, optional): 支付方式. Defaults to ""
            payment_platform (str, optional): 支付平台. Defaults to ""
            time_zone (str, optional): 时区. Defaults to "Asia/Shanghai"
        Returns:
            properties: 返回notion的json格式
        """
        payment_platform_dict = {"alipay": "Alipay", "wechatpay": "WeChatPay"}
        properties = {
            "Name": {"title": [{"text": {"content": content}}]},
            "Price": {"number": price},
            "Category": {"select": {"name": category}},
            "Date": {
                "date": {
                    "start": date,
                    "time_zone": time_zone,  # 时区, 参见官方文档
                }
            },
            "From": {"select": {"name": payment_platform_dict[self.payment_platform]}},
            "Counterparty": {"rich_text": [{"text": {"content": counterparty}}]},
            "Remarks": {"rich_text": [{"text": {"content": remarks}}]},
            "Transaction Number": {
                "rich_text": [{"text": {"content": transaction_number}}]
            },
            "Merchant Tracking Number": {
                "rich_text": [{"text": {"content": merchant_tracking_number}}]
            },
            "Payment Method": {"select": {"name": payment_method}},
        }
        return properties

    def process_row(self, row):
        if self.payment_platform == "alipay":
            properties = self.notion_property(
                row["商品说明"],
                row["金额"],
                row["交易分类"],
                row["交易时间"],
                row["交易对方"],
                row["备注"],
                row["交易订单号"],
                row["商家订单号"],
                row["收/付款方式"],
            )
        elif self.payment_platform == "wechatpay":
            properties = self.notion_property(
                row["商品"],
                row["金额(元)"],
                row["交易类型"],
                row["交易时间"],
                row["交易对方"],
                row["备注"],
                row["交易单号"],
                row["商户单号"],
                row["支付方式"],
            )
        else:
            raise ValueError("Invalid payment platform")
        response = self.create_notion_page(properties)
        NotionClient.response_result(response)
