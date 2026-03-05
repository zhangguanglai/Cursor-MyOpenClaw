"""
编码 API

提供生成代码补丁的接口。
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.models import CodingRequestIn, CodingResponseOut, PatchMeta
from openclaw_studio.api.dependencies import get_case_manager, get_coding_agent
from openclaw_core.agents import CodingAgent

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
            
            patches.append(PatchMeta(
                file_path=file_path or f"patches/{task_id}.patch",
                diff=patch_content,
                description=patch_info.get("description", "")
            ))
    
    return patches
