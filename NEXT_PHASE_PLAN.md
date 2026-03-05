# 下一阶段开发计划（Phase 2）

## 📊 当前状态总结

### ✅ 已完成（Phase 1）
- [x] **核心基础设施**
  - LLMRouter：多模型统一路由（Qwen/MiniMax）
  - PlanningAgent、CodingAgent、TestAgent
  - 工具集：代码读取/搜索/项目结构
- [x] **CLI 框架**
  - 完整的命令行接口
  - 案例管理（create-case, list-cases, show-case）
  - 规划命令（plan, show-plan）
  - 编码命令（code）
  - 测试命令（test）
- [x] **案例库系统**
  - SQLite 数据库（cases, plans, tasks, agent_runs, test_records）
  - 文件系统存储（plans, patches, tests）
  - CaseManager 统一接口
- [x] **日志系统**
  - 完整的日志模块（Logger）
  - CLI 日志集成
  - 文件轮转支持
- [x] **第一个完整闭环**
  - 使用真实需求（日志功能）完成完整流程
  - 成功生成计划、代码补丁、测试建议
  - 补丁已应用到代码库

### 📈 项目统计
- **代码行数**: ~3000+ 行
- **测试用例**: 21 个（全部通过）
- **案例数**: 1 个完整案例
- **文档**: 10+ 个设计和使用文档

---

## 🎯 Phase 2 目标（2-3 周）

### 核心目标
1. **Web 控制台 MVP**：提供可视化界面，替代部分 CLI 操作
2. **Git 深度集成**：与代码仓库无缝对接
3. **知识库系统**：沉淀开发经验和最佳实践
4. **使用 AI 原生流程开发新功能**：用 OpenClaw 开发 OpenClaw

---

## 📋 Phase 2.1: Web 控制台后端 API（Week 1）

### 目标
实现 FastAPI 后端，提供 RESTful API 供前端调用。

### 任务清单

#### 1. 项目结构搭建
- [ ] 创建 `openclaw_studio_api/` 目录
- [ ] 初始化 FastAPI 项目
- [ ] 配置依赖（requirements.txt 更新）
- [ ] 设置项目结构：
  ```
  openclaw_studio_api/
    __init__.py
    main.py              # FastAPI 应用入口
    api/
      __init__.py
      cases.py            # 案例管理 API
      plans.py            # 规划 API
      code.py             # 编码 API
      tests.py            # 测试 API
      history.py          # 历史记录 API
    models/
      __init__.py
      schemas.py          # Pydantic 模型
    services/
      __init__.py
      case_service.py     # 案例服务层
      agent_service.py    # Agent 调用服务层
  ```

#### 2. 实现核心 API 端点

**案例管理 API** (`/api/cases`)
- [ ] `GET /api/cases` - 列出所有案例
- [ ] `POST /api/cases` - 创建新案例
- [ ] `GET /api/cases/{case_id}` - 获取案例详情
- [ ] `PUT /api/cases/{case_id}` - 更新案例
- [ ] `DELETE /api/cases/{case_id}` - 删除案例（可选）

**规划 API** (`/api/cases/{case_id}/plan`)
- [ ] `POST /api/cases/{case_id}/plan` - 生成实现计划
- [ ] `GET /api/cases/{case_id}/plan` - 获取计划
- [ ] `PUT /api/cases/{case_id}/plan` - 更新计划（人工编辑）

**编码 API** (`/api/cases/{case_id}/tasks/{task_id}/code`)
- [ ] `POST /api/cases/{case_id}/tasks/{task_id}/code` - 生成代码补丁
- [ ] `GET /api/cases/{case_id}/patches` - 获取所有补丁
- [ ] `GET /api/cases/{case_id}/patches/{patch_id}` - 获取补丁详情

**测试 API** (`/api/cases/{case_id}/test`)
- [ ] `POST /api/cases/{case_id}/test` - 生成测试建议
- [ ] `GET /api/cases/{case_id}/test` - 获取测试结果

