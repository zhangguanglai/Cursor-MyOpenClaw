### OpenClaw Studio MVP 模块架构与数据流

> 对应待办 `mvp-architecture`。本设计聚焦于「面向你自己使用」的一版控制台 MVP，优先支持端到端跑通单人闭环。

---

### 1. 功能范围回顾（MVP）

- **需求输入与管理**：
  - 录入/查看需求（Feature/Issue/PR 描述）。
  - 将需求与本地 Git 仓库/分支关联。
- **规划视图**：
  - 调用 PlanningAgent 生成 `plan.md` + 子任务列表。
  - 支持人工编辑与确认计划。
- **执行视图**：
  - 按子任务调用 CodingAgent 生成 Patch 建议。
  - 在 UI 中查看 diff、选择性应用补丁（最终应用仍在 Cursor 中完成）。
- **测试视图**：
  - 调用 TestAgent 生成测试建议与验收清单。
  - 记录哪些测试已执行。
- **历史与知识库**：
  - 按需求查看完整闭环记录（需求 → 计划 → Patch → 测试 → 上线 → 总结）。

---

### 2. 模块划分（逻辑层）

#### 2.1 前端（Web UI）

- **模块**：
  - `RequirementCenterUI`：需求列表与详情页。
  - `PlanningView`：展示/编辑计划与子任务。
  - `ExecutionView`：展示子任务、Patch 列表与 diff。
  - `TestAndReviewView`：展示测试建议与验收清单。
  - `HistoryView`：按需求/时间轴浏览历史记录。
- **职责**：
  - 提供清晰的交互界面。
  - 通过 API 调用后端的 OpenClaw Core。

#### 2.2 后端（OpenClaw Studio API）

- **模块**：
  - `RequirementCenterAPI`：
    - CRUD：需求/Case。
    - 关联本地/远端 Git 仓库与分支。
  - `PlanController`：
    - 触发 PlanningAgent。
    - 读写 `plan.md` / `plan.json`。
  - `ExecutionController`：
    - 触发 CodingAgent。
    - 组织 Patch 建议，供前端展示。
  - `TestController`：
    - 触发 TestAgent。
    - 存储测试建议与验收记录。
  - `HistoryController`：
    - 聚合展示单个需求的全链路记录。

#### 2.3 核心（OpenClawCore）

- **模块**：
  - `LLMRouter`：多模型统一入口。
  - `PlanningAgent` / `CodingAgent` / `TestAgent`：见 `agents.md`。
  - `ToolHub`：
    - 代码读取工具（文件系统）。
    - 代码搜索工具（ripgrep 或等效）。
    - Git 工具（获取 diff/提交/分支信息）。
  - `ContextStore`：
    - 存储每次 Agent 调用的上下文与结果。

#### 2.4 存储层

- **Case & Plan 仓库**（可用 SQLite + 文件系统组合）：
  - 表结构示意：
    - `cases`：id, title, description, repo_path, branch, status, created_at, updated_at
    - `plans`：id, case_id, plan_md_path, plan_json_path
    - `tasks`：id, case_id, title, description, status, related_files(json)
    - `agent_runs`：id, case_id, agent_type, input_path, output_path, model, created_at
    - `test_records`：id, case_id, summary, details_path, created_at
  - 实际 Markdown 与 JSON 文件保存在：
    - `cases/<case_id>/plan.md`
    - `cases/<case_id>/plan.json`
    - `cases/<case_id>/verification.md`
    - `cases/<case_id>/summary.md`

---

### 3. 端到端数据流（示意）

#### 3.1 需求创建与绑定

1. 你在 UI 中创建一个需求：
   - 填写标题、描述、验收标准。
   - 选择本地仓库路径 + 目标分支。
2. `RequirementCenterAPI`：
   - 在数据库中创建 `case` 记录。
   - 在文件系统中创建 `cases/<case_id>/` 目录。

#### 3.2 生成实现计划（PlanningAgent 流程）

