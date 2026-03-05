"""
规划 API

提供生成实现计划的接口。
"""

from fastapi import APIRouter, HTTPException, Depends
import asyncio

import json
from openclaw_studio.case_manager import CaseManager
from openclaw_studio.models import PlanningRequestIn, PlanningResponseOut, TaskOut
from openclaw_studio.api.dependencies import get_case_manager, get_planning_agent
from openclaw_core.agents import PlanningAgent

router = APIRouter(prefix="/cases", tags=["Planning"])


@router.post("/{case_id}/planning", response_model=PlanningResponseOut)
async def trigger_planning(
    case_id: str,
    request: PlanningRequestIn,
    case_manager: CaseManager = Depends(get_case_manager),
    agent: PlanningAgent = Depends(get_planning_agent),
):
    """触发 PlanningAgent 生成实现计划"""
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    try:
        # 构建 PlanningRequest
        planning_request = {
            "requirement_description": request.requirement_description,
            "related_files": request.related_files or [],
        }
        
        # 调用 PlanningAgent
        result = await agent.generate_plan(planning_request)
        
        # 保存计划
        plan = case_manager.save_plan(
            case_id=case_id,
            plan_markdown=result["plan_markdown"],
            tasks=result.get("tasks", []),
        )
        
        # 记录 Agent 调用
        case_manager.record_agent_run(
            case_id=case_id,
            agent_type="planning",
            input_data=planning_request,
            output_data={"plan_id": plan.id, "tasks_count": len(result.get("tasks", []))},
            model=agent.llm_router.select_model("planning"),
        )
        
        # 转换任务格式
        tasks = [
            TaskOut(
                id=task.get("id", ""),
                title=task.get("title", ""),
                description=task.get("description", ""),
                related_files=task.get("related_files", []),
                risk_level=task.get("risk_level", "medium")
            )
            for task in result.get("tasks", [])
        ]
        
        return PlanningResponseOut(
            plan_markdown=result["plan_markdown"],
            tasks=tasks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")


@router.get("/{case_id}/planning", response_model=PlanningResponseOut)
async def get_planning(
    case_id: str,
    case_manager: CaseManager = Depends(get_case_manager),
):
    """获取案例的实现计划"""
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    plan_data = case_manager.get_plan(case_id)
    if not plan_data:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # 转换任务格式
    tasks = [
        TaskOut(
            id=task.id,
            title=task.title,
            description=task.description or "",
            related_files=json.loads(task.related_files) if task.related_files else [],
            risk_level=task.risk_level or "medium"
        )
        for task in case_manager.get_tasks(case_id)
    ]
    
    return PlanningResponseOut(
        plan_markdown=plan_data.get("markdown", ""),
        tasks=tasks
    )
