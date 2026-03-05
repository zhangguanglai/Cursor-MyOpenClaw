"""
知识库 API

提供知识库搜索、模板管理等 API 端点。
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel

from openclaw_studio.knowledge_base import KnowledgeBase, KnowledgeItem
from openclaw_core.logger import get_logger

logger = get_logger("openclaw.api.knowledge")

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


# Pydantic 模型
class KnowledgeItemOut(BaseModel):
    """知识库项输出模型"""
    path: str
    title: str
    content: str
    category: str
    tags: List[str]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}


class SearchRequest(BaseModel):
    """搜索请求模型"""
    query: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class SearchResponse(BaseModel):
    """搜索响应模型"""
    results: List[KnowledgeItemOut]
    total: int


# 依赖注入
def get_knowledge_base() -> KnowledgeBase:
    """获取知识库实例"""
    return KnowledgeBase()


@router.get("/search", response_model=SearchResponse)
async def search_knowledge(
    q: str = Query(..., description="搜索关键词"),
    category: Optional[str] = Query(None, description="类别筛选"),
    tags: Optional[str] = Query(None, description="标签筛选（逗号分隔）"),
    knowledge_base: KnowledgeBase = Depends(get_knowledge_base),
):
    """搜索知识库"""
    try:
        tag_list = tags.split(",") if tags else None
        if tag_list:
            tag_list = [tag.strip() for tag in tag_list]
        
        results = knowledge_base.search(q, category=category, tags=tag_list)
        
        return SearchResponse(
            results=[KnowledgeItemOut(**item.__dict__) for item in results],
            total=len(results),
        )
    except Exception as e:
        logger.error(f"搜索知识库失败: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/templates", response_model=List[str])
async def list_templates(
    knowledge_base: KnowledgeBase = Depends(get_knowledge_base),
):
    """列出所有模板"""
    try:
        return knowledge_base.list_templates()
    except Exception as e:
        logger.error(f"获取模板列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {str(e)}")


@router.get("/templates/{template_name}")
async def get_template(
    template_name: str,
    knowledge_base: KnowledgeBase = Depends(get_knowledge_base),
):
    """获取模板内容"""
    try:
        content = knowledge_base.get_template(template_name)
        if not content:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"template_name": template_name, "content": content}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模板失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")


@router.get("/items", response_model=List[KnowledgeItemOut])
async def list_items(
    category: Optional[str] = Query(None, description="类别筛选"),
    knowledge_base: KnowledgeBase = Depends(get_knowledge_base),
):
    """列出知识库项"""
    try:
        items = knowledge_base.list_items(category=category)
        return [KnowledgeItemOut(**item.__dict__) for item in items]
    except Exception as e:
        logger.error(f"列出知识库项失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list items: {str(e)}")


@router.post("/cases/{case_id}/archive")
async def archive_case(
    case_id: str,
    knowledge_base: KnowledgeBase = Depends(get_knowledge_base),
):
    """归档案例到知识库"""
    try:
        from pathlib import Path
        from openclaw_studio.case_manager import CaseManager
        
        case_manager = CaseManager()
        case = case_manager.get_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # 获取案例目录
        case_dir = Path("cases") / case_id
        if not case_dir.exists():
            raise HTTPException(status_code=404, detail="Case directory not found")
        
        success = knowledge_base.archive_case(case_id, case_dir)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to archive case")
        
        return {"message": f"Case {case_id} archived successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"归档案例失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to archive case: {str(e)}")
