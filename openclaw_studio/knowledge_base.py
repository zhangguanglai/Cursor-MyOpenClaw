"""
知识库管理模块

提供知识库的搜索、模板管理等功能。
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from openclaw_core.logger import get_logger

logger = get_logger("openclaw.knowledge_base")


@dataclass
class KnowledgeItem:
    """知识库项"""
    path: str
    title: str
    content: str
    category: str  # rules, playbooks, templates, cases
    tags: List[str]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class KnowledgeBase:
    """知识库管理器"""

    def __init__(self, base_path: str = "knowledge_base"):
        """
        初始化知识库

        Args:
            base_path: 知识库根目录路径
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        # 确保子目录存在
        for subdir in ["rules", "playbooks", "templates", "cases"]:
            (self.base_path / subdir).mkdir(exist_ok=True)

    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        从 Markdown 内容中提取元数据

        Args:
            content: Markdown 内容

        Returns:
            元数据字典
        """
        metadata = {
            "title": "",
            "tags": [],
        }
        
        # 提取标题（第一个 # 标题）
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata["title"] = title_match.group(1).strip()
        
        # 提取标签（从 frontmatter 或内容中）
        frontmatter_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            tags_match = re.search(r'tags:\s*\[(.*?)\]', frontmatter)
            if tags_match:
                tags_str = tags_match.group(1)
                metadata["tags"] = [tag.strip().strip('"\'') for tag in tags_str.split(',')]
        
        return metadata

    def _load_file(self, file_path: Path) -> Optional[KnowledgeItem]:
        """
        加载文件并创建 KnowledgeItem

        Args:
            file_path: 文件路径

        Returns:
            KnowledgeItem 或 None
        """
        if not file_path.exists() or not file_path.is_file():
            return None
        
        try:
            content = file_path.read_text(encoding="utf-8")
            metadata = self._extract_metadata(content)
            
            # 确定类别
            relative_path = file_path.relative_to(self.base_path)
            category = relative_path.parts[0] if relative_path.parts else "unknown"
            
            # 获取文件时间
            stat = file_path.stat()
            created_at = datetime.fromtimestamp(stat.st_ctime).isoformat()
            updated_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            return KnowledgeItem(
                path=str(relative_path),
                title=metadata.get("title", file_path.stem),
                content=content,
                category=category,
                tags=metadata.get("tags", []),
                created_at=created_at,
                updated_at=updated_at,
            )
        except Exception as e:
            logger.error(f"加载文件失败 {file_path}: {e}")
            return None

    def search(self, query: str, category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[KnowledgeItem]:
        """
        搜索知识库

        Args:
            query: 搜索关键词
            category: 类别筛选（rules, playbooks, templates, cases）
            tags: 标签筛选

        Returns:
            匹配的知识库项列表
        """
        results = []
        query_lower = query.lower()
        
        # 遍历所有 Markdown 文件
        for md_file in self.base_path.rglob("*.md"):
            # 跳过 README.md（可选）
            if md_file.name == "README.md":
                continue
            
            item = self._load_file(md_file)
            if not item:
                continue
            
            # 类别筛选
            if category and item.category != category:
                continue
            
            # 标签筛选
            if tags and not any(tag in item.tags for tag in tags):
                continue
            
            # 搜索匹配
            if (query_lower in item.title.lower() or 
                query_lower in item.content.lower()):
                results.append(item)
        
        # 按更新时间排序（最新的在前）
        results.sort(key=lambda x: x.updated_at or "", reverse=True)
        
        return results

    def get_template(self, template_name: str) -> Optional[str]:
        """
        获取模板内容

        Args:
            template_name: 模板名称（不含扩展名）

        Returns:
            模板内容或 None
        """
        template_path = self.base_path / "templates" / f"{template_name}.md"
        if template_path.exists():
            return template_path.read_text(encoding="utf-8")
        return None

    def list_templates(self) -> List[str]:
        """
        列出所有模板

        Returns:
            模板名称列表
        """
        templates_dir = self.base_path / "templates"
        if not templates_dir.exists():
            return []
        
        templates = []
        for md_file in templates_dir.glob("*.md"):
            if md_file.name != "README.md":
                templates.append(md_file.stem)
        
        return templates

    def archive_case(self, case_id: str, case_dir: Path) -> bool:
        """
        归档案例到知识库

        Args:
            case_id: 案例 ID
            case_dir: 案例目录路径

        Returns:
            是否成功归档
        """
        try:
            archive_dir = self.base_path / "cases" / case_id
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制案例文件
            if case_dir.exists():
                import shutil
                for item in case_dir.iterdir():
                    if item.is_file():
                        shutil.copy2(item, archive_dir / item.name)
                    elif item.is_dir():
                        shutil.copytree(item, archive_dir / item.name, dirs_exist_ok=True)
            
            logger.info(f"案例 {case_id} 已归档到知识库")
            return True
        except Exception as e:
            logger.error(f"归档案例失败 {case_id}: {e}")
            return False

    def list_items(self, category: Optional[str] = None) -> List[KnowledgeItem]:
        """
        列出知识库项

        Args:
            category: 类别筛选

        Returns:
            知识库项列表
        """
        items = []
        
        for md_file in self.base_path.rglob("*.md"):
            if md_file.name == "README.md":
                continue
            
            item = self._load_file(md_file)
            if item:
                if category is None or item.category == category:
                    items.append(item)
        
        return items
