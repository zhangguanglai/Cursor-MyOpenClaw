# 规划视图白屏问题修复

## 🔍 问题分析

### 发现的问题
- 规划视图页面显示空白（白屏）
- 可能原因：
  1. API 调用失败导致组件崩溃
  2. 缺少错误处理
  3. 404 错误未正确处理
  4. 组件渲染错误

## ✅ 已实施的修复

### 1. 错误处理改进

**文件**: `openclaw-studio-frontend/src/features/planning/PlanningView.tsx`

- ✅ 添加案例加载错误处理
- ✅ 添加计划加载错误处理
- ✅ 添加案例 ID 验证
- ✅ 添加友好的错误提示

### 2. API 查询优化

**文件**: `openclaw-studio-frontend/src/services/planning.ts`

- ✅ 处理 404 错误（计划不存在）
- ✅ 返回 null 而不是抛出错误
- ✅ 禁用重试（404 不需要重试）

### 3. 数据初始化改进

**文件**: `openclaw-studio-frontend/src/features/planning/PlanningView.tsx`

- ✅ 添加空值检查
- ✅ 处理 planData 为 null 的情况
- ✅ 处理 tasks 为空数组的情况
- ✅ 重置状态当 planData 为 null

### 4. 组件清理

- ✅ 移除未使用的 `PlanRenderer` 导入
- ✅ 添加控制台错误日志
- ✅ 改进错误消息

## 📊 修复内容

### 错误处理
```typescript
// 案例加载错误
if (caseError) {
  return <Alert message="加载案例失败" ... />
}

// 案例 ID 验证
if (!caseId) {
  return <Alert message="案例 ID 不存在" ... />
}

// 计划加载错误
if (planError) {
  return <Alert message="加载计划失败" ... />
}
```

### API 查询优化
```typescript
queryFn: async () => {
  try {
    const response = await apiClient.get(`/api/v1/cases/${caseId}/plan`);
    return response.data;
  } catch (error: any) {
    // 如果是 404，说明计划不存在，返回 null 而不是抛出错误
    if (error.response?.status === 404) {
      return null;
    }
    throw error;
  }
}
```

### 数据初始化
```typescript
useEffect(() => {
  if (planData) {
    setEditingMarkdown(planData.plan_markdown || '')
    setTasks((planData.tasks || []).map(...))
  } else {
    // 如果没有计划数据，重置状态
    setEditingMarkdown('')
    setTasks([])
  }
}, [planData])
```

## 🎯 修复效果

### 修复前
- ❌ 白屏（无任何内容）
- ❌ 无错误提示
- ❌ API 错误导致组件崩溃

### 修复后
- ✅ 显示友好的错误提示
- ✅ 显示加载状态
- ✅ 正确处理计划不存在的情况
- ✅ 用户可以重试或返回需求中心

## 📝 相关文件

- `openclaw-studio-frontend/src/features/planning/PlanningView.tsx` - 规划视图组件（已修复）
- `openclaw-studio-frontend/src/services/planning.ts` - 规划 API Hooks（已优化）

## ✅ 完成标准

- ✅ 错误处理添加完成
- ✅ API 查询优化完成
- ✅ 数据初始化改进完成
- ✅ 组件清理完成

**当前状态**: 规划视图白屏问题已修复，现在会显示友好的错误提示和加载状态。
