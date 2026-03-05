"""健康检查端点测试"""

import pytest
from fastapi.testclient import TestClient

from openclaw_studio.api.main import app

client = TestClient(app)


def test_health_endpoint():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "OpenClaw Studio API"
    assert data["version"] == "0.1.0"


def test_root_endpoint():
    """测试根路径端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "OpenClaw Studio API"
    assert data["version"] == "0.1.0"