**历史记录 API** (`/api/cases/{case_id}/history`)
- [ ] `GET /api/cases/{case_id}/history` - 获取完整历史记录
- [ ] `GET /api/cases/{case_id}/agent-runs` - 获取 Agent 调用记录

#### 3. 集成 OpenClaw Core
- [ ] 在服务层封装 CaseManager
- [ ] 封装 Agent 调用（异步处理）
- [ ] 实现错误处理和日志记录
- [ ] 添加请求验证（Pydantic）

#### 4. 测试
- [ ] 编写 API 单元测试
- [ ] 编写集成测试
- [ ] 测试异步 Agent 调用

### 技术栈
- **框架**: FastAPI
- **异步**: asyncio
- **验证**: Pydantic
- **测试**: pytest + httpx

### 交付物
- FastAPI 后端服务
- API 文档（自动生成）
- 测试覆盖

---

## 📋 Phase 2.2: Web 控制台前端（Week 2）

### 目标
实现 React 前端界面，提供易用的 Web UI。

### 任务清单

#### 1. 项目结构搭建
- [ ] 创建 `openclaw_studio_web/` 目录
- [ ] 初始化 React + TypeScript 项目
- [ ] 配置构建工具（Vite 或 Create React App）
- [ ] 设置项目结构：
  ```
  openclaw_studio_web/
    src/
      components/
        CaseList.tsx
        CaseDetail.tsx
        PlanningView.tsx
        ExecutionView.tsx
        TestView.tsx
        HistoryView.tsx
      services/
        api.ts              # API 客户端
      hooks/
        useCases.ts
        usePlan.ts
      App.tsx
      index.tsx
  ```

#### 2. 实现核心视图

**需求中心** (`/cases`)
- [ ] 案例列表页面
  - 显示所有案例（状态、标题、创建时间）
  - 筛选和搜索功能
  - 创建新案例按钮
- [ ] 案例详情页面
  - 显示案例基本信息
  - 显示关联的 Git 仓库信息
  - 快速操作按钮（生成计划、查看历史）

**规划视图** (`/cases/{id}/plan`)
- [ ] 计划展示页面
  - Markdown 渲染（使用 react-markdown）
  - 子任务列表（可展开/折叠）
  - 编辑计划功能（Markdown 编辑器）
  - 生成计划按钮

**执行视图** (`/cases/{id}/execution`)
- [ ] 任务列表页面
  - 显示所有子任务（状态、风险级别）
  - 为任务生成代码按钮
- [ ] 补丁展示页面
  - Diff 预览（使用 react-diff-view）
  - 补丁列表
  - 复制补丁按钮
  - 应用状态跟踪

**测试视图** (`/cases/{id}/test`)
- [ ] 测试建议页面
  - 潜在问题列表
  - 测试用例列表
  - 验收清单（可勾选）
  - 生成测试建议按钮

**历史视图** (`/cases/{id}/history`)
- [ ] 时间线展示
  - 完整闭环记录
  - Agent 调用记录
  - 状态变化历史

#### 3. UI 组件库
- [ ] 选择 UI 库（推荐：Ant Design 或 Material-UI）
- [ ] 实现基础组件（Button, Card, Table, Modal）
- [ ] 实现 Markdown 编辑器组件
- [ ] 实现 Diff 查看器组件

#### 4. 状态管理
- [ ] 使用 React Context 或 Zustand 管理全局状态
- [ ] 实现 API 调用封装
- [ ] 实现错误处理

#### 5. 测试
- [ ] 编写组件单元测试
- [ ] 编写 E2E 测试（可选）

### 技术栈
- **框架**: React 18+
- **语言**: TypeScript
- **UI 库**: Ant Design 或 Material-UI
- **构建**: Vite
- **状态管理**: Zustand 或 React Context

### 交付物
- React 前端应用
- 响应式设计
- 基础测试覆盖

---

