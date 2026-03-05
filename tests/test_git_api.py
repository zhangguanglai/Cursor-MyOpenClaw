"""
Git API 测试
"""

import pytest
from fastapi.testclient import TestClient
from openclaw_studio.api.main import app
from openclaw_studio.case_manager import CaseManager

client = TestClient(app)


@pytest.fixture
def test_case():
    """创建测试案例"""
    case_manager = CaseManager()
    case = case_manager.create_case(
        title="Git Integration Test Case",
        description="Test case for Git integration",
        repo_path=".",
        branch="main"
    )
    yield case
    # 清理（可选）


def test_get_git_status(test_case):
    """测试获取 Git 状态"""
    response = client.get(f"/api/v1/cases/{test_case.id}/git-status")
    assert response.status_code == 200
    data = response.json()
    assert "case_id" in data
    assert "status" in data
    assert "repo_info" in data
    assert data["status"]["branch"] is not None


def test_get_git_branches(test_case):
    """测试获取分支列表"""
    response = client.get(f"/api/v1/cases/{test_case.id}/git-branches")
    assert response.status_code == 200
    data = response.json()
    assert "case_id" in data
    assert "branches" in data
    assert "current_branch" in data
    assert isinstance(data["branches"], list)


def test_get_git_diff(test_case):
    """测试获取 Git diff"""
    response = client.get(f"/api/v1/cases/{test_case.id}/git-diff")
    assert response.status_code == 200
    data = response.json()
    assert "case_id" in data
    assert "diff" in data


def test_get_git_commits(test_case):
    """测试获取提交历史"""
    response = client.get(f"/api/v1/cases/{test_case.id}/git-commits?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "case_id" in data
    assert "commits" in data
    assert isinstance(data["commits"], list)


def test_get_git_status_no_repo():
    """测试没有关联 Git 仓库的案例"""
    case_manager = CaseManager()
    case = case_manager.create_case(
        title="No Git Repo Case",
        description="Case without Git repo",
        repo_path=None,
        branch=None
    )
    
    response = client.get(f"/api/v1/cases/{case.id}/git-status")
    assert response.status_code == 400
    assert "valid Git repository" in response.json()["detail"]
