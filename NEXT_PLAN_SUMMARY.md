# 下一步计划总结

## 📊 当前状态

### ✅ Phase 2.1: Web 后端 API（已完成 95%）
- ✅ FastAPI 项目结构
- ✅ 案例管理 API
- ✅ 规划 API
- ✅ 编码 API
- ✅ 测试 API
- ✅ 历史记录 API
- ✅ 健康检查端点
- ✅ 全局异常处理
- ✅ 测试覆盖（8/8 通过）

### ⏳ 待完善
- ⚠️ 测试 API 结果格式优化
- ⚠️ API 文档补充示例

---

## 🎯 下一步计划

### Phase 2.2: Web 前端开发（Week 2）

#### 目标
实现 React 前端界面，提供可视化 Web UI，替代部分 CLI 操作。

#### 核心任务

##### 1. 项目结构搭建
- [ ] 创建 `openclaw_studio_web/` 目录
- [ ] 初始化 React + TypeScript 项目（使用 Vite）
- [ ] 配置构建工具和开发环境
- [ ] 设置项目结构：
  ```
  openclaw_studio_web/
    src/
      components/      # UI 组件
      views/           # 页面视图
      services/        # API 客户端
      hooks/           # React Hooks
      types/           # TypeScript 类型
      utils/           # 工具函数
  ```

##### 2. 实现核心视图

**需求中心** (`/cases`)
- [ ] 案例列表页面
  - 显示所有案例（状态、标题、创建时间）
  - 筛选和搜索功能
  - 创建新案例按钮和表单
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
  - Diff 预览（使用 react-diff-view 或类似库）
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

##### 3. UI 组件库选择
- [ ] 选择 UI 库（推荐：Ant Design 或 Material-UI）
- [ ] 实现基础组件（Button, Card, Table, Modal）
- [ ] 实现 Markdown 编辑器组件
- [ ] 实现 Diff 查看器组件

##### 4. 状态管理和 API 集成
- [ ] 使用 Zustand 或 React Context 管理全局状态
- [ ] 实现 API 调用封装（基于 FastAPI 后端）
- [ ] 实现错误处理和加载状态
- [ ] 实现实时状态更新（轮询或 WebSocket）

##### 5. 测试
- [ ] 编写组件单元测试
- [ ] 编写 E2E 测试（可选）

#### 技术栈
- **框架**: React 18+
- **语言**: TypeScript
- **UI 库**: Ant Design 或 Material-UI
- **构建**: Vite
- **状态管理**: Zustand 或 React Context
- **路由**: React Router
- **HTTP 客户端**: axios 或 fetch

---

### Phase 2.3: Git 深度集成（Week 2-3）

#### 目标
实现与 Git 仓库的深度集成，支持代码状态查看和操作。

#### 核心任务

##### 1. Git 工具实现
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

##### 2. 集成到 CaseManager
- [ ] 在创建案例时验证 Git 仓库
- [ ] 在生成计划时读取项目结构
- [ ] 在生成代码时获取相关文件内容
- [ ] 在应用补丁后显示 Git diff

##### 3. API 扩展
- [ ] `GET /api/v1/cases/{case_id}/git-status` - 获取 Git 状态
- [ ] `GET /api/v1/cases/{case_id}/git-diff` - 获取代码差异
- [ ] `GET /api/v1/cases/{case_id}/git-branches` - 获取分支列表

##### 4. 前端集成
- [ ] 在案例详情页显示 Git 状态
- [ ] 在补丁页面显示 Git diff
- [ ] 支持创建新分支（可选）

---

### Phase 2.4: 知识库系统（Week 3）

#### 目标
建立可复制的知识体系，沉淀开发经验和最佳实践。

#### 核心任务

##### 1. 知识库结构
- [ ] 创建知识库目录结构：
  ```
  knowledge_base/
    rules/              # 规则与规范
    playbooks/         # 工作流剧本
    cases/             # 案例库（链接到 cases/）
    templates/         # 模板
  ```

##### 2. 案例模板系统
- [ ] 实现案例模板生成
- [ ] 支持从模板创建新案例
- [ ] 案例总结自动归档

##### 3. 知识库搜索
- [ ] 实现全文搜索功能
- [ ] 支持按标签/类型筛选
- [ ] API 端点：`GET /api/v1/knowledge/search?q=...`

---

## 🚀 立即开始（推荐顺序）

### 第一步：Web 前端开发（高优先级）

**使用 AI 原生流程开发前端**

```bash
# 1. 创建案例
openclaw create-case "实现 Web 控制台前端界面" \
  --description "使用 React + TypeScript 实现 OpenClaw Studio 前端界面，提供可视化 Web UI，包括需求中心、规划视图、执行视图、测试视图和历史视图。" \
  --repo "." \
  --branch "main"

# 2. 生成计划
openclaw plan <case_id> \
  --related-files "docs/mvp_studio.md" \
                   "openclaw_studio/api/main.py" \
                   "openclaw_studio/api/v1/cases.py"

# 3. 查看计划并开始开发
openclaw show-plan <case_id>
```

### 第二步：Git 集成（中优先级）

**使用 AI 原生流程开发 Git 集成**

```bash
# 1. 创建案例
openclaw create-case "实现 Git 深度集成" \
  --description "实现与 Git 仓库的深度集成，支持代码状态查看、diff 预览、分支管理等功能。"

# 2. 生成计划并开发
openclaw plan <case_id>
```

---

## 📅 时间规划

### Week 2: Web 前端开发
- **Day 1-2**: 项目搭建 + 基础组件
- **Day 3-4**: 核心视图实现
- **Day 5**: 前后端联调 + 测试

### Week 3: Git 集成 + 知识库
- **Day 1-2**: Git 工具实现 + API 扩展
- **Day 3-4**: 知识库系统
- **Day 5**: 优化 + 文档

---

## 🎯 成功标准

### Web 前端完成标准
- ✅ 可以通过 Web UI 完成所有核心操作
- ✅ 界面清晰易用，新用户可以快速上手
- ✅ 前后端联调成功，所有 API 正常工作
- ✅ 响应式设计，支持不同屏幕尺寸

### Git 集成完成标准
- ✅ 可以查看 Git 仓库状态
- ✅ 可以预览代码差异
- ✅ 可以管理分支
- ✅ 前端可以展示 Git 信息

---

## 💡 关键原则

1. **用 OpenClaw 开发 OpenClaw** - 每个新功能都用 AI 原生流程
2. **小步快跑** - 先实现 MVP，再逐步完善
3. **持续记录** - 每个决策和问题都要记录
4. **快速迭代** - 根据使用反馈快速调整

---

**最后更新**: 2026-03-05 18:40:00
