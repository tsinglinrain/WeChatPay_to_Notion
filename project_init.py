"""
项目启动模块

该模块在项目启动时自动配置日志系统，确保所有模块使用统一的日志配置。
可以根据环境变量或配置文件调整日志级别和输出方式。
"""

import os
from src.core.log_core.logging_config import setup_project_logging


def initialize_project():
    """初始化项目设置"""
    # 从环境变量获取日志级别，默认为INFO
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # 从环境变量获取是否启用文件日志，默认为True
    enable_file_logging = os.getenv('ENABLE_FILE_LOGGING', 'true').lower() == 'true'
    
    # 设置日志配置
    setup_project_logging(
        level=log_level,
        enable_file_logging=enable_file_logging,
        log_directory='logs'
    )
    
    # 获取logger并记录初始化信息
    from src.core.log_core.logging_config import get_logger
    logger = get_logger(__name__)
    
    logger.info("=" * 50)
    logger.info("WeChatPay to Notion Project Started")
    logger.info(f"Log Level: {log_level}")
    logger.info(f"File Logging: {'Enabled' if enable_file_logging else 'Disabled'}")
    logger.info("=" * 50)


# 在模块导入时自动初始化
initialize_project()
