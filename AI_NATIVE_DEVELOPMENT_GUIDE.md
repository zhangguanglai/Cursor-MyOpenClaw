# AI 原生研发流程指南

## 📖 概述

本文档说明如何使用 OpenClaw 的 AI 原生研发流程来开发新功能模块。核心理念是：**用 OpenClaw 开发 OpenClaw**。

---

## 🔄 完整工作流程

### 流程图

```
需求输入
    ↓
创建案例 (create-case)
    ↓
生成计划 (plan) ← PlanningAgent
    ↓
人工 Review & 确认
    ↓
按任务生成代码 (code) ← CodingAgent
    ↓
应用补丁 & 测试
    ↓
生成测试建议 (test) ← TestAgent
    ↓
执行验收
    ↓
完成 & 归档到知识库
```

---

## 📝 详细步骤

### Step 1: 需求输入与案例创建

**目标**：将功能需求转化为可追踪的案例

**操作**：
```bash
openclaw create-case "<功能标题>" \
  --description "<详细描述，包括：
  - 功能目标
  - 用户场景
  - 验收标准
  - 技术约束>" \
  --repo "." \
  --branch "main"
```

**示例**：
```bash
openclaw create-case "实现 Web 控制台后端 API" \
  --description "使用 FastAPI 实现 OpenClaw Studio 后端 API，提供 RESTful 接口。

功能目标：
- 提供案例管理 API（CRUD）
- 提供规划、编码、测试 API
- 集成 OpenClaw Core 的 Agent 调用
- 支持异步任务处理

用户场景：
- 前端通过 API 创建和管理案例
- 前端触发 Agent 生成计划、代码、测试建议
- 查看历史记录和 Agent 调用日志

验收标准：
- 所有 API 端点正常工作
- 集成测试通过
- API 文档自动生成
- 错误处理完善

技术约束：
- 使用 FastAPI 框架
- 异步处理 Agent 调用
- 与现有 CaseManager 集成" \
  --repo "." \
  --branch "main"
```

**输出**：
- 案例 ID（如 `case-abc123`）
- 案例记录在数据库中
- 案例目录创建：`cases/case-abc123/`

---

### Step 2: 生成实现计划

**目标**：使用 PlanningAgent 生成详细的实现计划

**操作**：
```bash
openclaw plan <case_id> \
  --related-files <相关文件1> <相关文件2> ...
```

**相关文件建议**：
- 设计文档（如 `docs/mvp_studio.md`）
- 现有实现（如 `openclaw_studio/case_manager.py`）
- 依赖模块（如 `openclaw_core/agents.py`）

**示例**：
```bash
openclaw plan case-abc123 \
  --related-files "docs/mvp_studio.md" \
                   "openclaw_studio/case_manager.py" \
                   "openclaw_core/agents.py" \
                   "openclaw_cli/cli.py"
```

**PlanningAgent 会**：
1. 读取需求描述
2. 分析相关文件
3. 理解项目结构
4. 生成详细计划，包括：
   - 任务拆解（5-10 个子任务）
   - 每个任务的描述、相关文件、风险级别
   - 技术方案建议
   - 依赖关系

**输出**：
- `cases/case-abc123/plan.md` - Markdown 格式的计划
- `cases/case-abc123/plan.json` - 结构化任务列表
- 数据库中的 `plans` 和 `tasks` 记录

**查看计划**：
```bash
openclaw show-plan case-abc123
```

---

### Step 3: 人工 Review 与确认

**目标**：审查计划，调整和确认

**操作**：
1. 查看生成的计划：
   ```bash
   openclaw show-plan case-abc123
   ```

2. 在 Web 控制台或编辑器中查看 `plan.md`

3. 根据需要调整：
   - 编辑 `plan.md` 文件
   - 调整任务优先级
   - 添加或删除任务
   - 修改任务描述

4. 确认计划后，开始执行

**Review 要点**：
- ✅ 任务拆解是否合理？
- ✅ 是否有遗漏的功能点？
- ✅ 技术方案是否可行？
- ✅ 风险是否识别到位？
- ✅ 依赖关系是否清晰？

---

### Step 4: 按任务生成代码

**目标**：使用 CodingAgent 为每个子任务生成代码补丁

**操作**：
```bash
# 查看任务列表
openclaw show-tasks case-abc123

# 为每个任务生成代码
openclaw code case-abc123 task-001
openclaw code case-abc123 task-002
# ...
```

**CodingAgent 会**：
1. 读取任务描述和相关文件
2. 分析代码上下文
3. 生成代码补丁（diff 格式）
4. 提供补丁说明

**输出**：
- `cases/case-abc123/patches/task-001.patch` - 补丁文件
- `cases/case-abc123/patches/task-001.meta.json` - 元数据
- 数据库中的 `agent_runs` 记录

**查看补丁**：
```bash
# 在编辑器中查看
cat cases/case-abc123/patches/task-001.patch

# 或在 Web 控制台中查看 diff
```

---

### Step 5: 应用补丁并测试

**目标**：应用生成的补丁，验证功能

**操作**：

1. **Review 补丁**：
   - 查看 diff，理解代码变更
   - 检查是否符合预期
   - 确认没有破坏性变更

2. **应用补丁**：
   ```bash
   # 手动应用（推荐）
   # 在编辑器中查看补丁，手动应用更改
   
   # 或使用 git apply（如果补丁格式正确）
   git apply cases/case-abc123/patches/task-001.patch
   ```

3. **运行测试**：
   ```bash
   # 运行相关测试
   python -m pytest tests/test_xxx.py
   
   # 运行所有测试
   python -m pytest tests/
   ```

