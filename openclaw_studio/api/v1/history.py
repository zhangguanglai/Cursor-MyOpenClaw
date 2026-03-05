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
    case_manager: CaseManager = Depends(get_case_manager),
):
    """获取案例的完整历史记录"""
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    history = []
    
    # 1. Case 本身
    history.append(HistoryItem(
        type="case",
        timestamp=case.created_at,
        data={
            "id": case.id,
            "title": case.title,
            "status": case.status,
        }
    ))
    
    # 2. Plan (如果存在)
    plan = case_manager.get_plan(case_id)
    if plan:
        history.append(HistoryItem(
            type="plan",
            timestamp=plan["plan"].created_at if hasattr(plan["plan"], "created_at") else case.updated_at,
            data={
                "plan_id": plan["plan"].id,
                "tasks_count": len(plan.get("tasks", [])),
            }
        ))
    
    # 3. Agent 调用记录
    agent_runs = case_manager.db.get_agent_runs(case_id)
    for run in agent_runs:
        history.append(HistoryItem(
            type="agent_run",
            timestamp=run.created_at,
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
                history.append(HistoryItem(
                    type="patch",
                    timestamp=meta.get("created_at", case.updated_at),
                    data=meta
                ))
            except Exception:
                pass
    
    # 按时间排序
    history.sort(key=lambda x: x.timestamp, reverse=True)
    
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
