"""
配置加载模块

提供统一的配置加载接口。
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_llm_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载 LLM 配置文件

    Args:
        config_path: 配置文件路径，默认查找 config/llm.yml

    Returns:
        配置字典
    """
    if config_path:
        path = Path(config_path)
    else:
        path = Path(__file__).parent.parent / "config" / "llm.yml"

    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
