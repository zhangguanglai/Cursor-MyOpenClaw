# OpenClaw CLI 使用指南

## ✅ 已完成功能

### 1. 案例库结构
- ✅ SQLite 数据库（`openclaw_studio.db`）
- ✅ 文件系统存储（`cases/` 目录）
- ✅ 完整的案例管理 API

### 2. CLI 命令
- ✅ `create-case` - 创建新需求案例
- ✅ `list-cases` - 列出所有案例
- ✅ `show-case` - 查看案例详情
- ✅ `plan` - 生成实现计划
- ✅ `show-plan` - 查看计划
- ✅ `show-tasks` - 查看任务列表
- ✅ `code` - 生成代码补丁
- ✅ `test` - 生成测试建议

## 🚀 快速开始

### 1. 配置 API Key

```powershell
# Windows PowerShell
$env:QWEN_API_KEY="your_api_key"
$env:MINIMAX_API_KEY="your_api_key"
```

### 2. 使用 CLI

```bash
# 创建案例
python -m openclaw_cli.cli create-case "需求标题" --description "需求描述"

# 列出案例
python -m openclaw_cli.cli list-cases

# 生成计划
python -m openclaw_cli.cli plan <case-id>

# 查看计划
python -m openclaw_cli.cli show-plan <case-id>

# 查看任务
python -m openclaw_cli.cli show-tasks <case-id>

# 生成代码
python -m openclaw_cli.cli code <case-id> <task-id>

# 生成测试建议
python -m openclaw_cli.cli test <case-id>
```

## 📁 文件结构

```
cases/
  <case-id>/
    plan.md              # 实现计划
    plan.json            # 结构化任务列表
    patches/             # 代码补丁
      <task-id>.patch
      <task-id>.meta.json
    tests/               # 测试建议
      suggestions.md
      checklist.md
    agent_runs/          # Agent 调用记录
      <run-id>_<type>_input.json
      <run-id>_<type>_output.json
    summary.md           # 案例总结
```

## 📝 第一个闭环示例

### 需求：添加日志记录功能

```bash
# 1. 创建案例
python -m openclaw_cli.cli create-case "添加日志记录功能" \
  --description "为 OpenClaw Core 添加日志记录功能，支持多级别、文件输出和日志轮转" \
  --repo "." \
  --branch "main"

# 2. 查看案例 ID（从输出中获取，例如：case-eca55ddc）
python -m openclaw_cli.cli list-cases

# 3. 生成计划
python -m openclaw_cli.cli plan case-eca55ddc

# 4. 查看计划
python -m openclaw_cli.cli show-plan case-eca55ddc

# 5. 查看任务列表
python -m openclaw_cli.cli show-tasks case-eca55ddc

# 6. 为第一个任务生成代码（从任务列表中获取 task-id）
python -m openclaw_cli.cli code case-eca55ddc <task-id>

# 7. 生成测试建议
python -m openclaw_cli.cli test case-eca55ddc
```

## ⚠️ 已知问题

1. **Windows 控制台编码问题**：
   - 某些中文字符可能无法正确显示
   - 建议使用 UTF-8 编码的终端或 IDE 终端

2. **需要配置 API Key**：
   - 必须设置 QWEN_API_KEY 或 MINIMAX_API_KEY
   - 否则 Agent 调用会失败

## 🔄 下一步

1. 修复 Windows 编码问题
2. 添加更多 CLI 命令（如 `summary`、`history`）
3. 实现 Web 控制台
4. 完善错误处理和用户提示

## 📚 相关文档

- `FIRST_LOOP_GUIDE.md` - 第一个闭环详细指南
- `NEXT_STEPS.md` - 下一步计划
- `docs/workflow.md` - 工作流文档
