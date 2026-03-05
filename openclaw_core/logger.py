"""
OpenClaw 日志记录模块

提供统一的日志记录功能，支持多级别、文件输出和日志轮转。
"""

import logging
import logging.handlers
from pathlib import Path
import yaml
from typing import Optional


class Logger:
    """OpenClaw 日志记录器"""
    
    def __init__(self, name: str = "openclaw", level: str = "INFO"):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # 避免重复添加 Handler
        if not self.logger.handlers:
            # 控制台 Handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """记录 DEBUG 级别日志"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """记录 INFO 级别日志"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录 WARNING 级别日志"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录 ERROR 级别日志"""
        self.logger.error(message)
    
    def add_file_handler(self, file_path: Path, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
        """
        添加文件 Handler（支持日志轮转）
        
        Args:
            file_path: 日志文件路径
            max_bytes: 单个日志文件最大大小（字节）
            backup_count: 保留的备份文件数量
        """
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(file_handler)
    
    def add_timed_file_handler(
        self,
        file_path: Path,
        when: str = 'midnight',
        interval: int = 1,
        backup_count: int = 7
    ):
        """
        添加按时间轮转的文件 Handler
        
        Args:
            file_path: 日志文件路径
            when: 轮转时间单位 ('S', 'M', 'H', 'D', 'W', 'midnight')
            interval: 轮转间隔
            backup_count: 保留的备份文件数量
        """
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        timed_handler = logging.handlers.TimedRotatingFileHandler(
            file_path,
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding='utf-8'
        )
        timed_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(timed_handler)
    
    @classmethod
    def from_config(cls, config_path: Optional[Path] = None):
        """
        从配置文件创建 Logger
        
        Args:
            config_path: 配置文件路径，默认查找 config/logger.yml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "logger.yml"
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        else:
            config = {}
        
        name = config.get('name', 'openclaw')
        level = config.get('level', 'INFO')
        logger = cls(name=name, level=level)
        
        # 如果配置了文件输出
        if 'file' in config:
            file_path = Path(config['file']['path'])
            max_bytes = config['file'].get('max_bytes', 10 * 1024 * 1024)
            backup_count = config['file'].get('backup_count', 5)
            logger.add_file_handler(file_path, max_bytes, backup_count)
        
        # 如果配置了时间轮转
        if 'timed_file' in config:
            file_path = Path(config['timed_file']['path'])
            when = config['timed_file'].get('when', 'midnight')
            interval = config['timed_file'].get('interval', 1)
            backup_count = config['timed_file'].get('backup_count', 7)
            logger.add_timed_file_handler(file_path, when, interval, backup_count)
        
        return logger


# 默认日志记录器实例
_default_logger: Optional[Logger] = None


def get_logger(name: str = "openclaw", level: str = "INFO") -> Logger:
    """
    获取日志记录器实例（单例模式）
    
    Args:
        name: 日志记录器名称
        level: 日志级别
    
    Returns:
        Logger 实例
    """
    global _default_logger
    if _default_logger is None:
        _default_logger = Logger(name=name, level=level)
    return _default_logger
