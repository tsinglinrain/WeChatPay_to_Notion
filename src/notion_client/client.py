from notion_client import Client
from src.adapters.base import PaymentAdapter
from src.utils.logger import get_logger


class NotionClient:
    def __init__(self, data_source_id, token, adapter: PaymentAdapter):
        self.data_source_id = data_source_id
        self.token = token
        self.client: Client = Client(auth=token)
        self.adapter = adapter
        self.logger = get_logger()

    def create_page(self, properties):
        """Create a new page in the data_source"""

        try:
            self.client.pages.create(
                # icon = {
                #     "external": {
                #         "url": icon_url  # 使用上传文件的 URL 作为图标
                #     }
                # },    # 我个人没有这个需求,如果有,可以加上
                # cover # 也没有需求
                parent={"data_source_id": self.data_source_id},
                properties=properties,
                # children=blocks,  # 不要children
            )
            self.logger.info("Page created successfully | 上传成功")
        except Exception as e:
            self.logger.error(f"Failed to create page: {e}")
            self.logger.warning("Upload failed, skipping | 上传失败,自动跳过,请自行检查")

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
            "From": {"select": {"name": self.adapter.get_notion_display_name()}},
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
        # Use adapter to get column mapping
        col_map = self.adapter.get_csv_column_mapping()
        
        properties = self.notion_property(
            row[col_map['content']],
            row[col_map['amount']],
            row[col_map['category']],
            row[col_map['datetime']],
            row[col_map['counterparty']],
            row[col_map['remarks']],
            row[col_map['transaction_id']],
            row[col_map['merchant_order_id']],
            row[col_map['payment_method']],
        )
        self.create_page(properties)
