"""
API 测试

使用 FastAPI TestClient 测试 API 端点。
"""

import pytest
from fastapi.testclient import TestClient

from openclaw_studio.api.main import app

client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "OpenClaw Studio API"


def test_create_case():
    """测试创建案例"""
    response = client.post(
        "/api/v1/cases/",
        json={
            "title": "Test Case",
            "description": "A test case for API testing",
            "repo_path": ".",
            "branch": "main"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Case"
    assert data["id"].startswith("case-")


def test_get_case():
    """测试获取案例"""
    # 先创建一个案例
    create_response = client.post(
        "/api/v1/cases/",
        json={
            "title": "Test Case for Get",
            "description": "Test description"
        }
    )
    assert create_response.status_code == 200
    case_id = create_response.json()["id"]
    
    # 获取案例
    response = client.get(f"/api/v1/cases/{case_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == case_id
    assert data["title"] == "Test Case for Get"


def test_list_cases():
    """测试列出所有案例"""
    response = client.get("/api/v1/cases/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_case_not_found():
    """测试获取不存在的案例"""
    response = client.get("/api/v1/cases/non-existent-case")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_case_history():
    """测试获取案例历史"""
    # 先创建一个案例
    create_response = client.post(
        "/api/v1/cases/",
        json={
            "title": "Test Case for History",
            "description": "Test description"
        }
    )
    assert create_response.status_code == 200
    case_id = create_response.json()["id"]
    
    # 获取历史
    response = client.get(f"/api/v1/cases/{case_id}/history")
    assert response.status_code == 200
    data = response.json()
    assert "case" in data
    assert "history" in data
    assert isinstance(data["history"], list)
