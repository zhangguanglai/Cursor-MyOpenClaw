"""
LLMRouter - 统一的多模型路由层

提供统一的接口屏蔽不同 LLM 提供商的差异，支持 Qwen、MiniMax 等 OpenAI 兼容模型。
"""

import os
import logging
from typing import List, Dict, Any, Optional, Literal, TypedDict, NotRequired
import httpx
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

Role = Literal["system", "user", "assistant", "tool"]


class LLMMessage(TypedDict):
    """LLM 消息格式"""
    role: Role
    content: str
    tool_call_id: NotRequired[str]


class ToolDefinition(TypedDict):
    """工具定义（Function Calling）"""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema


class LLMRouterResponse(TypedDict):
    """LLMRouter 统一返回格式"""
    content: str
    tool_calls: NotRequired[List[Dict[str, Any]]]
    raw: Dict[str, Any]
    model: str
    usage: NotRequired[Dict[str, int]]  # prompt_tokens, completion_tokens, total_tokens


class OpenAICompatibleProvider:
    """OpenAI 兼容协议的 Provider 实现"""

    def __init__(self, base_url: str, api_key_env: str):
        """
        初始化 Provider

        Args:
            base_url: API 基础 URL（如 https://api.minimax.chat/v1）
            api_key_env: 环境变量名，用于读取 API Key
        """
        self.base_url = base_url.rstrip("/")
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise ValueError(f"环境变量 {api_key_env} 未设置，请先配置 API Key")
        self.api_key = api_key
        self.api_key_env = api_key_env

    async def complete_chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用聊天完成接口

        Args:
            payload: OpenAI 兼容格式的请求体

        Returns:
            API 返回的 JSON 响应

        Raises:
            httpx.HTTPStatusError: HTTP 错误
            httpx.RequestError: 网络错误
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        logger.debug(f"调用 LLM API: {url}, model={payload.get('model')}")

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"LLM API 调用失败: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"LLM API 网络错误: {e}")
                raise


class LLMRouter:
    """统一的多模型路由层"""

    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None):
        """
        初始化 LLMRouter

        Args:
            config_path: 配置文件路径（YAML 格式），默认查找 config/llm.yml
            config_dict: 直接传入配置字典（优先级高于 config_path）
        """
        if config_dict:
            self.config = config_dict
        elif config_path:
            self.config = self._load_config(config_path)
        else:
            # 默认查找 config/llm.yml
            default_path = Path(__file__).parent.parent / "config" / "llm.yml"
            if default_path.exists():
                self.config = self._load_config(str(default_path))
            else:
                raise FileNotFoundError(
                    f"未找到配置文件，请提供 config_path 或确保存在 {default_path}"
                )

        # 初始化 Provider
        self.providers: Dict[str, OpenAICompatibleProvider] = {}
        for provider_name, provider_config in self.config.get("providers", {}).items():
            if provider_config.get("type") == "openai-compatible":
                self.providers[provider_name] = OpenAICompatibleProvider(
                    base_url=provider_config["base_url"],
                    api_key_env=provider_config["api_key_env"],
                )
            else:
                logger.warning(f"未知的 Provider 类型: {provider_config.get('type')}")

    @staticmethod
    def _load_config(config_path: str) -> Dict[str, Any]:
        """加载 YAML 配置文件"""
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def select_model(self, task_type: str) -> str:
        """
        根据任务类型选择模型

        Args:
            task_type: 任务类型（planning/coding/summary）

        Returns:
            模型标识（格式：provider/model_name）
        """
        models_config = self.config.get("models", {})
        task_config = models_config.get(task_type)
        if not task_config:
            # 默认使用 summary 类型
            task_config = models_config.get("summary", {})
        return task_config.get("default", "")

    async def complete_chat(
        self,
        messages: List[LLMMessage],
        *,
        model: Optional[str] = None,
        task_type: Optional[str] = None,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> LLMRouterResponse:
        """
        统一的聊天完成接口

        Args:
            messages: 消息列表
            model: 模型标识（格式：provider/model_name），如果未提供则根据 task_type 选择
            task_type: 任务类型（planning/coding/summary），用于自动选择模型
            tools: 工具定义列表（Function Calling）
            tool_choice: 工具选择策略（"auto"/"none"/具体工具名）
            temperature: 温度参数
            max_tokens: 最大 token 数
            extra: 额外参数（透传给底层 API）

        Returns:
            统一的响应格式

        Raises:
            ValueError: 模型标识无效或 Provider 不存在
        """
        # 确定使用的模型
        if not model:
            if not task_type:
                raise ValueError("必须提供 model 或 task_type 参数")
            model = self.select_model(task_type)

        # 解析 provider 和 model_name
        if "/" not in model:
            raise ValueError(f"模型标识格式错误，应为 provider/model_name，实际: {model}")
        provider_name, provider_model = model.split("/", 1)

        # 获取 Provider
        if provider_name not in self.providers:
            raise ValueError(f"未知的 Provider: {provider_name}，可用: {list(self.providers.keys())}")
        provider = self.providers[provider_name]

        # 构建请求体
        payload: Dict[str, Any] = {
            "model": provider_model,
            "messages": messages,
            "temperature": temperature,
        }

        if tools:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        if extra:
            payload.update(extra)

        # 调用 Provider
        raw_response = await provider.complete_chat(payload)

        # 归一化响应格式
        return self._normalize_response(raw_response, model)

    @staticmethod
    def _normalize_response(raw_response: Dict[str, Any], model: str) -> LLMRouterResponse:
        """
        将不同 Provider 的响应归一化为统一格式

        Args:
            raw_response: Provider 返回的原始响应
            model: 使用的模型标识

        Returns:
            归一化后的响应
        """
        choices = raw_response.get("choices", [])
        if not choices:
            raise ValueError("API 返回的 choices 为空")

        choice = choices[0]
        message = choice.get("message", {})

        # 提取 content
        content = message.get("content", "")

        # 提取 tool_calls（如果存在）
        tool_calls = message.get("tool_calls")
        if tool_calls:
            tool_calls = [tc for tc in tool_calls]  # 保持原始格式

        # 提取 usage
        usage = raw_response.get("usage")

        return LLMRouterResponse(
            content=content,
            tool_calls=tool_calls if tool_calls else None,
            raw=raw_response,
            model=model,
            usage=usage,
        )