## 📋 Phase 2.3: Git 深度集成（Week 2-3）

### 目标
实现与 Git 仓库的深度集成，支持代码状态查看和操作。

### 任务清单

#### 1. Git 工具实现
- [ ] 创建 `openclaw_core/git_tools.py`
- [ ] 实现 Git 操作类：
  ```python
  class GitTools:
      def get_repo_info(repo_path: str) -> Dict
      def get_branches(repo_path: str) -> List[str]
      def get_current_branch(repo_path: str) -> str
      def get_diff(repo_path: str, base: str, head: str) -> str
      def create_branch(repo_path: str, branch_name: str) -> bool
      def get_commit_history(repo_path: str, limit: int) -> List[Dict]
      def get_file_content(repo_path: str, file_path: str, ref: str) -> str
  ```

#### 2. 集成到 CaseManager
- [ ] 在创建案例时验证 Git 仓库
- [ ] 在生成计划时读取项目结构
- [ ] 在生成代码时获取相关文件内容
- [ ] 在应用补丁后显示 Git diff

#### 3. API 扩展
- [ ] `GET /api/cases/{case_id}/git-status` - 获取 Git 状态
- [ ] `GET /api/cases/{case_id}/git-diff` - 获取代码差异
- [ ] `GET /api/cases/{case_id}/git-branches` - 获取分支列表

#### 4. 前端集成
- [ ] 在案例详情页显示 Git 状态
- [ ] 在补丁页面显示 Git diff
- [ ] 支持创建新分支（可选）

### 技术栈
- **Git 库**: GitPython 或 subprocess
- **集成**: 与现有工具集整合

### 交付物
- Git 工具类
- API 端点
- 前端展示

---

## 📋 Phase 2.4: 知识库系统（Week 3）

### 目标
建立可复制的知识体系，沉淀开发经验和最佳实践。

### 任务清单

#### 1. 知识库结构
- [ ] 创建知识库目录结构：
  ```
  knowledge_base/
    rules/              # 规则与规范
      coding_standards.md
      api_design.md
      agent_prompts.md
    playbooks/          # 工作流剧本
      feature_development.md
      bug_fixing.md
      refactoring.md
    cases/              # 案例库（链接到 cases/）
      case-001/
      case-002/
    templates/          # 模板
      case_template.md
      plan_template.md
  ```

#### 2. 案例模板系统
- [ ] 实现案例模板生成
- [ ] 支持从模板创建新案例
- [ ] 案例总结自动归档

#### 3. 知识库搜索
- [ ] 实现全文搜索功能
- [ ] 支持按标签/类型筛选
- [ ] API 端点：`GET /api/knowledge/search?q=...`

#### 4. 最佳实践提取
- [ ] 从历史案例中提取模式
- [ ] 生成最佳实践文档
- [ ] 自动更新知识库

### 交付物
- 知识库目录结构
- 搜索功能
- 模板系统

---

## 🤖 使用 AI 原生研发流程开发新功能

### 核心理念
**用 OpenClaw 开发 OpenClaw** - 每个新功能模块都通过完整的 AI 原生研发流程来开发。

### 工作流程

#### 1. 创建功能开发案例
```bash
# 为每个新功能创建一个案例
openclaw create-case "实现 Web 控制台后端 API" \
  --description "使用 FastAPI 实现 OpenClaw Studio 后端 API，提供 RESTful 接口供前端调用" \
  --repo "." \
  --branch "main"
```

#### 2. 生成实现计划
```bash
# 使用 PlanningAgent 生成详细计划
openclaw plan <case_id> \
  --related-files "docs/mvp_studio.md" "openclaw_studio/case_manager.py"
```

#### 3. 人工 Review 计划
- 在 Web 控制台或 CLI 中查看生成的计划
- 编辑和调整计划
- 确认任务拆解

#### 4. 按任务生成代码
```bash
# 为每个子任务生成代码
openclaw code <case_id> <task_id>
```

