"""
OpenClaw Core - AI 原生研发平台内核

提供多模型路由、Agent 编排等核心能力。
"""

__version__ = "0.1.0"

# 导出 Logger
from openclaw_core.logger import Logger, get_logger

__all__ = ["Logger", "get_logger"]
