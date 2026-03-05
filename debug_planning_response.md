根据你的项目结构和需求（**添加一个简单的日志功能，记录用户操作**），我们可以快速定位到已有日志相关模块，并进行增强。以下是完整的、可执行的实施方案：

---

## ✅ 一、现状分析

从项目结构中可以看到：
- `config/logger.yml`：日志配置文件（存在）
- `openclaw_core/logger.py`：日志核心模块（存在）
- `logs/openclaw.log`：日志输出目录与默认文件（已存在）
- `tests/test_logger.py`：已有测试（说明日志模块已被设计）

因此，**日志基础框架已存在**，我们只需：
1. 确保 `logger.py` 支持「用户操作」级别日志（如 `INFO` 或自定义 `USER_OP` 级别）
2. 在关键用户触发点（如 API 调用、CLI 命令、前端交互后端处理）插入日志语句
3. （可选）统一日志格式，包含 `user_id` / `case_id` / `action` / `timestamp` 等上下文

---

## ✅ 二、推荐实现方案（轻量、低侵入、符合现有架构）

### 🔹 步骤 1：确认并增强 `openclaw_core/logger.py`

查看该文件内容（若为空或仅基础配置，需补充）：

✅ **目标：提供一个全局可调用的 `log_user_action()` 工具函数**

```python
# openclaw_core/logger.py
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any

# 初始化 logger（复用 config/logger.yml）
def setup_logger():
    import yaml
    from logging.config import dictConfig

    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "logger.yml")
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = yaml.safe_load(f)
        dictConfig(config)
    else:
        # fallback
        logging.basicConfig(level=logging.INFO)

def get_logger(name: str = "openclaw"):
    return logging.getLogger(name)

# 👇 新增：专门记录用户操作的日志方法
def log_user_action(
    action: str,
    user_id: Optional[str] = None,
    case_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
):
    """
    记录用户操作行为，自动附加时间、上下文等元信息。
    示例：log_user_action("create_case", user_id="u-123", case_id="case-abc")
    """
    logger = get_logger("user_action")
    context = {
        "action": action,
        "user_id": user_id or "unknown",
        "case_id": case_id or "none",
        "timestamp": datetime.now().isoformat(),
        **(extra or {}),
    }
    logger.info(f"USER_ACTION: {context}")
```

> 💡 提示：确保 `config/logger.yml` 中已定义名为 `user_action` 的 logger（见下方模板）

---

### 🔹 步骤 2：更新 `config/logger.yml`（补全 `user_action` logger）

```yaml
# config/logger.yml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
  detailed:
    format: "%(asctime)s | %(levelname)-8s | %(name)-12s | %(funcName)-15s | %(message)s"

handlers:
  file:
    class: logging.handlers.RotatingFileHandler
    level: INFO
    formatter: detailed
    filename: ../logs/openclaw.log
    maxBytes: 10485760  # 10MB
    backupCount: 5
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout

loggers:
  openclaw:
    level: INFO
    handlers: [console, file]
    propagate: false

  user_action:  # 👈 新增：专用于用户操作日志
    level: INFO
    handlers: [console, file]
    propagate: false

root:
  level: WARNING
  handlers: [console]
```

---

### 🔹 步骤 3：在关键入口处调用 `log_user_action`

| 模块 | 文件 | 插入位置示例 | 日志建议 |
|------|------|----------------|-----------|
| ✅ CLI 用户操作 | `openclaw_cli/cli.py` | `@click.command()` 函数内 | `log_user_action("cli_run", user_id="cli", extra={"command": ctx.invoked_subcommand})` |
| ✅ Web API（用户触发） | `openclaw_studio/api/v1/cases.py`, `/planning`, `/coding`, `/testing` 等路由 | 每个 `POST/PUT` handler 开头 | `log_user_action("start_planning", user_id="web", case_id=case_id)` |
| ✅ 前端服务调用（可选） | `openclaw_studio/case_manager.py` 中 `create_case`, `update_case_status` 等方法 | 方法开头 | `log_user_action("update_case_status", case_id=case_id, status=new_status)` |

📌 **最小可行插入示例（API 创建用例）**：
```python
# openclaw_studio/api/v1/cases.py
from openclaw_core.logger import log_user_action

@app.post("/cases")
def create_case(...):
    log_user_action("create_case", user_id="web", case_id=new_case.id)
    ...
```

---

### 🔹 步骤 4：验证 & 测试

✅ 添加简单单元测试（补充 `tests/test_logger.py`）：
```python
# tests/test_logger.py
from openclaw_core.logger import log_user_action, setup_logger

def test_log_user_action():
    setup_logger()
    log_user_action("test_action", user_id="test-u1", case_id="test-case-001")
    # 只需确保不抛异常；日志内容可通过捕获 handler 验证（进阶）
```

