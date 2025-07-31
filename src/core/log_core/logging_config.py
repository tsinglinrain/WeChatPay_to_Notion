"""
项目统一日志配置模块

该模块提供了项目级别的日志配置，确保所有模块使用一致的日志格式和配置。
支持控制台输出和文件输出，并提供不同的日志级别。
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional


class LogConfig:
    """日志配置类"""
    
    # 日志格式
    DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    SIMPLE_FORMAT = '%(levelname)s - %(message)s'
    DETAILED_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    
    # 日志级别映射
    LEVEL_MAPPING = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    @classmethod
    def setup_logging(
        cls,
        level: str = 'INFO',
        log_file: Optional[str] = None,
        console_output: bool = True,
        format_type: str = 'default'
    ) -> None:
        """
        设置项目日志配置
        
        Args:
            level: 日志级别 ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
            log_file: 日志文件路径，如果为None则不输出到文件
            console_output: 是否输出到控制台
            format_type: 格式类型 ('default', 'simple', 'detailed')
        """
        # 获取格式
        if format_type == 'simple':
            log_format = cls.SIMPLE_FORMAT
        elif format_type == 'detailed':
            log_format = cls.DETAILED_FORMAT
        else:
            log_format = cls.DEFAULT_FORMAT
        
        # 清除现有的处理器，避免重复配置
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 设置根日志级别
        log_level = cls.LEVEL_MAPPING.get(level.upper(), logging.INFO)
        root_logger.setLevel(log_level)
        
        handlers = []
        
        # 控制台处理器
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(logging.Formatter(log_format))
            handlers.append(console_handler)
        
        # 文件处理器
        if log_file:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 使用RotatingFileHandler避免日志文件过大
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(logging.Formatter(log_format))
            handlers.append(file_handler)
        
        # 添加处理器到根日志器
        for handler in handlers:
            root_logger.addHandler(handler)
        
        # 设置第三方库的日志级别，避免过多输出
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('chardet').setLevel(logging.WARNING)
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取指定名称的日志器
        
        Args:
            name: 日志器名称，通常使用 __name__
            
        Returns:
            logging.Logger: 配置好的日志器
        """
        return logging.getLogger(name)


def setup_project_logging(
    level: str = 'INFO',
    enable_file_logging: bool = True,
    log_directory: str = 'logs'
) -> None:
    """
    为整个项目设置日志配置
    
    Args:
        level: 日志级别
        enable_file_logging: 是否启用文件日志
        log_directory: 日志文件目录
    """
    log_file = None
    if enable_file_logging:
        # 在项目根目录创建logs文件夹
        log_file = os.path.join(log_directory, 'wechatpay_to_notion.log')
    
    LogConfig.setup_logging(
        level=level,
        log_file=log_file,
        console_output=True,
        format_type='default'
    )


def get_logger(name: str = None) -> logging.Logger:
    """
    便捷函数：获取日志器
    
    Args:
        name: 日志器名称，如果为None则使用调用者的模块名
        
    Returns:
        logging.Logger: 日志器实例
    """
    if name is None:
        # 获取调用者的模块名
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'unknown')
    
    return LogConfig.get_logger(name)


# 项目启动时自动配置日志
if not logging.getLogger().handlers:
    setup_project_logging()
