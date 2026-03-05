"""
Agent 单元测试
"""

import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
from openclaw_core.agents import (
    PlanningAgent,
    CodingAgent,
    TestAgent,
    PlanningRequest,
    CodingRequest,
    TestAgentRequest,
)
from openclaw_core.llm_router import LLMRouter


@pytest.fixture
def mock_llm_router():
    """模拟 LLMRouter"""
    router = MagicMock(spec=LLMRouter)
    router.complete_chat = AsyncMock()
    return router


@pytest.fixture
def sample_llm_response():
    """示例 LLM 响应"""
    return {
        "content": """## 实现计划

### 概述
这是一个示例实现计划。

### 任务列表

1. **任务 1**: 实现基础功能
   - 步骤 1: 创建文件
   - 步骤 2: 实现函数
   - 风险: 低

2. **任务 2**: 添加测试
   - 步骤 1: 编写测试用例
   - 风险: 中

```json
[
  {
    "id": "task-1",
    "title": "实现基础功能",
    "description": "创建核心功能模块",
    "estimated_steps": ["创建文件", "实现函数"],
    "related_files": ["src/main.py"],
    "risk_level": "low"
  }
]
```""",
        "model": "qwen/qwen-coder-plus",
        "raw": {},
    }


class TestPlanningAgent:
    """测试 PlanningAgent"""

    @pytest.mark.asyncio
    async def test_generate_plan_basic(self, mock_llm_router, sample_llm_response):
        """测试基础规划生成"""
        mock_llm_router.complete_chat.return_value = sample_llm_response

        agent = PlanningAgent(mock_llm_router)
        request: PlanningRequest = {
            "requirement_description": "实现一个用户登录功能",
            "constraints": ["必须兼容现有 API"],
            "acceptance_criteria": ["功能可以通过测试验证"],
        }

        response = await agent.generate_plan(request)

        assert "plan_markdown" in response
        assert "tasks" in response
        assert isinstance(response["tasks"], list)
        assert mock_llm_router.complete_chat.called
        # 验证调用了 planning 任务类型
        call_args = mock_llm_router.complete_chat.call_args
        assert call_args.kwargs.get("task_type") == "planning"

    @pytest.mark.asyncio
    async def test_generate_plan_with_files(self, mock_llm_router, sample_llm_response):
        """测试带相关文件的规划"""
        mock_llm_router.complete_chat.return_value = sample_llm_response

        agent = PlanningAgent(mock_llm_router)
        request: PlanningRequest = {
            "requirement_description": "添加新功能",
            "related_files": ["openclaw_core/llm_router.py"],
        }

        response = await agent.generate_plan(request)
        assert response["plan_markdown"]


class TestCodingAgent:
    """测试 CodingAgent"""

    @pytest.mark.asyncio
    async def test_generate_code_basic(self, mock_llm_router):
        """测试基础代码生成"""
        mock_llm_router.complete_chat.return_value = {
            "content": """## 代码修改

### 修改说明
在函数中添加参数校验。

```diff
--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,5 @@
 def foo(x):
+    if x is None:
+        raise ValueError("x cannot be None")
     return x * 2
```

## 理由
增加输入验证，提高代码健壮性。

## 测试建议
- 测试 None 输入的情况
""",
            "model": "minimax/minimax-coder-2.5",
            "raw": {},
        }

        agent = CodingAgent(mock_llm_router)
        request: CodingRequest = {
            "task": {
                "id": "task-1",
                "title": "添加参数校验",
                "description": "在函数 foo 中添加 None 检查",
                "related_files": ["src/main.py"],
            },
        }

        response = await agent.generate_code(request)

        assert "patches" in response
        assert len(response["patches"]) > 0
        assert "rationale" in response
        assert "test_suggestions" in response
        assert mock_llm_router.complete_chat.called
        # 验证调用了 coding 任务类型
        call_args = mock_llm_router.complete_chat.call_args
        assert call_args.kwargs.get("task_type") == "coding"


class TestTestAgent:
    """测试 TestAgent"""

    @pytest.mark.asyncio
    async def test_analyze_changes(self, mock_llm_router):
        """测试改动分析"""
        mock_llm_router.complete_chat.return_value = {
            "content": """## 潜在问题

- 当输入为 None 时可能抛异常（严重程度: high）
- 缺少边界值检查（严重程度: medium）

## 测试用例

### test_foo_with_none
- 构造输入 None
- 调用函数 foo
- 断言抛出 ValueError

## 人工验收
- 通过接口测试验证功能正常
""",
            "model": "qwen/qwen-plus",
            "raw": {},
        }

        agent = TestAgent(mock_llm_router)
        request: TestAgentRequest = {
            "changes": [
                {
                    "file_path": "src/main.py",
                    "diff": "+def foo(x):\n+    return x * 2",
                }
            ],
        }

        response = await agent.analyze_changes(request)

        assert "potential_issues" in response
        assert "test_cases" in response
        assert "manual_checklist" in response
        assert mock_llm_router.complete_chat.called
        # 验证调用了 summary 任务类型
        call_args = mock_llm_router.complete_chat.call_args
        assert call_args.kwargs.get("task_type") == "summary"
