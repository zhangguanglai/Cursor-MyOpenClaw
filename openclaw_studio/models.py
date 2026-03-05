"""
Pydantic 模型定义

定义所有 API 的请求和响应模型。
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class CaseBase(BaseModel):
    """案例基础模型"""
    title: str = Field(..., description="案例标题")
    description: str = Field(..., description="需求描述")
    repo_path: Optional[str] = Field(None, description="Git 仓库路径")
    branch: Optional[str] = Field(None, description="Git 分支")


class CaseCreate(CaseBase):
    """创建案例请求模型"""
    pass


class CaseOut(CaseBase):
    """案例响应模型"""
    id: str = Field(..., description="案例唯一 ID")
    status: str = Field("created", description="状态")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class PlanningRequestIn(BaseModel):
    """规划请求模型"""
    requirement_description: str = Field(..., description="需求描述")
    related_files: Optional[List[str]] = Field(None, description="相关文件列表")


class TaskOut(BaseModel):
    """任务输出模型"""
    id: str
    title: str
    description: str
    related_files: List[str] = []
    risk_level: str = "medium"
    status: Optional[str] = "pending"


class PlanningResponseOut(BaseModel):
    """规划响应模型"""
    plan_id: str = Field(..., description="计划 ID")
    plan_markdown: str = Field(..., description="计划 Markdown 内容")
    tasks: List[TaskOut] = Field(default_factory=list, description="任务列表")


class CodingRequestIn(BaseModel):
    """编码请求模型"""
    task_id: str = Field(..., description="任务 ID")
    task_title: str = Field(..., description="任务标题")
    task_description: str = Field(..., description="任务描述")
    related_files: List[str] = Field(default_factory=list, description="相关文件列表")


class PatchMeta(BaseModel):
    """补丁元数据模型"""
    file_path: str = Field(..., description="文件路径")
    diff: str = Field(..., description="补丁内容")
    description: str = Field(..., description="补丁描述")


class CodingResponseOut(BaseModel):
    """编码响应模型"""
    patches: List[PatchMeta] = Field(default_factory=list, description="补丁列表")


class TestRequestIn(BaseModel):
    """测试请求模型"""
    changes: List[Dict[str, Any]] = Field(default_factory=list, description="代码变更列表")


class TestResponseOut(BaseModel):
    """测试响应模型"""
    test_id: Optional[str] = Field(None, description="测试 ID")
    potential_issues: List[Dict[str, Any]] = Field(default_factory=list, description="潜在问题")
    test_cases: List[Dict[str, Any]] = Field(default_factory=list, description="测试用例")
    manual_checklist: List[str] = Field(default_factory=list, description="验收清单")
    checklist: Optional[List[str]] = Field(None, description="验收清单（别名）")
    generated_at: Optional[str] = Field(None, description="生成时间")


class HistoryItem(BaseModel):
    """历史记录项模型"""
    type: str = Field(..., description="记录类型")
    timestamp: str = Field(..., description="时间戳")
    description: str = Field(..., description="事件描述")
    data: Dict[str, Any] = Field(..., description="数据")


class CaseHistoryOut(BaseModel):
    """案例历史响应模型"""
    case: CaseOut = Field(..., description="案例信息")
    history: List[HistoryItem] = Field(default_factory=list, description="历史记录列表")
