# 重复案例问题解决方案

## 🔍 问题原因

出现两个相同标题但不同 ID 的案例是因为：

1. **案例 ID 生成机制**
   - 系统使用 `uuid.uuid4().hex[:8]` 生成唯一 ID
   - 每次创建都会生成新的 ID，即使标题相同

2. **没有重复检测**
   - 原系统设计允许创建相同标题的案例
   - 适用于需要创建多个相似但不同案例的场景

3. **可能的原因**
   - 脚本被运行了两次
   - 前端和后端同时创建
   - 网络重试导致重复创建

## ✅ 已实施的解决方案

### 1. 添加重复检测机制

**文件**: `openclaw_studio/case_manager.py`

```python
def create_case(..., check_duplicate: bool = True):
    # 检查是否已存在相同标题的案例
    if check_duplicate:
        existing_cases = self.db.list_cases()
        for case in existing_cases:
            if case.title == title and case.status != "archived":
                logger.warning(f"已存在相同标题的案例: {case.id}")
                return case  # 返回现有案例而不是创建新的
```

**行为**：
- 默认启用重复检测（`check_duplicate=True`）
- 如果发现相同标题的案例（非归档状态），返回现有案例
- 避免创建重复案例

### 2. 添加案例删除功能

**文件**: 
- `openclaw_studio/database.py` - 添加 `delete_case` 方法
- `openclaw_studio/case_manager.py` - 添加 `delete_case` 方法
- `openclaw_studio/api/v1/cases.py` - 添加 `DELETE /api/v1/cases/{case_id}` 端点

**功能**：
- 删除案例及其所有关联数据
- 删除数据库记录（cases, plans, tasks, patches, test_records, agent_runs）
- 删除文件存储目录

**API 端点**：
```http
DELETE /api/v1/cases/{case_id}
```

### 3. 创建删除脚本

**文件**: `scripts/delete_case.py`

```bash
# 删除案例
python scripts/delete_case.py case-2a73c7be
```

## 📊 处理结果

### 已删除重复案例
- ✅ `case-2a73c7be` - 已删除（较早创建的重复案例）
- ✅ 保留 `case-e13da6ed` - 较新创建的案例

### 当前状态
- 系统现在会自动检测重复案例
- 如果尝试创建相同标题的案例，会返回现有案例
- 可以通过 API 或脚本删除不需要的案例

## 🎯 使用建议

### 创建案例时
- 系统会自动检测重复
- 如果存在相同标题的案例，会返回现有案例
- 如果需要强制创建，可以设置 `check_duplicate=False`（不推荐）

### 删除案例时
```bash
# 使用脚本删除
python scripts/delete_case.py <case_id>

# 或使用 API
curl -X DELETE http://localhost:8000/api/v1/cases/<case_id>
```

## ⚠️ 注意事项

1. **删除操作不可逆**
   - 删除案例会同时删除所有关联数据
   - 包括计划、任务、补丁、测试记录等
   - 请谨慎操作

2. **重复检测规则**
   - 只检查标题是否相同
   - 不检查描述内容
   - 已归档的案例不参与重复检测

3. **未来改进**
   - 可以考虑添加前端提示："已存在相同标题的案例，是否继续创建？"
   - 可以添加案例合并功能
   - 可以添加更智能的重复检测（检查标题和描述）

---

**实施时间**: 2026-03-06  
**相关案例**: `case-2a73c7be` (已删除), `case-e13da6ed` (保留)
