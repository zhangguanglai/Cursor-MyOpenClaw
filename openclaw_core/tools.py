"""
Agent 工具集

提供代码读取、搜索等基础工具，供 Agent 使用。
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
import re


class CodeReader:
    """代码读取工具"""

    @staticmethod
    def read_file(file_path: str) -> str:
        """
        读取文件内容

        Args:
            file_path: 文件路径（相对或绝对）

        Returns:
            文件内容

        Raises:
            FileNotFoundError: 文件不存在
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def read_files(file_paths: List[str]) -> Dict[str, str]:
        """
        批量读取文件

        Args:
            file_paths: 文件路径列表

        Returns:
            文件路径到内容的映射
        """
        result = {}
        for file_path in file_paths:
            try:
                result[file_path] = CodeReader.read_file(file_path)
            except FileNotFoundError:
                result[file_path] = f"<文件不存在: {file_path}>"
        return result


class CodeSearcher:
    """代码搜索工具"""

    def __init__(self, root_dir: Optional[str] = None):
        """
        初始化搜索器

        Args:
            root_dir: 搜索根目录，默认当前工作目录
        """
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()

    def search_identifier(self, identifier: str, file_pattern: str = "*.py") -> List[Dict[str, any]]:
        """
        搜索标识符（函数名、类名、变量名）

        Args:
            identifier: 要搜索的标识符
            file_pattern: 文件匹配模式

        Returns:
            匹配结果列表，每个结果包含 file_path 和 line_number
        """
        results = []
        pattern = re.compile(rf"\b{re.escape(identifier)}\b")

        for file_path in self.root_dir.rglob(file_pattern):
            try:
                content = file_path.read_text(encoding="utf-8")
                for line_num, line in enumerate(content.splitlines(), 1):
                    if pattern.search(line):
                        results.append({
                            "file_path": str(file_path.relative_to(self.root_dir)),
                            "line_number": line_num,
                            "line_content": line.strip(),
                        })
            except Exception:
                continue

        return results

    def search_pattern(self, pattern: str, file_pattern: str = "*.py") -> List[Dict[str, any]]:
        """
        使用正则表达式搜索

        Args:
            pattern: 正则表达式
            file_pattern: 文件匹配模式

        Returns:
            匹配结果列表
        """
        results = []
        regex = re.compile(pattern)

        for file_path in self.root_dir.rglob(file_pattern):
            try:
                content = file_path.read_text(encoding="utf-8")
                for line_num, line in enumerate(content.splitlines(), 1):
                    if regex.search(line):
                        results.append({
                            "file_path": str(file_path.relative_to(self.root_dir)),
                            "line_number": line_num,
                            "line_content": line.strip(),
                        })
            except Exception:
                continue

        return results


class ProjectStructure:
    """项目结构工具"""

    def __init__(self, root_dir: Optional[str] = None):
        """
        初始化项目结构工具

        Args:
            root_dir: 项目根目录
        """
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()

    def get_structure(self, max_depth: int = 3, exclude_dirs: Optional[List[str]] = None) -> str:
        """
        获取项目结构概览

        Args:
            max_depth: 最大深度
            exclude_dirs: 排除的目录列表

        Returns:
            项目结构描述（文本）
        """
        if exclude_dirs is None:
            exclude_dirs = [".git", "__pycache__", ".pytest_cache", "venv", "env", ".venv", "node_modules"]

        lines = []
        lines.append(f"项目根目录: {self.root_dir}")

        def walk_dir(path: Path, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return

            try:
                items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    lines.append(f"{prefix}{current_prefix}{item.name}")

                    if item.is_dir() and item.name not in exclude_dirs:
                        next_prefix = prefix + ("    " if is_last else "│   ")
                        walk_dir(item, next_prefix, depth + 1)
            except PermissionError:
                pass

        walk_dir(self.root_dir)
        return "\n".join(lines)
