# 故障排查指南

## 🔴 常见问题

### 问题 1: 点击"生成计划"没有生成

#### 症状
- 点击"生成计划"按钮后，显示"规划生成失败"
- 浏览器控制台显示 500 错误
- 后端日志显示错误

#### 可能原因

1. **LLM API Key 未配置**（最常见）
   - 错误信息：`LLM API Key 未配置。请设置环境变量 QWEN_API_KEY 或 MINIMAX_API_KEY。`
   - 解决方案：见下方"配置 API Key"

2. **网络连接问题**
   - 错误信息：`LLM API 网络错误`
   - 解决方案：检查网络连接，确保可以访问 LLM API

3. **API Key 无效**
   - 错误信息：`LLM API 调用失败: 401` 或 `403`
   - 解决方案：检查 API Key 是否正确，是否已过期

4. **后端服务未启动**
   - 错误信息：`无法连接到后端服务`
   - 解决方案：启动后端服务 `python start_backend.py`

#### 解决方案

##### 配置 API Key

**Windows PowerShell（当前会话）**:
```powershell
# 设置 Qwen API Key
$env:QWEN_API_KEY="your_qwen_api_key"

# 设置 MiniMax API Key（可选）
$env:MINIMAX_API_KEY="your_minimax_api_key"

# 验证设置
echo $env:QWEN_API_KEY
```

**Windows PowerShell（永久设置）**:
```powershell
# 永久设置（需要重启终端）
[System.Environment]::SetEnvironmentVariable('QWEN_API_KEY', 'your_qwen_api_key', 'User')
[System.Environment]::SetEnvironmentVariable('MINIMAX_API_KEY', 'your_minimax_api_key', 'User')
```

**Linux/Mac**:
```bash
# 当前会话
export QWEN_API_KEY="your_qwen_api_key"
export MINIMAX_API_KEY="your_minimax_api_key"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export QWEN_API_KEY="your_qwen_api_key"' >> ~/.bashrc
echo 'export MINIMAX_API_KEY="your_minimax_api_key"' >> ~/.bashrc
source ~/.bashrc
```

**重要提示**:
- 设置环境变量后，需要**重启后端服务**才能生效
- 如果使用 IDE 启动后端，也需要重启 IDE

##### 验证配置

运行以下命令验证 API Key 是否配置正确：

```bash
python scripts/test_llm_connection.py
```

或使用 Python 直接检查：

```python
import os
qwen_key = os.environ.get("QWEN_API_KEY")
if qwen_key:
    print(f"✅ QWEN_API_KEY: {qwen_key[:20]}...")
else:
    print("❌ QWEN_API_KEY 未设置")
```

### 问题 2: Git 状态显示 400 错误

#### 症状
- 规划视图或执行视图中，Git 状态卡片显示红色错误
- 错误信息：`无法获取 Git 状态: Request failed with status code 400`

#### 可能原因

1. **当前目录不是 Git 仓库**
   - 解决方案：在 Git 仓库根目录启动后端服务

2. **Git 仓库路径配置错误**
   - 解决方案：检查案例的 `repo_path` 配置

3. **Git 工具未安装**
   - 解决方案：安装 Git 并确保在 PATH 中

#### 解决方案

1. 确保在 Git 仓库根目录启动后端服务
2. 如果案例关联了特定的 Git 仓库，确保路径正确
3. 检查 Git 是否已安装：`git --version`

### 问题 3: 页面显示白屏

#### 症状
- 页面完全空白，没有任何内容
- 浏览器控制台显示 JavaScript 错误

#### 可能原因

1. **前端构建错误**
   - 解决方案：检查前端构建日志，修复错误

2. **API 连接失败**
   - 解决方案：确保后端服务正在运行

3. **路由错误**
   - 解决方案：检查 URL 是否正确

#### 解决方案

1. 打开浏览器开发者工具（F12）
2. 查看 Console 标签页的错误信息
3. 查看 Network 标签页的 API 请求
4. 根据错误信息修复问题

### 问题 4: 补丁生成失败

#### 症状
- 点击"生成补丁"后，显示错误信息
- 补丁列表为空

#### 可能原因

1. **任务信息不完整**
   - 解决方案：确保任务有完整的标题和描述

2. **LLM API Key 未配置**
   - 解决方案：见"问题 1"的解决方案

3. **网络问题**
   - 解决方案：检查网络连接

#### 解决方案

1. 检查任务信息是否完整
2. 检查 API Key 配置
3. 查看后端日志获取详细错误信息

### 问题 5: 测试建议生成失败

#### 症状
- 点击"生成测试建议"后，显示错误信息
- 测试结果为空

#### 可能原因

1. **没有可用的补丁**
   - 解决方案：先生成代码补丁

2. **LLM API Key 未配置**
   - 解决方案：见"问题 1"的解决方案

3. **网络问题**
   - 解决方案：检查网络连接

#### 解决方案

1. 确保已生成至少一个补丁
2. 检查 API Key 配置
3. 查看后端日志获取详细错误信息

## 🔍 调试方法

### 1. 检查后端日志

后端服务启动后，会在控制台输出日志。查看错误信息：

```bash
# 启动后端服务
python start_backend.py

# 查看日志输出
# 错误信息会显示在控制台
```

### 2. 检查浏览器控制台

1. 打开浏览器开发者工具（F12）
2. 切换到 Console 标签页
3. 查看错误信息

### 3. 检查网络请求

1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签页
3. 查看 API 请求的状态码和响应内容

### 4. 使用调试脚本

```bash
# 测试 LLM 连接
python scripts/test_llm_connection.py

# 测试规划 API
python scripts/debug_planning_api.py <case_id>

# 测试完整流程
python scripts/test_complete_workflow.py
```

## 📋 检查清单

遇到问题时，按以下清单检查：

- [ ] 后端服务是否正在运行？
- [ ] 前端服务是否正在运行？
- [ ] LLM API Key 是否已配置？
- [ ] 环境变量是否在正确的终端/IDE 中设置？
- [ ] 后端服务是否在设置环境变量后重启？
- [ ] 网络连接是否正常？
- [ ] 浏览器控制台是否有错误？
- [ ] 后端日志是否有错误信息？

## 🆘 获取帮助

如果以上方法都无法解决问题：

1. **查看详细日志**
   - 后端日志：启动后端服务的终端
   - 前端日志：浏览器控制台

2. **收集错误信息**
   - 错误消息
   - 堆栈跟踪
   - 相关配置

3. **检查相关文档**
   - [用户使用指南](USER_GUIDE.md)
   - [API 文档](http://localhost:8000/docs)
   - [API Keys 配置指南](../API_KEYS.md)

---

**最后更新**: 2026-03-06
