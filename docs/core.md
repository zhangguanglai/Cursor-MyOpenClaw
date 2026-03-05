### OpenClaw 核心定位与技术栈（确认版）

> 说明：本节对应待办 `clarify-openclaw-core`，已根据你的选择更新为确认版：  
> - 主力语言：Python 3.11+（A1）  
> - 服务形态：本地 CLI + 轻量 Web 控制台（B1）  
> - 数据存储：SQLite 起步，后续再抽象（C1）  
> - 基础设施：GitHub 仓库（[zhangguanglai/Causor-MyOpenClaw](https://github.com/zhangguanglai/Causor-MyOpenClaw)），CI 使用 GitHub Actions

---

### 1. OpenClaw 在系统中的定位（确认版草案）

- **系统角色**：作为「AI 原生研发平台内核」：
  - 负责多 Agent 编排：任务拆解、子任务分配、工具调用、上下文管理。
  - 负责多模型路由：对接 Qwen、MiniMax、以及其他 OpenAI 兼容模型。
  - 负责与外部研发环境对接：Git 仓库、Cursor、CI/CD、Issue/PR 系统等。
- **不直接负责的部分（由上层产品承担）**：
  - 具体业务域逻辑（如特定 SaaS 产品的领域模型）。
  - 终端 UI：Web 控制台、VS Code/Cursor 插件、CLI 等。

---

### 2. 技术栈与运行时（已确认）

#### 2.1 后端语言与运行环境

- **已确认方案**：Python 3.11+
  - 生态丰富，适合快速实验 Agent/工具链。
  - 与多数 LLM SDK（Qwen/MiniMax/OpenAI 等）都有成熟支持。
  - 社区在「Agent 编排框架」和「工作流引擎」方面有大量可复用经验。
  - 后续如需要，可在保持协议一致的前提下增加 TypeScript/Go 实现。

#### 2.2 服务形态

- **短期（个人阶段，已确认 B1）**：本地/单机服务 + CLI/简单 Web 控制台
  - 以命令行或轻量 HTTP API 形式运行，方便与 Cursor/本地 Git 协作。
  - 优先保证「易迭代、好调试」，不追求复杂分布式架构。
- **中期（小团队阶段）**：拆分为几个逻辑模块服务
  - `openclaw-core`（Agent 编排 + LLMRouter）
  - `workspace-adapter`（对接 Git/Cursor/文件系统）
  - `ci-integration`（对接 CI/CD 与测试环境，优先支持 GitHub Actions）

---

### 3. 基础依赖与第三方组件（建议）

- **LLM 接入层**：
  - OpenAI 兼容接口客户端（统一封装 Qwen/MiniMax 等）。
  - HTTP 客户端：`httpx` / `requests`（Python）或 `axios`（TS）。
- **数据与状态存储（已确认 C1）**：
  - 初期：本地文件 + 轻量 SQLite，存储：
    - 规划文档（Plan）、执行记录、Agent 调用日志。
    - 任务与会话上下文（方便回溯与分析）。
  - 中期：可抽象成仓库接口，平滑切换到 Postgres 等（不影响上层 Agent 设计）。
- **任务编排/队列（可选，按复杂度逐步引入）**：
  - 初期：同步调用 + 简单异步（线程/协程）。
  - 中期：如有需要，可接入 Celery / RQ / 基于消息队列的方案。

---

### 4. 与代码空间/工具链的集成方式（初稿）

- **本地 Git 仓库 + Cursor**：
  - 通过文件系统 API 直接读写代码文件。
  - 通过 Git 命令/库获取 diff、提交记录。
  - 在 Cursor 中以「智能改动建议 + Patch」形式由你人工应用。
- **CI/CD 集成（已确认：GitHub + GitHub Actions）**：
  - 提供 Hook 或 API，供 GitHub Actions 在特定阶段调用 OpenClaw 的 TestAgent。
  - 记录测试结果、日志，回写到 Plan/案例库中。

---

### 5. 当前确认结论小结

- 主力实现语言：**Python 3.11+**。  
- 服务形态：**本地 CLI + 轻量 Web 控制台**，优先确保易迭代与好调试。  
- 数据与状态：**SQLite + 本地文件系统起步**，中长期可平滑迁移到 Postgres 等。  
- Git 托管与 CI：**GitHub 仓库 + GitHub Actions**，OpenClaw 后续会为 TestAgent 与 CI 的集成预留标准接口。


