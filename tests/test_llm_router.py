"""
LLMRouter 单元测试
"""

import pytest
import os
from typing import List
from unittest.mock import AsyncMock, patch, MagicMock
from openclaw_core.llm_router import (
    LLMRouter,
    OpenAICompatibleProvider,
    LLMMessage,
    LLMRouterResponse,
)


@pytest.fixture
def sample_config():
    """示例配置"""
    return {
        "providers": {
            "qwen": {
                "type": "openai-compatible",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "api_key_env": "QWEN_API_KEY",
            },
            "minimax": {
                "type": "openai-compatible",
                "base_url": "https://api.minimax.chat/v1",
                "api_key_env": "MINIMAX_API_KEY",
            },
        },
        "models": {
            "planning": {
                "default": "qwen/qwen-coder-plus",
                "candidates": ["qwen/qwen-coder-plus"],
            },
            "coding": {
                "default": "minimax/minimax-coder-2.5",
                "candidates": ["minimax/minimax-coder-2.5"],
            },
            "summary": {
                "default": "qwen/qwen-plus",
                "candidates": ["qwen/qwen-plus"],
            },
        },
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    """模拟环境变量"""
    monkeypatch.setenv("QWEN_API_KEY", "test_qwen_key")
    monkeypatch.setenv("MINIMAX_API_KEY", "test_minimax_key")


class TestOpenAICompatibleProvider:
    """测试 OpenAICompatibleProvider"""

    def test_init_success(self, mock_env_vars):
        """测试成功初始化"""
        provider = OpenAICompatibleProvider(
            base_url="https://api.test.com/v1",
            api_key_env="QWEN_API_KEY",
        )
        assert provider.base_url == "https://api.test.com/v1"
        assert provider.api_key == "test_qwen_key"

    def test_init_missing_api_key(self):
        """测试缺少 API Key 的情况"""
        with pytest.raises(ValueError, match="环境变量.*未设置"):
            OpenAICompatibleProvider(
                base_url="https://api.test.com/v1",
                api_key_env="NONEXISTENT_KEY",
            )

    @pytest.mark.asyncio
    async def test_complete_chat_success(self, mock_env_vars):
        """测试成功调用 API"""
        provider = OpenAICompatibleProvider(
            base_url="https://api.test.com/v1",
            api_key_env="QWEN_API_KEY",
        )

        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Hello, world!",
                        "role": "assistant",
                    }
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_response
            mock_resp.raise_for_status = MagicMock()
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_resp
            )

            result = await provider.complete_chat({"model": "test-model", "messages": []})
            assert result == mock_response


class TestLLMRouter:
    """测试 LLMRouter"""

    def test_init_with_config_dict(self, sample_config, mock_env_vars):
        """测试使用配置字典初始化"""
        router = LLMRouter(config_dict=sample_config)
        assert "qwen" in router.providers
        assert "minimax" in router.providers

    def test_select_model(self, sample_config, mock_env_vars):
        """测试模型选择"""
        router = LLMRouter(config_dict=sample_config)
        assert router.select_model("planning") == "qwen/qwen-coder-plus"
        assert router.select_model("coding") == "minimax/minimax-coder-2.5"
        assert router.select_model("summary") == "qwen/qwen-plus"
        # 未知类型应回退到 summary
        assert router.select_model("unknown") == "qwen/qwen-plus"

    @pytest.mark.asyncio
    async def test_complete_chat_with_model(self, sample_config, mock_env_vars):
        """测试使用指定模型调用"""
        router = LLMRouter(config_dict=sample_config)

        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Test response",
                        "role": "assistant",
                    }
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        with patch.object(
            router.providers["qwen"], "complete_chat", new_callable=AsyncMock
        ) as mock_provider:
            mock_provider.return_value = mock_response

            messages: List[LLMMessage] = [
                {"role": "user", "content": "Hello"}
            ]
            result = await router.complete_chat(messages, model="qwen/qwen-coder-plus")

            assert result["content"] == "Test response"
            assert result["model"] == "qwen/qwen-coder-plus"
            assert "raw" in result

    @pytest.mark.asyncio
    async def test_complete_chat_with_task_type(self, sample_config, mock_env_vars):
        """测试使用任务类型自动选择模型"""
        router = LLMRouter(config_dict=sample_config)

        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Planning response",
                        "role": "assistant",
                    }
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
        }

        with patch.object(
            router.providers["qwen"], "complete_chat", new_callable=AsyncMock
        ) as mock_provider:
            mock_provider.return_value = mock_response

            messages: List[LLMMessage] = [
                {"role": "user", "content": "Plan this feature"}
            ]
            result = await router.complete_chat(messages, task_type="planning")

            assert result["content"] == "Planning response"
            assert result["model"] == "qwen/qwen-coder-plus"

    def test_complete_chat_invalid_model(self, sample_config, mock_env_vars):
        """测试无效模型标识"""
        router = LLMRouter(config_dict=sample_config)
        messages: List[LLMMessage] = [{"role": "user", "content": "Hello"}]

        with pytest.raises(ValueError, match="模型标识格式错误"):
            import asyncio
            asyncio.run(router.complete_chat(messages, model="invalid-model"))

    def test_complete_chat_unknown_provider(self, sample_config, mock_env_vars):
        """测试未知 Provider"""
        router = LLMRouter(config_dict=sample_config)
        messages: List[LLMMessage] = [{"role": "user", "content": "Hello"}]

        with pytest.raises(ValueError, match="未知的 Provider"):
            import asyncio
            asyncio.run(router.complete_chat(messages, model="unknown/model"))