4. **修复问题**：
   - 如果补丁有问题，可以：
     - 手动修复
     - 重新生成补丁（调整 prompt 或相关文件）
     - 创建新任务修复

5. **提交代码**：
   ```bash
   git add .
   git commit -m "feat: <功能描述>"
   ```

---

### Step 6: 生成测试建议

**目标**：使用 TestAgent 生成测试建议和验收清单

**操作**：
```bash
openclaw test case-abc123
```

**TestAgent 会**：
1. 分析所有代码变更（补丁）
2. 识别潜在问题
3. 生成测试用例
4. 提供验收清单

**输出**：
- `cases/case-abc123/tests/suggestions.md` - 测试建议
- `cases/case-abc123/tests/checklist.md` - 验收清单
- 数据库中的 `test_records` 记录

**查看测试建议**：
```bash
cat cases/case-abc123/tests/suggestions.md
```

---

### Step 7: 执行验收

**目标**：按照测试建议和验收清单执行测试

**操作**：

1. **执行测试用例**：
   - 按照 `suggestions.md` 中的测试用例执行
   - 记录测试结果

2. **检查验收清单**：
   - 逐项检查 `checklist.md` 中的项目
   - 标记完成状态

3. **修复问题**：
   - 如果发现问题，创建新的修复任务
   - 重复 Step 4-7

4. **更新案例状态**：
   ```bash
   # 在 Web 控制台或数据库中更新状态
   # status: testing -> completed
   ```

---

### Step 8: 完成与归档

**目标**：总结开发过程，归档到知识库

**操作**：

1. **编写总结**：
   - 在 `cases/case-abc123/summary.md` 中记录：
     - 实际实现与原计划的偏差
     - 遇到的问题和解决方案
     - 下次可以如何改进
     - 可复用的经验

2. **归档到知识库**：
   ```bash
   # 将案例移动到知识库
   mv cases/case-abc123 knowledge_base/cases/
   
   # 或创建链接
   ln -s ../cases/case-abc123 knowledge_base/cases/case-abc123
   ```

3. **更新知识库**：
   - 提取可复用的模式
   - 更新最佳实践文档
   - 更新案例模板

---

## 🎯 最佳实践

### 1. 需求描述要详细
- 包含功能目标、用户场景、验收标准
- 说明技术约束和依赖
- 提供相关文档和代码文件

### 2. 任务拆解要合理
- 每个任务应该是独立的、可测试的
- 任务之间依赖关系清晰
- 任务大小适中（1-2 天可完成）

### 3. 及时 Review
- 生成计划后立即 Review
- 生成代码后立即 Review
- 不要盲目应用所有补丁

### 4. 持续测试
- 每个任务完成后运行测试
- 发现问题立即修复
- 保持测试通过

### 5. 记录一切
- 记录每个决策
- 记录遇到的问题
- 记录解决方案
- 更新知识库

---

## 📚 示例：完整开发流程

### 案例：实现 Web API 模块

#### Step 1: 创建案例
```bash
openclaw create-case "实现 Web 控制台后端 API" \
  --description "..." \
  --repo "." \
  --branch "main"
# 输出: case-abc123
```

#### Step 2: 生成计划
```bash
openclaw plan case-abc123 \
  --related-files "docs/mvp_studio.md" "openclaw_studio/case_manager.py"
# 生成 8 个子任务
```

#### Step 3: Review 计划
```bash
openclaw show-plan case-abc123
# 查看并调整计划
```

#### Step 4: 生成代码
```bash
openclaw code case-abc123 task-001  # 项目结构
openclaw code case-abc123 task-002  # 案例管理 API
openclaw code case-abc123 task-003  # 规划 API
# ... 继续其他任务
```

#### Step 5: 应用补丁
```bash
# 逐个应用补丁
git apply cases/case-abc123/patches/task-001.patch
# 测试
python -m pytest tests/
# 提交
git commit -m "feat: Add FastAPI project structure"
```

#### Step 6: 生成测试建议
```bash
openclaw test case-abc123
# 查看测试建议
cat cases/case-abc123/tests/suggestions.md
```

#### Step 7: 执行验收
- 执行测试用例
- 检查验收清单
- 修复问题

#### Step 8: 完成归档
- 编写总结
- 归档到知识库
- 更新最佳实践

---

## 🔍 常见问题

### Q: 生成的代码不符合预期怎么办？
A: 
1. 检查需求描述是否清晰
2. 检查相关文件是否完整
3. 调整 prompt 或重新生成
4. 手动修复并记录经验

### Q: 如何提高代码质量？
A:
1. 提供更详细的需求描述
2. 提供更多相关文件和示例
3. 在 Review 时给出明确反馈
4. 使用 TestAgent 生成测试

### Q: 如何加快开发速度？
A:
1. 并行处理独立任务
2. 复用已有的案例和模板
3. 使用知识库中的最佳实践
4. 自动化测试和部署

---

## 📈 持续改进

### 每次开发后
1. **回顾流程**：哪些步骤有效？哪些需要改进？
2. **更新知识库**：提取可复用的模式
3. **优化 Prompt**：根据效果调整 Agent 的 prompt
4. **改进工具**：根据使用反馈改进 CLI 和 Web 控制台

### 长期目标
- 建立丰富的案例库
- 形成可复用的开发模式
- 自动化更多步骤
- 支持团队协作

---

## 🚀 开始使用

准备好用 AI 原生流程开发新功能了吗？

```bash
# 创建第一个功能开发案例
openclaw create-case "你的功能标题" \
  --description "详细描述" \
  --repo "." \
  --branch "main"

# 生成计划
openclaw plan <case_id>

# 开始开发！
```

让我们用 OpenClaw 开发 OpenClaw！
