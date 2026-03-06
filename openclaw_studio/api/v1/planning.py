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
from openclaw_core.logger import get_logger

logger = get_logger("openclaw.api.planning")

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
            plan_id=plan.id,
            plan_markdown=result["plan_markdown"],
            tasks=tasks
        )
    except Exception as e:
        import traceback
        import os
        error_detail = str(e)
        error_traceback = traceback.format_exc()
        
        # 检查是否是 API Key 未配置的问题
        api_key_configured = bool(os.getenv('QWEN_API_KEY') or os.getenv('MINIMAX_API_KEY'))
        if not api_key_configured:
            error_detail = "LLM API Key 未配置。请设置环境变量 QWEN_API_KEY 或 MINIMAX_API_KEY。"
            logger.error(f"Planning failed: {error_detail}")
        else:
            logger.error(f"Planning failed: {error_detail}\n{error_traceback}")
        
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


@router.get("/{case_id}/plan", response_model=PlanningResponseOut)
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
    tasks = []
    db_tasks = case_manager.get_tasks(case_id)
    
    for task in db_tasks:
        # 解析 related_files（可能是 JSON 字符串）
        related_files = []
        if task.related_files:
            try:
                related_files = json.loads(task.related_files)
            except (json.JSONDecodeError, TypeError):
                # 如果不是 JSON，尝试作为列表处理
                if isinstance(task.related_files, list):
                    related_files = task.related_files
                elif isinstance(task.related_files, str):
                    # 尝试按逗号分割
                    related_files = [f.strip() for f in task.related_files.split(",") if f.strip()]
        
        tasks.append(TaskOut(
            id=task.id,
            title=task.title,
            description=task.description or "",
            related_files=related_files,
            risk_level=task.risk_level or "medium",
            status=task.status or "pending"
        ))
    
    plan = plan_data.get("plan")
    return PlanningResponseOut(
        plan_id=plan.id if plan else "",
        plan_markdown=plan_data.get("markdown", ""),
        tasks=tasks
    )


@router.put("/{case_id}/plan")
async def update_plan(
    case_id: str,
    request: dict,
    case_manager: CaseManager = Depends(get_case_manager),
):
    """更新计划内容"""
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    plan_markdown = request.get("plan_markdown", "")
    if not plan_markdown:
        raise HTTPException(status_code=400, detail="plan_markdown is required")
    
    # 更新计划文件
    plan_data = case_manager.get_plan(case_id)
    if plan_data:
        plan = plan_data.get("plan")
        if plan:
            # 更新计划 markdown
            case_storage = case_manager.storage
            case_storage.save_plan_markdown(case_id, plan_markdown)
            
            return {"message": "Plan updated successfully"}
    
    raise HTTPException(status_code=404, detail="Plan not found")


@router.put("/{case_id}/tasks/{task_id}/status")
async def update_task_status(
    case_id: str,
    task_id: str,
    request: dict,
    case_manager: CaseManager = Depends(get_case_manager),
):
    """更新任务状态"""
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    status = request.get("status")
    if status not in ["pending", "completed"]:
        raise HTTPException(status_code=400, detail="status must be 'pending' or 'completed'")
    
    # 更新任务状态
    case_manager.update_task_status(task_id, status)
    
    return {"message": "Task status updated successfully"}