#### 5. 应用补丁并测试
- 查看生成的补丁
- 应用补丁到代码库
- 运行测试

#### 6. 生成测试建议
```bash
# 生成测试建议和验收清单
openclaw test <case_id>
```

#### 7. 完成并总结
- 执行测试和验收
- 记录实现过程中的经验
- 更新知识库

### 优势

1. **实践验证**：在开发过程中验证 OpenClaw 的能力
2. **持续改进**：发现流程问题，立即改进
3. **知识沉淀**：每个功能开发都成为知识库的一部分
4. **可追溯性**：完整的开发历史记录

### 示例：开发 Web API 模块

#### Step 1: 创建案例
```bash
openclaw create-case "实现 Web 控制台后端 API" \
  --description "使用 FastAPI 实现 RESTful API，支持案例管理、规划、编码、测试等功能"
```

#### Step 2: 生成计划
```bash
openclaw plan case-xxx \
  --related-files "docs/mvp_studio.md" "openclaw_studio/case_manager.py" "openclaw_core/agents.py"
```

PlanningAgent 会生成类似这样的计划：
- 任务 1: 搭建 FastAPI 项目结构
- 任务 2: 实现案例管理 API
- 任务 3: 实现规划 API
- 任务 4: 实现编码 API
- 任务 5: 实现测试 API
- 任务 6: 集成 OpenClaw Core
- 任务 7: 添加 API 文档
- 任务 8: 编写测试

#### Step 3: 逐个任务生成代码
```bash
# 为每个任务生成代码
openclaw code case-xxx task-001  # 项目结构
openclaw code case-xxx task-002  # 案例管理 API
# ...
```

#### Step 4: 应用补丁并测试
- 查看每个补丁
- 应用补丁
- 运行测试

#### Step 5: 生成测试建议
```bash
openclaw test case-xxx
```

#### Step 6: 完成并归档
- 执行验收清单
- 记录经验教训
- 更新知识库

### 知识库更新

每次完成功能开发后：
1. **案例归档**：将案例移动到 `knowledge_base/cases/`
2. **提取模式**：从案例中提取可复用的模式
3. **更新模板**：更新案例模板和最佳实践
4. **文档更新**：更新相关文档

---

## 📅 时间规划

### Week 1: Web 后端 API
- **Day 1-2**: 项目结构搭建 + 基础 API
- **Day 3-4**: 核心 API 实现
- **Day 5**: 集成测试 + 文档

### Week 2: Web 前端 + Git 集成
- **Day 1-3**: 前端核心视图实现
- **Day 4-5**: Git 集成 + 前端集成

### Week 3: 知识库系统 + 优化
- **Day 1-2**: 知识库结构 + 搜索
- **Day 3-4**: 使用 AI 流程开发新功能（实践）
- **Day 5**: 优化 + 文档

---

## 🎯 成功标准

### Phase 2 完成标准
- ✅ Web 控制台可以替代 CLI 完成所有核心操作
- ✅ 界面清晰易用，新用户可以快速上手
- ✅ Git 集成完善，可以查看代码状态
- ✅ 知识库内容丰富，至少 3 个完整案例
- ✅ 至少使用 AI 流程完成 1 个新功能开发

---

## 💡 建议

1. **优先使用 AI 流程**：每个新功能都用 OpenClaw 开发
2. **小步快跑**：先实现 MVP，再逐步完善
3. **持续记录**：每个决策和问题都要记录
4. **快速迭代**：根据使用反馈快速调整

---

## 🚀 立即开始

### 第一个任务：使用 AI 流程开发 Web API 模块

```bash
# 1. 创建案例
openclaw create-case "实现 Web 控制台后端 API" \
  --description "使用 FastAPI 实现 OpenClaw Studio 后端 API"

# 2. 生成计划
openclaw plan <case_id>

# 3. 开始开发
# 按照生成的计划，逐个任务生成代码
```

让我们开始用 OpenClaw 开发 OpenClaw！
