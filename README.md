OpenClaw Core（基于 OpenClaw 的 AI 原生研发内核）
=========================================

**GitHub 仓库**：https://github.com/zhangguanglai/Causor-MyOpenClaw

本仓库用于实现「OpenClaw Core」及其周边能力，包括：

- 多模型统一路由层：`LLMRouter`（Qwen / MiniMax 等，基于 Python 3.11+）
- 核心 Agent：PlanningAgent / CodingAgent / TestAgent
- OpenClaw Studio MVP（本地 CLI + 轻量 Web 控制台）
- 与 GitHub Actions 的 CI 集成

当前重点是：

- 先以文档形式固化架构与流程（见 `docs/`）
- 配置基础 CI（GitHub Actions + Python 3.11 + pytest）
- 逐步补齐 `openclaw_core` 代码与测试

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 API Key

设置环境变量（至少配置一个）：

```bash
# Windows PowerShell
$env:QWEN_API_KEY="your_qwen_api_key"
$env:MINIMAX_API_KEY="your_minimax_api_key"

# Linux/Mac
export QWEN_API_KEY="your_qwen_api_key"
export MINIMAX_API_KEY="your_minimax_api_key"
```

### 使用示例

```python
import asyncio
from openclaw_core.llm_router import LLMRouter, LLMMessage

async def main():
    router = LLMRouter()
    messages: list[LLMMessage] = [
        {"role": "user", "content": "你好"}
    ]
    response = await router.complete_chat(messages, task_type="summary")
    print(response["content"])

asyncio.run(main())
```

更多示例请参考：
- `examples/llm_router_example.py` - LLMRouter 使用示例
- `examples/agents_example.py` - Agent 使用示例

### 运行测试

```bash
pytest
```

## 核心功能

### 1. LLMRouter - 多模型统一路由

统一的多模型路由层，支持 Qwen、MiniMax 等 OpenAI 兼容模型。

```python
from openclaw_core.llm_router import LLMRouter, LLMMessage

router = LLMRouter()
messages = [{"role": "user", "content": "你好"}]
response = await router.complete_chat(messages, task_type="summary")
```

### 2. PlanningAgent - 规划 Agent

从需求生成实现计划，拆解为可执行的子任务。

```python
from openclaw_core.agents import PlanningAgent, PlanningRequest

agent = PlanningAgent(router)
request: PlanningRequest = {
    "requirement_description": "实现用户登录功能",
    "constraints": ["必须兼容现有 API"],
}
response = await agent.generate_plan(request)
```

### 3. CodingAgent - 编码 Agent

根据任务生成代码修改建议和补丁。

```python
from openclaw_core.agents import CodingAgent, CodingRequest

agent = CodingAgent(router)
request: CodingRequest = {
    "task": {
        "id": "task-1",
        "title": "添加参数校验",
        "related_files": ["src/main.py"],
    },
}
response = await agent.generate_code(request)
```

### 4. TestAgent - 测试 Agent

分析代码改动并生成测试建议和验收清单。

```python
from openclaw_core.agents import TestAgent, TestAgentRequest

agent = TestAgent(router)
request: TestAgentRequest = {
    "changes": [{"file_path": "src/main.py", "diff": "..."}],
}
response = await agent.analyze_changes(request)
```

## 项目结构

```
.
├── openclaw_core/          # 核心代码
│   ├── llm_router.py      # LLMRouter 实现
│   ├── agents.py          # Agent 实现（Planning/Coding/Test）
│   ├── tools.py           # Agent 工具集（代码读取/搜索）
│   └── config.py           # 配置加载
├── config/                 # 配置文件
│   └── llm.yml            # LLM 配置
├── tests/                  # 测试代码
│   ├── test_llm_router.py
│   └── test_agents.py
├── examples/               # 使用示例
│   ├── llm_router_example.py
│   └── agents_example.py
└── docs/                   # 设计文档
```

## 详细设计文档

- `docs/core.md`：核心定位与技术栈（确认版）
- `docs/llm_router.md`：LLMRouter 设计与多模型配置方案
- `docs/agents.md`：核心 Agent 定义
- `docs/workflow.md`：单人阶段 AI 原生研发流程
- `docs/mvp_studio.md`：OpenClaw Studio MVP 架构与数据流
- `docs/org_playbook.md`：从 1 人到 5 人的组织与协作 Playbook

