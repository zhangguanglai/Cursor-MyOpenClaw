"""
Cases API Endpoints

This module defines the API endpoints for managing cases.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.api.dependencies import get_case_manager

# Initialize the router
router = APIRouter(prefix="/cases", tags=["cases"])

# Pydantic models for request and response
class CaseCreate(BaseModel):
    title: str
    description: str
    repo_path: Optional[str] = None
    branch: Optional[str] = None

class CaseResponse(BaseModel):
    id: str
    title: str
    description: str
    repo_path: Optional[str]
    branch: Optional[str]
    status: str
    created_at: str
    updated_at: str

# Create a new case
@router.post("/", response_model=CaseResponse)
async def create_case(case: CaseCreate, case_manager: CaseManager = Depends(get_case_manager)):
    created_case = case_manager.create_case(
        title=case.title,
        description=case.description,
        repo_path=case.repo_path,
        branch=case.branch,
    )
    return CaseResponse(
        id=created_case.id,
        title=created_case.title,
        description=created_case.description or "",
        repo_path=created_case.repo_path,
        branch=created_case.branch,
        status=created_case.status,
        created_at=created_case.created_at,
        updated_at=created_case.updated_at
    )

# Get a specific case by ID
@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: str, case_manager: CaseManager = Depends(get_case_manager)):
    case = case_manager.get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseResponse(
        id=case.id,
        title=case.title,
        description=case.description or "",
        repo_path=case.repo_path,
        branch=case.branch,
        status=case.status,
        created_at=case.created_at,
        updated_at=case.updated_at
    )

# List all cases
@router.get("/", response_model=List[CaseResponse])
async def list_cases(case_manager: CaseManager = Depends(get_case_manager)):
    cases = case_manager.list_cases()
    return [
        CaseResponse(
            id=case.id,
            title=case.title,
            description=case.description or "",
            repo_path=case.repo_path,
            branch=case.branch,
            status=case.status,
            created_at=case.created_at,
            updated_at=case.updated_at
        )
        for case in cases
    ]

# Delete a case
@router.delete("/{case_id}")
async def delete_case(case_id: str, case_manager: CaseManager = Depends(get_case_manager)):
    """删除案例及其所有关联数据"""
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    success = case_manager.delete_case(case_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete case")
    
    return {"message": "Case deleted successfully", "case_id": case_id}
