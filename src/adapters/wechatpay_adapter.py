"""WeChat Pay payment platform adapter."""

from typing import Dict
from src.adapters.base import PaymentAdapter


class WechatpayAdapter(PaymentAdapter):
    """Adapter for WeChat Pay payment platform."""

    def __init__(self):
        super().__init__("wechatpay")

    def get_email_sender(self) -> str:
        """WeChat Pay sends bills from this email address."""
        return "wechatpay@tencent.com"

    def get_csv_encoding(self) -> str:
        """WeChat Pay CSV files use UTF-8 encoding."""
        return "utf-8"

    def get_bill_file_prefix(self) -> str:
        """WeChat Pay bill files start with this prefix."""
        return "微信支付账单"

    def get_notion_display_name(self) -> str:
        """Display name in Notion."""
        return "WeChatPay"

    def get_csv_column_mapping(self) -> Dict[str, str]:
        """WeChat Pay CSV column names."""
        return {
            'content': '商品',
            'amount': '金额(元)',
            'category': '交易类型',
            'datetime': '交易时间',
            'counterparty': '交易对方',
            'remarks': '备注',
            'transaction_id': '交易单号',
            'merchant_order_id': '商户单号',
            'payment_method': '支付方式',
        }

    def process_amount(self, amount_str: str) -> float:
        """WeChat Pay amount has ¥ prefix that needs to be removed.
        
        Args:
            amount_str: Amount string like '¥123.45'
            
        Returns:
            Float value with ¥ removed
        """
        # Remove ¥ symbol if present
        if isinstance(amount_str, str) and amount_str.startswith('¥'):
            return float(amount_str[1:])
        return float(amount_str)

    def process_remarks(self, remarks_str: str) -> str:
        """WeChat Pay uses '/' for empty remarks, convert to empty string.
        
        Args:
            remarks_str: Raw remarks (may be '/')
            
        Returns:
            Empty string if '/', otherwise original string
        """
        return "" if remarks_str == "/" else remarks_str

    def needs_excel_conversion(self) -> bool:
        """WeChat Pay provides Excel files that need conversion to CSV."""
        return True
