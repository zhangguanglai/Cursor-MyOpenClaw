# 案例状态说明

## 支持的状态

系统定义了 **6 个案例状态**：

1. **`created`** - 已创建（默认状态）
2. **`planning`** - 规划中
3. **`coding`** - 编码中
4. **`testing`** - 测试中
5. **`completed`** - 已完成
6. **`cancelled`** - 已取消

## 状态转换流程

```
created (已创建)
  ↓ 点击"生成计划"
planning (规划中)
  ↓ 开始生成代码补丁
coding (编码中)
  ↓ 生成测试建议
testing (测试中)
  ↓ 所有任务完成，测试通过
completed (已完成)
```

或者：

```
任何状态
  ↓ 用户取消
cancelled (已取消)
```

## 当前实现状态

### ✅ 已实现的状态转换

1. **创建案例** → `created`
   - 位置：`CaseManager.create_case()`
   - 默认状态为 `created`

2. **生成计划** → `planning`
   - 位置：`CaseManager.save_plan()`
   - 当保存计划时，自动更新状态为 `planning`

3. **生成测试** → `testing`
   - 位置：`testing.py` 的 `generate_test()`
   - 当生成测试建议时，自动更新状态为 `testing`

### ❌ 未实现的状态转换

1. **开始编码** → `coding`
   - 应该在生成第一个代码补丁时更新
   - 当前：生成补丁时只更新任务状态，不更新案例状态

2. **完成所有任务** → `completed`
   - 应该在所有任务完成且测试通过时更新
   - 当前：没有自动检测逻辑

3. **取消案例** → `cancelled`
   - 应该提供手动取消功能
   - 当前：没有实现

## 状态显示

前端 `RequirementCenter.tsx` 中已支持显示所有状态：

- **已创建** (`created`) - 灰色标签
- **规划中** (`planning`) - 蓝色标签（processing）
- **编码中** (`coding`) - 蓝色标签（processing）
- **测试中** (`testing`) - 橙色标签（warning）
- **已完成** (`completed`) - 绿色标签（success）
- **已取消** (`cancelled`) - 灰色标签（default）

## 建议的状态转换逻辑

### 1. 编码阶段自动更新

在 `coding.py` 的 `generate_code()` 中：

```python
# 检查案例当前状态
if case.status == "planning":
    # 第一次生成代码补丁时，更新为 coding
    case_manager.update_case_status(case_id, "coding")
```

### 2. 完成状态自动更新

在任务完成时检查：

```python
# 检查所有任务是否完成
all_tasks = case_manager.get_tasks(case_id)
if all(task.status == "completed" for task in all_tasks):
    # 所有任务完成，更新为 completed
    case_manager.update_case_status(case_id, "completed")
```

### 3. 手动取消功能

添加 API 端点：

```python
@router.put("/{case_id}/cancel")
async def cancel_case(case_id: str, ...):
    """取消案例"""
    case_manager.update_case_status(case_id, "cancelled")
```

## 状态转换时机总结

| 操作 | 当前状态 | 更新后状态 | 实现状态 |
|------|---------|-----------|---------|
| 创建案例 | - | `created` | ✅ 已实现 |
| 生成计划 | `created` | `planning` | ✅ 已实现 |
| 生成第一个补丁 | `planning` | `coding` | ❌ 未实现 |
| 生成测试建议 | `coding` | `testing` | ✅ 已实现 |
| 所有任务完成 | `testing` | `completed` | ❌ 未实现 |
| 手动取消 | 任何状态 | `cancelled` | ❌ 未实现 |

## 下一步改进

1. **完善状态自动转换**：
   - 在生成代码补丁时自动更新为 `coding`
   - 在所有任务完成时自动更新为 `completed`

2. **添加手动状态管理**：
   - 在案例详情页添加状态选择器
   - 允许手动更新状态（特别是 `completed` 和 `cancelled`）

3. **状态过滤功能**：
   - 在需求中心添加状态筛选器
   - 可以按状态查看案例列表
