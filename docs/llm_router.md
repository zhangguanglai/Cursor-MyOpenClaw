### LLMRouter 统一接口与多模型配置方案（草案）

> 对应待办 `design-llm-router`。以下以「Python + OpenAI 兼容协议」为默认假设，你确认主力语言后，我们可以调整示例代码与实现细节。

---

### 1. 设计目标

- **统一调用入口**：屏蔽 Qwen、MiniMax 等不同厂商 SDK/域名/参数差异。
- **支持多模型策略**：根据任务类型（规划/编码/总结等）选择不同模型。
- **支持工具调用**：对上层 Agent 提供统一的 `tools`/function calling 能力。
- **可观测性**：便于记录每次调用的模型、token 用量与错误信息。

---

### 2. 抽象接口设计

#### 2.1 核心接口：`LLMRouter`

以 Python 伪代码为例（真实实现时可拆分到模块）：

```python
from typing import List, Dict, Any, Optional, Literal

Role = Literal["system", "user", "assistant", "tool"]

class LLMMessage(TypedDict):
    role: Role
    content: str
    tool_call_id: NotRequired[str]

class ToolDefinition(TypedDict):
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema

class LLMRouter:
    async def complete_chat(
        self,
        messages: List[LLMMessage],
        *,
        model: str,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[str] = None,  # "auto" | "none" | 具体工具名
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        extra: Optional[Dict[str, Any]] = None,  # 透传底层特定参数
    ) -> Dict[str, Any]:
        ...
```

> 关键点：**上层 Agent 只依赖 `LLMRouter.complete_chat` 这一抽象，不直接感知是 Qwen 还是 MiniMax。**

---

### 3. 多模型配置方案

#### 3.1 配置结构

建议使用一个统一的 YAML/JSON 配置，例如 `config/llm.yml`：

```yaml
providers:
  qwen:
    type: openai-compatible
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    api_key_env: "QWEN_API_KEY"
  minimax:
    type: openai-compatible
    base_url: "https://api.minimax.chat/v1"
    api_key_env: "MINIMAX_API_KEY"

models:
  planning:
    # 代码/需求规划任务
    default: "qwen/qwen-coder-plus"
    candidates:
      - "qwen/qwen-coder-plus"
      - "minimax/minimax-coder-2.5"
  coding:
    # 具体代码生成与重构
    default: "minimax/minimax-coder-2.5"
    candidates:
      - "minimax/minimax-coder-2.5"
      - "qwen/qwen-coder-plus"
  summary:
    # 报告、总结、说明文档
    default: "qwen/qwen-plus"
    candidates:
      - "qwen/qwen-plus"
```

这里采用 `provider/model_name` 的形式表达模型来源，便于在 `LLMRouter` 内部拆解。

#### 3.2 任务到模型的映射

在 Agent 层或一个简单的「策略模块」中，按任务类型选择模型：

```python
def select_model(task_type: str, config: Dict[str, Any]) -> str:
    group = config["models"].get(task_type)
    if not group:
        return config["models"]["summary"]["default"]
    return group["default"]
```

---

### 4. Provider 适配层

#### 4.1 OpenAI 兼容 Provider

大部分新一代 LLM（包括 Qwen、MiniMax 2.5）都提供 OpenAI 兼容协议，可以统一用一套 HTTP 客户端：

```python
import os
import httpx

class OpenAICompatibleProvider:
    def __init__(self, base_url: str, api_key_env: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ[api_key_env]

    async def complete_chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
        resp.raise_for_status()
        return resp.json()
```

#### 4.2 在 LLMRouter 中路由到 Provider

```python
class LLMRouter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = {
            "qwen": OpenAICompatibleProvider(
                base_url=config["providers"]["qwen"]["base_url"],
                api_key_env=config["providers"]["qwen"]["api_key_env"],
            ),
            "minimax": OpenAICompatibleProvider(
                base_url=config["providers"]["minimax"]["base_url"],
                api_key_env=config["providers"]["minimax"]["api_key_env"],
            ),
        }

    async def complete_chat(...):
        provider_name, provider_model = model.split("/", 1)
        provider = self.providers[provider_name]
        payload = {
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
        return await provider.complete_chat(payload)
```

---

### 5. 工具调用 / Function Calling 支持

#### 5.1 上层 Agent 使用方式

- 上层 Agent 定义工具列表（JSON Schema）。
- 调用 `LLMRouter.complete_chat(messages, model=..., tools=tools, tool_choice="auto")`。
- 解析返回结果中的 `tool_calls` 或相应字段，触发本地工具执行。

#### 5.2 统一返回格式建议

为便于跨 Provider 使用，建议在 Router 层做一次「归一化」：

```python
class LLMRouterResponse(TypedDict):
    content: str
    tool_calls: NotRequired[List[Dict[str, Any]]]
    raw: Dict[str, Any]
```

> 这样 Agent 只关心 `content` 和 `tool_calls`，同时保留 `raw` 方便调试。

---

### 6. 监控与限流（后续增强）

- 在 Router 内部增加：
  - 请求日志（模型名、耗时、token 用量）。
  - 简单重试与退避（429/5xx 时）。
  - 简单并发/速率限制（防止超额调用）。
- 后续可：
  - 接入 Prometheus/Grafana 做指标监控。
  - 加一层按任务/用户维度的配额控制。

---

### 7. 技术选型确认（已确认）

✅ **已确认**：本项目采用「OpenAI 兼容协议」作为所有 LLM 集成的基础。  
✅ **已确认**：默认支持 Qwen 和 MiniMax 2.5，通过环境变量配置 API Key。  
⚠️ **待定**：第一版是否支持「工具调用」（Function Calling）。建议先实现纯对话模式，工具调用作为后续增强功能。

---

### 8. 下一步实现计划

基于以上确认，下一步可以：
1. 实现 `openclaw_core/llm_router.py` 模块（Python 3.11+）
2. 实现 `config/llm.yml` 配置加载与解析
3. 编写对应的单元测试（`tests/test_llm_router.py`）
4. 提供使用示例（`examples/llm_router_example.py`）

