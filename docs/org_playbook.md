### 从 1 人到 5 人的角色分工、协作模式与知识库结构

> 对应待办 `org-playbook`。目标是：当你从「个人实践者」扩展到一个 2–5 人小团队时，OpenClaw 仍然是协作中枢，而不是额外负担。

---

### 1. 阶段划分与总体思路

- **阶段 0：1 人（当前）**
  - 你一个人承担产品/架构/开发/运维所有角色。
  - 重点：跑通 3–5 个完整闭环，并沉淀案例与规则。
- **阶段 1：2–3 人**
  - 引入 1–2 名「AI 工程/后端/前端」伙伴。
  - 重点：让新成员「默认通过 OpenClaw 协作」，而不是绕过它。
- **阶段 2：4–5 人**
  - 形成比较稳定的分工：产品/Agent 流程/前端/平台等。
  - 重点：规范化工作流，避免信息只留在聊天里。

原则：**任何新成员加入，都应该能通过 OpenClaw Studio + 知识库快速复盘你过去的闭环案例，并按相同模式工作。**

---

### 2. 关键角色定义（2–5 人阶段）

#### 2.1 AI 工程负责人（你）

- 职责：
  - 负责 OpenClaw 的整体架构与演进路线。
  - 定义/维护 LLMRouter 策略、Agent 能力边界与工具规范。
  - 把业务需求转化为「可被 Agent 执行的工作流」。
- 主要与 Agent 的关系：
  - 高频使用 PlanningAgent 做高层规划。
  - 与 Agent 共同定义/优化提示词模板与内部协议。

#### 2.2 Agent 流程工程师

- 职责：
  - 负责编排 Agent 调用顺序与上下文管理。
  - 开发/维护 ToolHub 中的各类工具（代码搜索、CI 查询、Issue 同步等）。
  - 优化 Agent 的「状态机」与出错恢复策略。
- 协作方式：
  - 与你一起迭代 `agents.md` 与实际实现代码。
  - 在案例闭环中观察 Agent 表现，提出改进方案。

#### 2.3 前端/体验工程师

- 职责：
  - 负责 OpenClaw Studio 的 UI/UX。
  - 将复杂的 Agent 能力包装成易理解的交互流程。
  - 为不同角色（产品/后端/测试）设计专属视图或快捷入口。
- 协作方式：
  - 使用 CodingAgent 协助开发前端代码（组件/状态管理/接口调用）。
  - 将「最佳使用方式」写入 `/playbooks` 中的前端工作流剧本。

#### 2.4 平台/DevOps 工程师（可由你或他人兼职）

- 职责：
  - 管理部署、CI/CD、监控与日志。
  - 将 TestAgent 与 CI 集成，形成自动化质量门禁。
- 协作方式：
  - 设计一套「上线前必须经过的 Agent 流程」。
  - 将环境信息与运维规范写入知识库。

---

### 3. 人机协作工作流示例（按角色）

#### 3.1 产品/需求方如何使用 OpenClaw

1. 在 `RequirementCenter` 中创建需求：
   - 使用统一模板（见下方知识库部分）。
2. 通过 Studio 调用 PlanningAgent 生成实现计划。
3. 与 AI 工程负责人一起 Review 计划，必要时调整需求。

#### 3.2 开发工程师如何使用 OpenClaw

1. 从 `cases` 列表中选择一个已确认计划的需求。
2. 在 `ExecutionView` 中领取子任务：
   - 可以按人分配，也可以自由领取。
3. 针对子任务调用 CodingAgent：
   - 阅读 Patch 建议与解释。
   - 在本地 IDE 中应用/调整。
4. 自测 + 触发 TestAgent 获取更多测试建议。

#### 3.3 测试/质量角色如何使用 OpenClaw（可由 Dev 兼任）

1. 在 `TestAndReviewView` 中查看 Agent 生成的测试建议。
2. 扩展或细化为实际测试用例（手工或自动化）。
3. 将测试结果与问题反馈回 `cases/<case_id>/verification.md`。
4. 将典型问题沉淀为「回归检查清单」。

---

### 4. 知识库结构设计

建议使用「文件系统 + 轻量 Wiki」的组合，初步结构如下：

```text
docs/
  rules/           # 统一规则与规范
    coding.md      # 代码风格、提交规范
    api_design.md  # API 设计与版本管理规范
    agents.md      # Agent 使用与提示词风格规范（可拆分）

  playbooks/       # 人机协作剧本
    fe_workflow.md     # 前端工程师如何用 OpenClaw
    be_workflow.md     # 后端/Agent 工程师协作流程
    qa_workflow.md     # 测试/QA 如何结合 TestAgent
    release_flow.md    # 发布与回滚流程中的 Agent 使用

  cases/           # 典型需求实现案例（按需求/feature 分类）
    <case_id>/
      plan.md
      plan.json
      patches/
      verification.md
      summary.md

  org/             # 组织与团队相关
    roles.md       # 本文精简版 + 确认后的最终版
    onboarding.md  # 新成员 onboarding 指南
    rituals.md     # 例会、复盘等固定仪式的说明
```

---

### 5. 新成员 Onboarding 剧本（简版）

当一个新同事加入时，可以按下面路径引导：

1. **第 1 天：理解体系**
   - 阅读：
     - `docs/core.md`：OpenClaw 核心定位与技术栈。
     - `docs/llm_router.md`：LLMRouter 与多模型策略（了解即可）。
     - `docs/workflow.md`：单人闭环流程。
   - 在 OpenClaw Studio 中浏览几条历史 `cases`，熟悉从需求到上线的完整路径。
2. **第 2–3 天：跟做一个已完成的 Case**
   - 选择一个代表性案例：
     - 按文档重新走一遍：阅读需求 → 计划 → Patch → 测试。
   - 目标：能从历史记录中看懂当时 Agent 与人是如何协作的。
3. **第 4–7 天：在你的陪同下完成一个「真实需求」**
   - 由你担任「辅导员」：
     - 帮他使用 PlanningAgent/CodingAgent/TestAgent 完成一个小需求。
   - 结果：在 `cases` 中新增一个由他主导的完整闭环案例。

---

### 6. 团队协作中的约定与仪式

- **统一约定**：
  - 所有新需求，必须在 RequirementCenter 中创建并走 PlanningAgent。
  - 所有中大型改动，都要有对应的 `case` 与 `plan` 文档。
  - 任何「非小修小补」的提交，都建议在合并前走一次 TestAgent。
- **例行仪式（可按周/月执行）**：
  - **Weekly Case Review**：
    - 每周选 1–2 个典型 Case，一起回顾：
      - Agent 表现好/不好的地方。
      - 哪些 Prompt/规则需要更新。
  - **Monthly Playbook Update**：
    - 根据当月实践，更新：
      - `playbooks/*`
      - `rules/*`

---

### 7. 你现在可以落地的最小组织动作

即使目前只有你一个人，也可以先做以下两件事为未来团队铺路：

1. **坚持用同一套流程与模板工作**：
   - 每个需求都按 `workflow.md` 中的流程走一遍。
   - 所有产出都沉淀为 `cases` 与 `playbooks`。
2. **边做边写「给未来同事看的说明」**：
   - 在每个 Case 的 `summary.md` 里，假设未来有人要学习你是怎么做的，写给 TA 看。
   - 定期整理到 `org/onboarding.md` 中，形成一份「加入 OpenClaw 团队的第一周」指南。

当你之后真的拉起 2–5 人小团队时，这些文档和流程就可以直接复用，而不需要重新从零讲一遍你的工作方式。

