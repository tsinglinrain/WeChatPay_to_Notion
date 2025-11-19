"""Base adapter interface for payment platforms."""

from abc import ABC, abstractmethod
from typing import Dict


class PaymentAdapter(ABC):
    """Abstract base class for payment platform adapters."""

    def __init__(self, platform_name: str):
        self.platform_name = platform_name

    @abstractmethod
    def get_email_sender(self) -> str:
        """Return the email address that sends bill notifications."""
        pass

    @abstractmethod
    def get_csv_encoding(self) -> str:
        """Return the CSV file encoding for this platform."""
        pass

    @abstractmethod
    def get_bill_file_prefix(self) -> str:
        """Return the prefix of downloaded bill files (e.g., '支付宝交易明细')."""
        pass

    @abstractmethod
    def get_notion_display_name(self) -> str:
        """Return the display name for Notion (e.g., 'Alipay', 'WeChatPay')."""
        pass

    @abstractmethod
    def get_csv_column_mapping(self) -> Dict[str, str]:
        """Return column name mapping from platform CSV to standard format.
        
        Returns:
            Dict mapping: {
                'content': '商品说明',  # product description column
                'amount': '金额',       # amount column
                'category': '交易分类',  # category column
                'datetime': '交易时间',  # datetime column
                'counterparty': '交易对方',  # counterparty column
                'remarks': '备注',      # remarks column
                'transaction_id': '交易订单号',  # transaction number
                'merchant_order_id': '商家订单号',  # merchant order number
                'payment_method': '收/付款方式',  # payment method
            }
        """
        pass

    @abstractmethod
    def process_amount(self, amount_str: str) -> float:
        """Convert platform-specific amount string to float.
        
        Args:
            amount_str: Amount string from CSV (e.g., '123.45' or '¥123.45')
            
        Returns:
            Float amount value
        """
        pass

    @abstractmethod
    def process_remarks(self, remarks_str: str) -> str:
        """Process platform-specific remarks field.
        
        Args:
            remarks_str: Raw remarks string from CSV
            
        Returns:
            Processed remarks string
        """
        pass

    @abstractmethod
    def needs_excel_conversion(self) -> bool:
        """Return True if downloaded files are Excel and need conversion to CSV."""
        pass
