# CLI 日志集成报告

## 完成时间
2026-03-05

## 集成内容

### 1. 日志模块初始化
在 `openclaw_cli/cli.py` 中：
- 导入 `get_logger` 函数
- 创建日志记录器实例：`logger = get_logger("openclaw.cli")`
- 配置日志文件输出到 `~/.openclaw/logs/cli.log`
- 自动创建日志目录

### 2. 日志记录点

#### create_case 命令
- `logger.info(f"创建案例: {title}")` - 记录案例创建开始
- `logger.info(f"案例已创建: {case.id}, 标题: {case.title}")` - 记录创建成功

#### plan 命令
- `logger.info(f"开始为案例 {case_id} 生成实现计划")` - 记录计划生成开始
- `logger.error(f"案例不存在: {case_id}")` - 记录错误
- `logger.debug(f"调用 PlanningAgent，案例: {case_id}")` - 记录 Agent 调用
- `logger.info(f"计划已生成: {plan.id}, 任务数量: {len(response['tasks'])}")` - 记录成功
- `logger.error(f"生成计划失败: {e}", exc_info=True)` - 记录异常详情

#### code 命令
- `logger.info(f"开始为任务 {task_id} (案例: {case_id}) 生成代码")` - 记录代码生成开始
- `logger.error(f"案例不存在: {case_id}")` - 记录错误
- `logger.error(f"任务不存在: {task_id}")` - 记录错误
- `logger.debug(f"调用 CodingAgent，任务: {task_id}")` - 记录 Agent 调用
- `logger.info(f"代码已生成，补丁数量: {len(response['patches'])}")` - 记录成功
- `logger.error(f"生成代码失败: {e}", exc_info=True)` - 记录异常详情

#### test 命令
- `logger.info(f"开始为案例 {case_id} 生成测试建议")` - 记录测试生成开始
- `logger.error(f"案例不存在: {case_id}")` - 记录错误
- `logger.debug(f"调用 TestAgent，案例: {case_id}")` - 记录 Agent 调用
- `logger.info(f"测试建议已生成，问题数: {len(response['potential_issues'])}, 测试用例数: {len(response['test_cases'])}")` - 记录成功
- `logger.error(f"生成测试建议失败: {e}", exc_info=True)` - 记录异常详情

## 日志文件位置

```
~/.openclaw/logs/cli.log
```

日志文件会自动轮转（按大小，默认 10MB，保留 5 个备份）。

## 日志级别

- **INFO**: 记录关键操作（创建案例、生成计划、生成代码等）
- **DEBUG**: 记录详细调试信息（Agent 调用等）
- **ERROR**: 记录错误和异常（包含完整堆栈信息）

## 使用示例

### 查看日志文件
```bash
# Windows
type %USERPROFILE%\.openclaw\logs\cli.log

# Linux/Mac
cat ~/.openclaw/logs/cli.log
```

### 实时查看日志
```bash
# Windows PowerShell
Get-Content %USERPROFILE%\.openclaw\logs\cli.log -Wait -Tail 50

# Linux/Mac
tail -f ~/.openclaw/logs/cli.log
```

## 测试验证

✅ **CLI 日志集成测试通过**
```python
from openclaw_cli.cli import logger
logger.info('CLI 日志集成测试')
```

✅ **所有单元测试通过** (21 passed)

## 优势

1. **可追溯性**: 所有 CLI 操作都有完整日志记录
2. **调试友好**: 错误信息包含完整堆栈跟踪
3. **性能监控**: 可以分析操作耗时和频率
4. **问题排查**: 通过日志快速定位问题
5. **审计支持**: 记录所有关键操作，便于审计

## 下一步

- [ ] 添加日志查询命令（`openclaw logs`）
- [ ] 在 Web 控制台中显示日志
- [ ] 添加日志级别配置选项
- [ ] 支持日志过滤和搜索
