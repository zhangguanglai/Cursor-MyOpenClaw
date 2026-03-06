# 后端服务重启指南

## 🔴 问题说明

如果"生成计划"功能失败，通常是因为后端服务在启动时没有读取到 `QWEN_API_KEY` 环境变量。

**原因**：后端服务使用单例模式创建 `LLMRouter`，在服务启动时初始化。如果此时环境变量未设置，即使后来设置了环境变量，已创建的实例也不会重新读取。

## ✅ 解决方案

### 方法 1: 使用重启脚本（推荐）

1. **停止后端服务**
   ```powershell
   .\scripts\stop_backend.ps1
   ```

2. **重启后端服务**
   ```powershell
   .\scripts\restart_backend.ps1
   ```

### 方法 2: 手动重启

1. **停止后端服务**
   - 找到运行后端服务的终端窗口
   - 按 `Ctrl+C` 停止服务

2. **设置环境变量并启动**
   ```powershell
   # 设置 API Key
   $env:QWEN_API_KEY='sk-fe321dca0bf146ca99df33876ad56bbb'
   
   # 启动后端服务
   python start_backend.py
   ```

### 方法 3: 永久设置环境变量

如果希望每次启动时自动加载环境变量：

**Windows PowerShell（永久设置）**:
```powershell
[System.Environment]::SetEnvironmentVariable('QWEN_API_KEY', 'sk-fe321dca0bf146ca99df33876ad56bbb', 'User')
```

设置后需要：
1. 重启终端/IDE
2. 重启后端服务

## 🔍 验证步骤

重启后端服务后，验证配置：

1. **检查服务是否运行**
   ```powershell
   # 访问健康检查端点
   # 浏览器: http://localhost:8000/health
   ```

2. **测试规划 API**
   ```powershell
   python scripts/debug_planning_api.py case-e13da6ed
   ```

3. **在前端测试**
   - 访问: http://localhost:5174/cases/case-e13da6ed/plan
   - 点击"生成计划"按钮
   - 应该能正常生成计划

## 📋 检查清单

重启前：
- [ ] 确认已设置 `QWEN_API_KEY` 环境变量
- [ ] 停止现有后端服务
- [ ] 等待端口 8000 释放

重启后：
- [ ] 后端服务正常启动（无错误）
- [ ] 健康检查返回 200
- [ ] 规划 API 测试通过
- [ ] 前端可以正常生成计划

## 🐛 常见问题

### Q: 重启后仍然失败？

**A**: 检查以下几点：
1. 环境变量是否在启动后端服务的终端中设置
2. 后端服务启动日志中是否有错误
3. API Key 是否正确（运行 `python scripts/test_llm_connection.py`）

### Q: 如何确认环境变量已加载？

**A**: 在后端服务启动时，查看日志。如果看到：
```
成功初始化 Provider: qwen
```
说明环境变量已正确加载。

### Q: 可以不用重启吗？

**A**: 由于使用了单例模式，必须重启后端服务才能重新读取环境变量。这是设计上的限制，确保服务启动时配置正确。

## 📝 最佳实践

1. **启动前设置环境变量**
   - 在启动后端服务之前，先设置环境变量
   - 使用脚本自动设置（如 `restart_backend.ps1`）

2. **使用启动脚本**
   - 使用提供的脚本启动服务，确保环境变量正确设置

3. **永久配置（可选）**
   - 如果经常使用，可以永久设置环境变量
   - 但要注意安全性，不要将 API Key 提交到 Git

---

**最后更新**: 2026-03-06
