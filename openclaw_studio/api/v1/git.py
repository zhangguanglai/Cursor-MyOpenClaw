"""
Git 集成 API

提供 Git 相关的 API 端点，支持：
- 获取 Git 状态
- 获取代码差异
- 获取分支列表
- 创建分支（可选）
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pathlib import Path

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.api.dependencies import get_case_manager
from openclaw_core.git_tools import GitTools
from openclaw_core.logger import get_logger

logger = get_logger("openclaw.api.git")

router = APIRouter(prefix="/cases", tags=["Git"])


def get_git_tools(case_id: str, case_manager: CaseManager) -> Optional[GitTools]:
    """获取案例关联的 GitTools 实例"""
    case = case_manager.get_case(case_id)
    if not case:
        return None
    
    repo_path = case.repo_path
    if not repo_path:
        return None
    
    # 如果 repo_path 是相对路径，尝试解析
    repo_path_obj = Path(repo_path)
    if not repo_path_obj.is_absolute():
        # 尝试相对于项目根目录
        project_root = Path(__file__).parent.parent.parent.parent
        repo_path_obj = project_root / repo_path
    
    try:
        return GitTools(str(repo_path_obj))
    except Exception as e:
        logger.warning(f"无法初始化 GitTools: {e}")
        return None


@router.get("/{case_id}/git-status")
async def get_git_status(
    case_id: str,
    case_manager: CaseManager = Depends(get_case_manager),
):
    """获取案例关联仓库的 Git 状态"""
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    git_tools = get_git_tools(case_id, case_manager)
    if not git_tools:
        raise HTTPException(
            status_code=400,
            detail="Case does not have a valid Git repository associated"
        )
    
    try:
        status = git_tools.get_status()
        repo_info = git_tools.get_repo_info()
        
        # 构建标准化的 GitStatusOut 格式
        return {
            "case_id": case_id,
            "repo_path": str(git_tools.repo_path),
            "current_branch": repo_info.get("current_branch", "unknown"),
            "remote_url": repo_info.get("remote_url"),
            "staged_files": status.get("staged_files", []),
            "unstaged_files": status.get("unstaged_files", []),
            "untracked_files": status.get("untracked_files", []),
        }
    except Exception as e:
        logger.error(f"获取 Git 状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get git status: {str(e)}")


@router.get("/{case_id}/git-diff")
async def get_git_diff(
    case_id: str,
    base: Optional[str] = None,
    head: Optional[str] = None,
    file_path: Optional[str] = None,
    case_manager: CaseManager = Depends(get_case_manager),
):
    """获取案例关联仓库的代码差异"""
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    git_tools = get_git_tools(case_id, case_manager)
    if not git_tools:
        raise HTTPException(
            status_code=400,
            detail="Case does not have a valid Git repository associated"
        )
    
    try:
        diff = git_tools.get_diff(base=base, head=head, file_path=file_path)
        return {
            "case_id": case_id,
            "base": base or "HEAD",
            "head": head or "working directory",
            "file_path": file_path,
            "diff": diff,
        }
    except Exception as e:
        logger.error(f"获取 Git diff 失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get git diff: {str(e)}")


@router.get("/{case_id}/git-branches")
async def get_git_branches(
    case_id: str,
    remote: bool = False,
    case_manager: CaseManager = Depends(get_case_manager),
):
    """获取案例关联仓库的分支列表"""
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    git_tools = get_git_tools(case_id, case_manager)
    if not git_tools:
        raise HTTPException(
            status_code=400,
            detail="Case does not have a valid Git repository associated"
        )
    
    try:
        branches = git_tools.get_branches(remote=remote)
        current_branch = git_tools.get_current_branch()
        
        return {
            "case_id": case_id,
            "current_branch": current_branch,
            "branches": branches,
            "remote": remote,
        }
    except Exception as e:
        logger.error(f"获取分支列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get branches: {str(e)}")


@router.post("/{case_id}/git-branches")
async def create_branch(
    case_id: str,
    branch_name: str,
    checkout: bool = True,
    case_manager: CaseManager = Depends(get_case_manager),
):
    """为案例关联仓库创建新分支"""
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    git_tools = get_git_tools(case_id, case_manager)
    if not git_tools:
        raise HTTPException(
            status_code=400,
            detail="Case does not have a valid Git repository associated"
        )
    
    try:
        success = git_tools.create_branch(branch_name, checkout=checkout)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create branch")
        
        return {
            "case_id": case_id,
            "branch_name": branch_name,
            "checkout": checkout,
            "current_branch": git_tools.get_current_branch() if checkout else None,
            "message": f"Branch '{branch_name}' created successfully",
        }
    except Exception as e:
        logger.error(f"创建分支失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create branch: {str(e)}")


@router.get("/{case_id}/git-commits")
async def get_git_commits(
    case_id: str,
    limit: int = 10,
    branch: Optional[str] = None,
    case_manager: CaseManager = Depends(get_case_manager),
):
    """获取案例关联仓库的提交历史"""
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    git_tools = get_git_tools(case_id, case_manager)
    if not git_tools:
        raise HTTPException(
            status_code=400,
            detail="Case does not have a valid Git repository associated"
        )
    
    try:
        commits = git_tools.get_commit_history(limit=limit, branch=branch)
        return {
            "case_id": case_id,
            "branch": branch or git_tools.get_current_branch(),
            "limit": limit,
            "commits": commits,
        }
    except Exception as e:
        logger.error(f"获取提交历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get commits: {str(e)}")
