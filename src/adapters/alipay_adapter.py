"""Alipay payment platform adapter."""

from typing import Dict
from src.adapters.base import PaymentAdapter


class AlipayAdapter(PaymentAdapter):
    """Adapter for Alipay payment platform."""

    def __init__(self):
        super().__init__("alipay")

    def get_email_sender(self) -> str:
        """Alipay sends bills from this email address."""
        return "service@mail.alipay.com"

    def get_csv_encoding(self) -> str:
        """Alipay CSV files use GBK encoding."""
        return "gbk"

    def get_bill_file_prefix(self) -> str:
        """Alipay bill files start with this prefix."""
        return "支付宝交易明细"

    def get_notion_display_name(self) -> str:
        """Display name in Notion."""
        return "Alipay"

    def get_csv_column_mapping(self) -> Dict[str, str]:
        """Alipay CSV column names."""
        return {
            'content': '商品说明',
            'amount': '金额',
            'transaction_type': '收/支',
            'category': '交易分类',
            'datetime': '交易时间',
            'counterparty': '交易对方',
            'remarks': '备注',
            'transaction_id': '交易订单号',
            'merchant_order_id': '商家订单号',
            'payment_method': '收/付款方式',
        }

    def process_amount(self, amount_str: str) -> float:
        """Alipay amount is already a plain number string.
        
        Args:
            amount_str: Amount string like '123.45'
            
        Returns:
            Float value
        """
        return float(amount_str)

    def process_remarks(self, remarks_str: str) -> str:
        """Alipay remarks don't need special processing.
        
        Args:
            remarks_str: Raw remarks
            
        Returns:
            Same remarks string
        """
        return remarks_str

    def needs_excel_conversion(self) -> bool:
        """Alipay provides CSV files directly."""
        return False
