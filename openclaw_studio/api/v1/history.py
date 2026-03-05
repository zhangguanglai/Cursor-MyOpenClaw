"""
历史记录 API

提供案例历史记录的查询接口。
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pathlib import Path
import json

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.models import CaseHistoryOut, HistoryItem, CaseOut
from openclaw_studio.api.dependencies import get_case_manager

router = APIRouter(prefix="/cases", tags=["History"])


@router.get("/{case_id}/history", response_model=CaseHistoryOut)
async def get_case_history(
    case_id: str,
    types: str = None,
    startTime: str = None,
    endTime: str = None,
    search: str = None,
    case_manager: CaseManager = Depends(get_case_manager),
):
    """获取案例的完整历史记录"""
    from datetime import datetime
    
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    history = []
    
    # 1. Case 本身
    history.append(HistoryItem(
        type="case",
        timestamp=case.created_at,
        description=f"创建案例: {case.title}",
        data={
            "id": case.id,
            "title": case.title,
            "status": case.status,
        }
    ))
    
    # 2. Plan (如果存在)
    plan_data = case_manager.get_plan(case_id)
    if plan_data:
        plan = plan_data.get("plan")
        if plan:
            history.append(HistoryItem(
                type="plan",
                timestamp=plan.created_at if plan.created_at else case.updated_at,
                description=f"生成实现计划 ({len(plan_data.get('tasks', []))} 个任务)",
                data={
                    "plan_id": plan.id,
                    "tasks_count": len(plan_data.get("tasks", [])),
                }
            ))
    
    # 3. Agent 调用记录
    agent_runs = case_manager.db.get_agent_runs(case_id)
    for run in agent_runs:
        agent_type_label = {"planning": "规划", "coding": "编码", "test": "测试"}.get(run.agent_type, run.agent_type)
        history.append(HistoryItem(
            type="agent_run",
            timestamp=run.created_at or case.updated_at,
            description=f"{agent_type_label} Agent 调用 ({run.model or 'N/A'})",
            data={
                "agent_type": run.agent_type,
                "model": run.model,
                "status": run.status,
            }
        ))
    
    # 4. 补丁记录
    patches_dir = Path(f"cases/{case_id}/patches")
    if patches_dir.exists():
        for meta_file in patches_dir.glob("*.meta.json"):
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                task_id = meta.get("task_id", "")
                file_path = meta.get("file_path", "")
                description = meta.get("description", "")
                history.append(HistoryItem(
                    type="patch",
                    timestamp=meta.get("created_at", case.updated_at),
                    description=f"生成补丁: {file_path}",
                    data={
                        "task_id": task_id,
                        "file_path": file_path,
                        "description": description,
                        **meta
                    }
                ))
            except Exception:
                pass
    
    # 5. 测试记录（从 agent_runs 中提取 test 类型）
    test_runs = [r for r in agent_runs if r.agent_type == "test"]
    for run in test_runs:
        history.append(HistoryItem(
            type="test",
            timestamp=run.created_at or case.updated_at,
            description="执行测试分析",
            data={
                "test_id": run.id,
                "status": run.status,
            }
        ))
    
    # 按时间排序
    history.sort(key=lambda x: x.timestamp or "", reverse=True)
    
    # 应用筛选
    if types:
        type_list = types.split(",")
        history = [h for h in history if h.type in type_list]
    
    if startTime:
        start = datetime.fromisoformat(startTime.replace("Z", "+00:00"))
        history = [h for h in history if h.timestamp and datetime.fromisoformat(h.timestamp.replace("Z", "+00:00")) >= start]
    
    if endTime:
        end = datetime.fromisoformat(endTime.replace("Z", "+00:00"))
        history = [h for h in history if h.timestamp and datetime.fromisoformat(h.timestamp.replace("Z", "+00:00")) <= end]
    
    if search:
        search_lower = search.lower()
        history = [
            h for h in history
            if search_lower in h.description.lower() or search_lower in json.dumps(h.data).lower()
        ]
    
    return CaseHistoryOut(
        case=CaseOut(
            id=case.id,
            title=case.title,
            description=case.description or "",
            repo_path=case.repo_path,
            branch=case.branch,
            status=case.status,
            created_at=case.created_at,
            updated_at=case.updated_at
        ),
        history=history
    )