1. UI 中点击「生成计划」。
2. `PlanController`：
   - 聚合输入：
     - 需求描述（来自 `cases` 表）。
     - 项目结构（通过 ToolHub 扫描仓库）。
   - 调用 `PlanningAgent`：
     - `PlanningAgent` 通过 `LLMRouter` 调用模型（如 `planning` 策略）。
     - 使用代码读取/搜索工具收集上下文。
   - 得到：
     - `plan_markdown`。
     - `tasks` 列表。
   - 将结果写入：
     - `cases/<case_id>/plan.md`
     - `cases/<case_id>/plan.json`
   - 更新 `plans` 表、`tasks` 表。
3. 前端 `PlanningView`：
   - 渲染 `plan.md` 与任务列表。
   - 支持你手动编辑计划内容（更新后回写文件与 DB）。

#### 3.3 按子任务执行（CodingAgent 流程）

1. 在 `ExecutionView` 中选择一个子任务。
2. `ExecutionController`：
   - 读取该任务的 `related_files` 列表。
   - 通过 ToolHub 读取对应文件内容。
   - 调用 `CodingAgent`：
     - 输入：任务描述 + 文件内容 + 约束等。
     - 经 `LLMRouter` 选择 `coding` 模型。
   - 得到若干 `patches` + 解释。
   - 将结果记录到：
     - `cases/<case_id>/patches/<task_id>_<run_id>.json`
     - `agent_runs` 表。
3. 前端 `ExecutionView`：
   - 展示 Patch 列表与 diff 预览。
   - 提供：
     - 「复制 Patch」→ 粘贴到 Cursor 中应用。
     - （未来）「通过工具直接应用 Patch 到仓库」。

#### 3.4 测试与验收（TestAgent 流程）

1. 当若干子任务完成后，在 `TestAndReviewView` 中点击「生成测试建议」。
2. `TestController`：
   - 聚合本 Case 的改动（可通过 Git diff 或记录的 Patch）。
   - 调用 `TestAgent`（模型策略 `summary`）。
   - 得到：
     - `potential_issues`
     - `test_cases`
     - `manual_checklist`
   - 写入：
     - `cases/<case_id>/verification.md`
     - `test_records` 表。
3. 你执行测试与手工验收：
   - 在 UI 中勾选已完成测试与验证项。
   - 可在 `verification.md` 补充备注。

#### 3.5 上线与总结

1. 你在本地完成提交、合并与部署。
2. 在 UI 中将 Case 状态标记为「已上线」。
3. 在 `HistoryView` 中补充/编辑 `summary.md`：
   - 实际实现与原计划的偏差。
   - 下次可以如何与 Agent 更好协作。

---

### 4. 技术栈建议（可调整）

> 以下是针对「快速自用 MVP」的建议，可以按你确认的主语言调整实现。

- **后端**：
  - Python + FastAPI（或等价框架）：
    - 快速开发 HTTP API。
    - 异步支持便于同时处理多个 LLM 调用。
  - 或：TypeScript + NestJS / Express。
- **前端**：
  - React + 一套简洁 UI 组件库（如 Ant Design / Chakra UI）。
  - 或直接在 Cursor 内内嵌使用 CLI + Markdown 输出（前期极简版）。
- **存储**：
  - SQLite + 文件系统（如前文所述）。

---

### 5. 增量演进方向

在 MVP 跑通后，可以逐步演进：

1. **更紧密的 IDE 集成**：
   - 提供 VS Code/Cursor 插件，直接在编辑器侧栏展示 OpenClaw Studio 视图。
2. **自动 Patch 应用与回滚**：
   - 在后端通过 Git 操作自动应用/回滚 Patch。
3. **多用户与权限**：
   - 支持多开发者账号与权限控制。
4. **更丰富的工具集**：
   - CI 状态查询、Issue/PR 系统集成（GitHub/GitLab 等）。

这些都可以在不破坏当前核心架构的前提下迭代加入。

