"""
环境变量配置模块
用于从环境变量或.env文件中加载配置
"""

import os
from typing import Tuple
from dotenv import load_dotenv

load_dotenv()


def get_email_config() -> Tuple[str | None, str | None, str | None]:
    """
    获取邮箱配置
    返回: (username, password, imap_url)
    """
    username = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")
    imap_url = os.getenv("EMAIL_IMAP_URL")

    if not all([username, password, imap_url]):
        missing = []
        if not username:
            missing.append("EMAIL_USERNAME")
        if not password:
            missing.append("EMAIL_PASSWORD")
        if not imap_url:
            missing.append("EMAIL_IMAP_URL")
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return username, password, imap_url


def get_notion_config() -> Tuple[str | None, str | None]:
    """
    获取Notion配置
    返回: (data_source_id, token)
    """
    data_source_id = os.getenv("NOTION_DATA_SOURCE_ID")
    token = os.getenv("NOTION_TOKEN")

    if not all([data_source_id, token]):
        missing = []
        if not data_source_id:
            missing.append("NOTION_DATA_SOURCE_ID")
        if not token:
            missing.append("NOTION_TOKEN")
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return data_source_id, token


def config_loader() -> Tuple[str, str, str, str, str]:
    """
    加载所有配置
    返回: (username, password, imap_url, data_source_id, token)
    """
    username, password, imap_url = get_email_config()
    data_source_id, token = get_notion_config()

    return username, password, imap_url, data_source_id, token
