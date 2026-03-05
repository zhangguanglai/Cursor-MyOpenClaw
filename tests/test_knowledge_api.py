"""
知识库 API 测试
"""

import pytest
from fastapi.testclient import TestClient
from openclaw_studio.api.main import app

client = TestClient(app)


def test_search_knowledge():
    """测试搜索知识库"""
    response = client.get("/api/v1/knowledge/search?q=Python")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data
    assert isinstance(data["results"], list)


def test_search_by_category():
    """测试按类别搜索"""
    response = client.get("/api/v1/knowledge/search?q=code&category=rules")
    assert response.status_code == 200
    data = response.json()
    assert all(item["category"] == "rules" for item in data["results"])


def test_list_templates():
    """测试列出模板"""
    response = client.get("/api/v1/knowledge/templates")
    assert response.status_code == 200
    templates = response.json()
    assert isinstance(templates, list)
    assert "case_template" in templates


def test_get_template():
    """测试获取模板"""
    response = client.get("/api/v1/knowledge/templates/case_template")
    assert response.status_code == 200
    data = response.json()
    assert "template_name" in data
    assert "content" in data
    assert data["template_name"] == "case_template"


def test_get_template_not_found():
    """测试获取不存在的模板"""
    response = client.get("/api/v1/knowledge/templates/nonexistent")
    assert response.status_code == 404


def test_list_items():
    """测试列出知识库项"""
    response = client.get("/api/v1/knowledge/items")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)


def test_list_items_by_category():
    """测试按类别列出知识库项"""
    response = client.get("/api/v1/knowledge/items?category=rules")
    assert response.status_code == 200
    items = response.json()
    assert all(item["category"] == "rules" for item in items)
