from notion_client import Client


class NotionClient:
    def __init__(self, database_id: str, token: str, payment_platform: str):
        self.database_id = database_id
        self.token = token
        self.client: Client = Client(auth=token)
        self.payment_platform = payment_platform

    def create_page(self, properties: dict) -> None:
        """Create a new page in the database"""

        try:
            self.client.pages.create(
                # icon = {
                #     "external": {
                #         "url": icon_url  # 使用上传文件的 URL 作为图标
                #     }
                # },    # 我个人没有这个需求,如果有,可以加上
                # cover # 也没有需求
                parent={"database_id": self.database_id},
                properties=properties,
                # children=blocks,  # 不要children
            )
            print("Page created successfully\n上传成功")
        except Exception as e:
            print(f"Failed to create page: {e}")
            print("-" * 20)
            print("上传失败,自动跳过,请自行检查")

    def notion_property(
        self,
        content: str,
        price: float,
        category: str,
        date: str,
        counterparty: str,
        remarks: str,
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
        self.create_page(properties)
