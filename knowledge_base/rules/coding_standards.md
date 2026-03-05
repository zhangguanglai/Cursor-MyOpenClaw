# 代码风格与提交规范

## 代码风格

### Python

- 遵循 PEP 8 代码风格
- 使用类型提示（Type Hints）
- 函数和类必须有文档字符串
- 使用 4 个空格缩进
- 行长度不超过 100 字符

### TypeScript/JavaScript

- 使用 ESLint 和 Prettier
- 使用 TypeScript 类型定义
- 函数和组件必须有 JSDoc 注释
- 使用 2 个空格缩进

## 提交规范

### 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例

```
feat(api): Add Git integration endpoints

- Add GET /api/v1/cases/{id}/git-status
- Add GET /api/v1/cases/{id}/git-diff
- Add tests for Git API endpoints

Closes #123
```

## 代码审查

- 所有代码变更必须经过审查
- 确保测试覆盖
- 确保文档更新
