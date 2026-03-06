"""
编码 API

提供生成代码补丁的接口。
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pathlib import Path

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.models import CodingRequestIn, CodingResponseOut, PatchMeta
from openclaw_studio.api.dependencies import get_case_manager, get_coding_agent
from openclaw_core.agents import CodingAgent
from openclaw_core.logger import get_logger

logger = get_logger("openclaw.api.coding")

router = APIRouter(prefix="/cases", tags=["Coding"])


@router.post("/{case_id}/tasks/{task_id}/code", response_model=CodingResponseOut)
async def generate_code(
    case_id: str,
    task_id: str,
    request: CodingRequestIn,
    case_manager: CaseManager = Depends(get_case_manager),
    agent: CodingAgent = Depends(get_coding_agent),
):
    """为任务生成代码补丁"""
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    task = case_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        # 检查案例状态，如果是 planning，则更新为 coding
        if case.status == "planning":
            case_manager.update_case_status(case_id, "coding")
        
        # 构建 CodingRequest
        coding_request = {
            "task": {
                "id": task_id,
                "title": request.task_title,
                "description": request.task_description,
                "related_files": request.related_files,
            }
        }
        
        # 调用 CodingAgent
        result = await agent.generate_code(coding_request)
        
        # 保存补丁
        for patch in result["patches"]:
            case_manager.save_patch(
                case_id=case_id,
                task_id=task_id,
                patch_content=patch["diff"],
                description=patch.get("description", ""),
            )
        
        # 更新任务状态
        case_manager.update_task_status(task_id, "completed")
        
        # 检查是否所有任务都已完成，如果是则更新案例状态为 completed
        all_tasks = case_manager.get_tasks(case_id)
        if all_tasks and all(task.status == "completed" for task in all_tasks):
            case_manager.update_case_status(case_id, "completed")
        
        # 记录 Agent 调用
        case_manager.record_agent_run(
            case_id=case_id,
            agent_type="coding",
            task_id=task_id,
            input_data=coding_request,
            output_data={"patches_count": len(result["patches"])},
            model=agent.llm_router.select_model("coding"),
        )
        
        # 转换补丁格式
        patches = [
            PatchMeta(
                file_path=patch.get("file_path", ""),
                diff=patch.get("diff", ""),
                description=patch.get("description", "")
            )
            for patch in result["patches"]
        ]
        
        return CodingResponseOut(patches=patches)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")


@router.get("/{case_id}/patches", response_model=List[PatchMeta])
async def get_patches(
    case_id: str,
    case_manager: CaseManager = Depends(get_case_manager),
):
    """获取案例的所有补丁"""
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    patches_info = case_manager.get_patches(case_id)
    patches = []
    
    for patch_info in patches_info:
        task_id = patch_info.get("task_id", "")
        if not task_id:
            continue
            
        patch_content = case_manager.storage.load_patch(case_id, task_id)
        if patch_content:
            # 从文件路径中提取实际的文件路径（如果补丁是 diff 格式）
            file_path = patch_info.get("file_path", "")
            # 如果 file_path 是完整路径，提取相对路径
            if file_path and "cases" in file_path:
                # 尝试从补丁内容中提取文件路径
                import re
                diff_match = re.search(r"diff --git a/(.+?) b/", patch_content)
                if diff_match:
                    file_path = diff_match.group(1)
            
            # 添加补丁元数据
            patch_meta = PatchMeta(
                file_path=file_path or f"patches/{task_id}.patch",
                diff=patch_content,
                description=patch_info.get("description", "")
            )
            # 为前端添加额外字段（通过 dict 扩展）
            patch_dict = patch_meta.model_dump()
            patch_dict['id'] = task_id
            patch_dict['task_id'] = task_id
            patch_dict['content'] = patch_content
            patch_dict['created_at'] = patch_info.get('created_at', '')
            patches.append(patch_dict)
    
    return patches


@router.patch("/{case_id}/patches/{patch_id}/apply")
async def apply_patch(
    case_id: str,
    patch_id: str,
    commit: bool = Query(False, description="是否提交到 Git"),
    commit_message: Optional[str] = Query(None, description="提交信息"),
    case_manager: CaseManager = Depends(get_case_manager),
):
    """
    应用补丁到代码库
    
    Args:
        case_id: 案例 ID
        patch_id: 补丁 ID（通常是 task_id）
        commit: 是否提交到 Git
        commit_message: 提交信息（如果 commit=True）
    """
    from openclaw_core.patch_applier import PatchApplier, PatchApplyResult
    from openclaw_studio.api.v1.git import get_git_tools
    
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # 加载补丁内容
    patch_content = case_manager.storage.load_patch(case_id, patch_id)
    if not patch_content:
        raise HTTPException(status_code=404, detail="Patch not found")
    
    # 获取 Git 工具（如果案例关联了仓库）
    git_tools = None
    if case.repo_path:
        try:
            git_tools = get_git_tools(case_id, case_manager)
        except Exception as e:
            logger.warning(f"无法初始化 Git 工具: {e}")
    
    # 创建补丁应用器
    if git_tools:
        applier = PatchApplier(git_tools=git_tools)
    elif case.repo_path:
        applier = PatchApplier(repo_path=case.repo_path)
    else:
        # 如果没有关联仓库，使用项目根目录
        import os
        repo_path = os.getcwd()
        applier = PatchApplier(repo_path=repo_path)
    
    try:
        if commit and git_tools:
            # 应用并提交到 Git
            if not commit_message:
                task = case_manager.get_task(patch_id)
                commit_message = f"Apply patch: {task.title if task else patch_id}"
            
            result, message, details = applier.apply_patch_with_git(
                patch_content=patch_content,
                commit_message=commit_message,
                dry_run=False
            )
        else:
            # 只应用补丁，不提交
            result, message, details = applier.apply_patch(
                patch_content=patch_content,
                dry_run=False
            )
        
        if result == PatchApplyResult.SUCCESS:
            # 更新补丁状态（如果数据库支持）
            # 这里可以添加数据库更新逻辑
            
            return {
                "message": message,
                "patch_id": patch_id,
                "result": "success",
                "details": details
            }
        elif result == PatchApplyResult.CONFLICT:
            raise HTTPException(
                status_code=409,
                detail={
                    "message": message,
                    "result": "conflict",
                    "details": details
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": message,
                    "result": "error",
                    "details": details
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"应用补丁失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"应用补丁失败: {str(e)}")
