# 服务状态报告

## 🚀 服务启动情况

### 后端 API 服务
- **状态**: ✅ 已启动（后台运行）
- **地址**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **启动命令**: `python start_backend.py`

### 前端开发服务器
- **状态**: ✅ 已启动（后台运行）
- **地址**: http://localhost:5173
- **启动命令**: `cd openclaw-studio-frontend && npm run dev`

## 📋 快速测试

### 1. 检查后端服务
```bash
# 方式1: 使用测试脚本
python test_integration.py

# 方式2: 使用浏览器
# 访问 http://localhost:8000/health
# 应该看到: {"status": "healthy", "timestamp": "..."}
```

### 2. 检查前端服务
```bash
# 使用浏览器访问
# http://localhost:5173
# 应该看到 OpenClaw Studio 首页
```

### 3. 测试完整流程
1. 访问 http://localhost:5173/cases
2. 点击"创建案例"按钮
3. 填写表单并提交
4. 查看案例列表
5. 点击案例进入详情页
6. 测试生成计划功能

## 🔧 服务管理

### 停止服务

#### Windows PowerShell
```powershell
# 查找进程
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*node*"}

# 停止 Python 进程（后端）
Get-Process python | Stop-Process

# 停止 Node 进程（前端）
Get-Process node | Stop-Process
```

#### 手动停止
- 后端: 在运行 `start_backend.py` 的终端按 `Ctrl+C`
- 前端: 在运行 `npm run dev` 的终端按 `Ctrl+C`

### 重启服务

```bash
# 重启后端
python start_backend.py

# 重启前端
cd openclaw-studio-frontend
npm run dev
```

## 📊 服务日志

### 后端日志
后端服务会在终端输出日志，包括：
- 请求日志
- 错误信息
- Agent 调用记录

### 前端日志
前端服务会在终端输出：
- Vite 构建信息
- HMR (Hot Module Replacement) 更新
- 错误信息

## 🐛 常见问题

### 1. 端口被占用

**后端 (8000)**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F
```

**前端 (5173)**
```bash
# Vite 会自动尝试下一个端口
# 或手动指定端口
npm run dev -- --port 5174
```

### 2. 无法连接到后端

- 检查后端服务是否正在运行
- 检查防火墙设置
- 确认端口 8000 未被占用

### 3. CORS 错误

- 确认后端 CORS 配置正确（`openclaw_studio/api/main.py`）
- 检查前端 `.env` 文件中的 `VITE_API_BASE_URL`

### 4. API Key 错误

- 检查环境变量是否设置
- 确认 API Key 是否有效
- 查看后端日志中的错误信息

## 📝 测试清单

- [ ] 后端健康检查通过
- [ ] 前端页面正常加载
- [ ] 可以创建案例
- [ ] 可以查看案例列表
- [ ] 可以生成计划
- [ ] 可以查看补丁
- [ ] 可以生成测试建议
- [ ] 可以查看历史记录

---

**最后更新**: 2026-03-05 19:50:00
