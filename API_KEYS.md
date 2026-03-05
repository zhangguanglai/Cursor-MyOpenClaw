# API Keys 配置指南

## 🔑 当前配置

### Qwen API Key
- **环境变量名**: `QWEN_API_KEY`
- **当前值**: `sk-fe321dca0bf146ca99df33876ad56bbb` (Qwen 3.5)
- **用途**: 用于 planning、coding、summary 任务

### MiniMax API Key
- **环境变量名**: `MINIMAX_API_KEY`
- **用途**: 用于 coding 任务（备选）

---

## 📝 设置方法

### Windows PowerShell（当前会话）

```powershell
# 设置 Qwen API Key
$env:QWEN_API_KEY="sk-sp-5d0278696a1347ad92725d9552182fd9"

# 设置 MiniMax API Key（可选）
$env:MINIMAX_API_KEY="your_minimax_api_key"

# 验证设置
echo $env:QWEN_API_KEY
```

### Windows PowerShell（永久设置）

```powershell
# 永久设置 Qwen API Key（需要重启终端）
[System.Environment]::SetEnvironmentVariable('QWEN_API_KEY', 'sk-sp-5d0278696a1347ad92725d9552182fd9', 'User')

# 永久设置 MiniMax API Key（可选）
[System.Environment]::SetEnvironmentVariable('MINIMAX_API_KEY', 'your_minimax_api_key', 'User')
```

### Linux/Mac

```bash
# 当前会话
export QWEN_API_KEY="sk-sp-5d0278696a1347ad92725d9552182fd9"
export MINIMAX_API_KEY="your_minimax_api_key"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export QWEN_API_KEY="sk-sp-5d0278696a1347ad92725d9552182fd9"' >> ~/.bashrc
echo 'export MINIMAX_API_KEY="your_minimax_api_key"' >> ~/.bashrc
source ~/.bashrc
```

---

## ✅ 验证配置

### 方法 1: 使用 Python 验证

```python
import os

qwen_key = os.environ.get("QWEN_API_KEY")
minimax_key = os.environ.get("MINIMAX_API_KEY")

if qwen_key:
    print(f"✅ QWEN_API_KEY: {qwen_key[:20]}...")
else:
    print("❌ QWEN_API_KEY 未设置")

if minimax_key:
    print(f"✅ MINIMAX_API_KEY: {minimax_key[:20]}...")
else:
    print("⚠️  MINIMAX_API_KEY 未设置（可选）")
```

### 方法 2: 使用 CLI 测试

```bash
# 运行测试脚本
python test_api.py

# 或运行示例
python examples/llm_router_example.py
```

---

## 🔒 安全建议

1. **不要提交 API Key 到 Git**
   - API Key 已添加到 `.gitignore`
   - 不要将 API Key 硬编码到代码中

2. **使用环境变量**
   - 始终通过环境变量配置 API Key
   - 配置文件（`config/llm.yml`）只引用环境变量名

3. **定期轮换**
   - 定期更新 API Key
   - 如果泄露，立即更换

4. **限制权限**
   - 使用最小权限原则
   - 只授予必要的 API 权限

---

## 📋 更新记录

### 2026-03-05
- 更新 Qwen API Key: `sk-fe321dca0bf146ca99df33876ad56bbb` (Qwen 3.5，第三次更新)
- 之前: `sk-sp-59e0db34e07b42a4932b596212d03ee5` (已失效)
- 更早: `sk-sp-5d0278696a1347ad92725d9552182fd9` (已失效)

---

## 🆘 常见问题

### Q: 如何更新 API Key？
A: 使用上述方法设置新的环境变量值即可。

### Q: API Key 设置后仍然报错？
A: 
1. 确认环境变量已正确设置（使用验证方法）
2. 重启终端/IDE
3. 检查 API Key 是否有效

### Q: 如何在 CI/CD 中配置？
A: 在 GitHub Actions 等 CI 平台中，通过 Secrets 配置环境变量。

---

## 📚 相关文档

- `config/llm.yml` - LLM 配置文件
- `openclaw_core/llm_router.py` - LLMRouter 实现
- `README.md` - 项目 README
