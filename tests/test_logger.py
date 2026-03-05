"""
Logger 模块测试
"""

import pytest
import tempfile
from pathlib import Path
from openclaw_core.logger import Logger, get_logger


class TestLogger:
    """测试 Logger 类"""

    def test_logger_initialization(self):
        """测试日志记录器初始化"""
        logger = Logger(name="test", level="DEBUG")
        assert logger.logger.name == "test"
        assert logger.logger.level == 10  # DEBUG

    def test_logger_methods(self, caplog):
        """测试日志方法"""
        logger = Logger(name="test", level="DEBUG")
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # 使用 caplog 捕获日志记录
        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text

    def test_add_file_handler(self, tmp_path):
        """测试添加文件 Handler"""
        log_file = tmp_path / "test.log"
        logger = Logger(name="test")
        logger.add_file_handler(log_file)
        
        logger.info("Test message")
        
        assert log_file.exists()
        content = log_file.read_text(encoding='utf-8')
        assert "Test message" in content

    def test_add_timed_file_handler(self, tmp_path):
        """测试添加时间轮转 Handler"""
        log_file = tmp_path / "test_timed.log"
        logger = Logger(name="test")
        logger.add_timed_file_handler(log_file, when='midnight')
        
        logger.info("Test timed message")
        
        assert log_file.exists()
        content = log_file.read_text(encoding='utf-8')
        assert "Test timed message" in content

    def test_from_config_file_exists(self, tmp_path):
        """测试从配置文件创建 Logger（文件存在）"""
        import yaml
        
        config_file = tmp_path / "logger.yml"
        config = {
            'name': 'test_config',
            'level': 'DEBUG',
            'file': {
                'path': str(tmp_path / 'app.log'),
                'max_bytes': 1024,
                'backup_count': 3
            }
        }
        config_file.write_text(yaml.dump(config), encoding='utf-8')
        
        logger = Logger.from_config(config_file)
        assert logger.logger.name == "test_config"
        assert logger.logger.level == 10  # DEBUG

    def test_from_config_file_not_exists(self):
        """测试从配置文件创建 Logger（文件不存在）"""
        fake_path = Path("/nonexistent/logger.yml")
        logger = Logger.from_config(fake_path)
        # 应该使用默认配置
        assert logger is not None

    def test_get_logger_singleton(self):
        """测试 get_logger 单例模式"""
        logger1 = get_logger()
        logger2 = get_logger()
        # 应该是同一个实例
        assert logger1 is logger2
