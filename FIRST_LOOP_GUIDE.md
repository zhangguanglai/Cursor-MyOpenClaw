# 第一个完整闭环指南

## 选择一个真实需求

我们选择一个简单但真实的需求来跑通第一个完整闭环：

### 需求：为 OpenClaw Core 添加日志记录功能

**需求描述**：
```
为 OpenClaw Core 添加一个简单的日志记录功能：
- 支持不同日志级别（DEBUG, INFO, WARNING, ERROR）
- 可以输出到控制台和文件
- 支持日志轮转（按大小或时间）
- 使用 Python 标准库 logging 模块，不引入新依赖
- 性能影响最小
```

**验收标准**：
- [ ] 可以通过配置启用/禁用日志
- [ ] 日志文件可以自动轮转（按大小或时间）
- [ ] 所有现有测试通过
- [ ] 代码符合项目规范

---

## 完整流程步骤

### 1. 创建案例

```bash
python -m openclaw_cli.cli create-case "添加日志记录功能" \
  --description "为 OpenClaw Core 添加日志记录功能，支持多级别、文件输出和日志轮转" \
  --repo "." \
  --branch "main"
```

### 2. 查看案例列表

```bash
python -m openclaw_cli.cli list-cases
```

### 3. 生成实现计划

```bash
# 获取案例 ID（从 list-cases 输出）
python -m openclaw_cli.cli plan <case-id>
```

### 4. 查看计划

```bash
python -m openclaw_cli.cli show-plan <case-id>
```

### 5. 查看任务列表

```bash
python -m openclaw_cli.cli show-tasks <case-id>
```

### 6. 为任务生成代码

```bash
# 获取任务 ID（从 show-tasks 输出）
python -m openclaw_cli.cli code <case-id> <task-id>
```

### 7. 生成测试建议

```bash
python -m openclaw_cli.cli test <case-id>
```

### 8. 查看测试建议

测试建议会保存在 `cases/<case-id>/tests/` 目录下。

---

## 注意事项

1. **需要配置 API Key**：
   ```bash
   # Windows PowerShell
   $env:QWEN_API_KEY="your_api_key"
   $env:MINIMAX_API_KEY="your_api_key"
   ```

2. **首次运行会创建数据库**：
   - 数据库文件：`openclaw_studio.db`
   - 案例目录：`cases/`

3. **查看生成的文件**：
   - 计划：`cases/<case-id>/plan.md`
   - 补丁：`cases/<case-id>/patches/`
   - 测试：`cases/<case-id>/tests/`

---

## 预期结果

完成闭环后，你应该有：
- ✅ 一个完整的实现计划
- ✅ 多个代码补丁文件
- ✅ 测试建议和验收清单
- ✅ 所有文件都保存在案例目录中
- ✅ 数据库中有完整的记录

---

## 下一步

完成第一个闭环后：
1. 查看生成的文件，评估质量
2. 记录问题和改进点
3. 优化 CLI 和 Agent
4. 开始第二个闭环
