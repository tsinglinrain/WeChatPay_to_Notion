"""Factory for creating payment platform adapters."""

from typing import Dict, Type
from src.adapters.base import PaymentAdapter
from src.adapters.alipay_adapter import AlipayAdapter
from src.adapters.wechat_adapter import WechatAdapter


class AdapterFactory:
    """Factory class for creating payment platform adapters."""

    _adapters: Dict[str, Type[PaymentAdapter]] = {
        "alipay": AlipayAdapter,
        "wechatpay": WechatAdapter,
    }

    @classmethod
    def create(cls, platform: str) -> PaymentAdapter:
        """Create an adapter for the specified platform.
        
        Args:
            platform: Platform name ('alipay' or 'wechatpay')
            
        Returns:
            PaymentAdapter instance for the platform
            
        Raises:
            ValueError: If platform is not supported
        """
        adapter_class = cls._adapters.get(platform)
        if adapter_class is None:
            raise ValueError(
                f"Unsupported platform: {platform}. "
                f"Supported platforms: {list(cls._adapters.keys())}"
            )
        return adapter_class()

    @classmethod
    def get_supported_platforms(cls) -> list:
        """Get list of supported platform names.
        
        Returns:
            List of supported platform identifiers
        """
        return list(cls._adapters.keys())