✅ 手动触发一次 CLI 或 API 请求，检查 `logs/openclaw.log` 是否出现类似：
```
2025-04-05 10:23:45,123 | INFO     | user_action  | log_user_action | USER_ACTION: {'action': 'create_case', 'user_id': 'web', 'case_id': 'case-3af5da41', 'timestamp': '2025-04-05T10:23:45.123456', ...}
```

---

## ✅ 三、交付物清单（你只需做这些）

| 文件 | 修改内容 | 说明 |
|--------|------------|------|
| `openclaw_core/logger.py` | ✅ 新增 `log_user_action()` 函数 | 核心日志工具 |
| `config/logger.yml` | ✅ 新增 `user_action` logger 配置 | 确保日志写入文件+控制台 |
| `openclaw_cli/cli.py` | ✅ 在主命令/子命令中调用 `log_user_action` | 覆盖 CLI 用户行为 |
| `openclaw_studio/api/v1/*.py` | ✅ 在关键 POST/PUT 接口开头添加日志 | 覆盖 Web 用户行为 |
| `tests/test_logger.py` | ✅ 补充简单测试 | 确保函数可用 |

> ⚠️ 不需要修改前端（`openclaw-studio-frontend`）——日志由后端统一记录。

---

## ✅ 四、后续可扩展（非本次必需）

- 🌐 增加 `user_id` 自动提取（如从 JWT token 或 session）
- 📊 日志结构化输出为 JSON（便于 ELK / Grafana 分析）
- 📁 按 `case_id` 分日志文件（`logs/cases/case-xxx.log`）
- 🚨 添加敏感操作审计级别（如 `log_user_action(..., level="AUDIT")`）

---

如需我为你 **直接生成所有修改后的代码片段（含 diff）** 或 **帮你一键 patch 这些文件**，请告诉我，我可以立即输出 `.patch` 文件或逐文件内容。

是否需要我：
- ✅ 生成 `openclaw_core/logger.py` 完整新版本？
- ✅ 生成 `config/logger.yml` 补全版？
- ✅ 给出 `openclaw_cli/cli.py` 和 `openclaw_studio/api/v1/cases.py` 的具体插入代码？
- ✅ 输出一个可运行的 `patch` 命令或 Git patch 文件？

欢迎随时指定 👇

```json
[
  {
    "id": "task-001",
    "title": "增强 logger.py：添加 log_user_action 工具函数",
    "description": "在 openclaw_core/logger.py 中实现支持上下文的用户操作日志记录函数",
    "estimated_steps": ["打开 logger.py", "导入 logging/datetime/yaml", "编写 log_user_action 函数", "确保 get_logger('user_action') 可用"],
    "related_files": ["openclaw_core/logger.py"],
    "risk_level": "low"
  },
  {
    "id": "task-002",
    "title": "更新 logger.yml 配置",
    "description": "在 config/logger.yml 中添加名为 'user_action' 的 logger 配置，复用 file/console handler",
    "estimated_steps": ["打开 config/logger.yml", "在 loggers: 下新增 user_action 配置", "验证 YAML 格式"],
    "related_files": ["config/logger.yml"],
    "risk_level": "low"
  },
  {
    "id": "task-003",
    "title": "在 CLI 入口注入用户操作日志",
    "description": "在 openclaw_cli/cli.py 主命令中调用 log_user_action，记录命令名和参数摘要",
    "estimated_steps": ["定位 @click.group 或 @click.command", "导入 log_user_action", "在 handler 开头插入日志"],
    "related_files": ["openclaw_cli/cli.py"],
    "risk_level": "medium"
  },
  {
    "id": "task-004",
    "title": "在 Web API 关键路由注入用户操作日志",
    "description": "在 openclaw_studio/api/v1/cases.py、planning.py 等 POST/PUT 接口中添加 log_user_action 调用",
    "estimated_steps": ["选择 2~3 个核心 API（如 /cases, /planning, /coding）", "在每个 handler 开头添加日志", "传入 case_id/user_id 上下文"],
    "related_files": ["openclaw_studio/api/v1/cases.py", "openclaw_studio/api/v1/planning.py", "openclaw_studio/api/v1/coding.py"],
    "risk_level": "medium"
  },
  {
    "id": "task-005",
    "title": "补充单元测试与日志验证",
    "description": "更新 tests/test_logger.py，验证 log_user_action 不崩溃；手动检查 logs/openclaw.log 输出",
    "estimated_steps": ["添加 test_log_user_action 函数", "运行 pytest tests/test_logger.py", "触发一次 CLI/API，检查日志文件"],
    "related_files": ["tests/test_logger.py", "logs/openclaw.log"],
    "risk_level": "low"
  }
]
```