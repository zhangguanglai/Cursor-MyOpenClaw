# 前端服务故障排查

## 🔍 快速检查

### 1. 检查前端服务是否运行

```powershell
# 检查端口 5173
netstat -ano | findstr ":5173" | findstr "LISTENING"

# 检查 node 进程
Get-Process node -ErrorAction SilentlyContinue
```

### 2. 访问前端

- **本地访问**: http://localhost:5173
- **网络访问**: http://127.0.0.1:5173

## 🐛 常见问题

### 问题 1: 前端服务未启动

#### 症状
- 浏览器无法访问 http://localhost:5173
- 显示"无法连接"或"连接被拒绝"

#### 解决方案

1. **进入前端目录**
   ```powershell
   cd D:\MyWorkspace\Causor-MyOpenClaw\openclaw-studio-frontend
   ```

2. **安装依赖（如果未安装）**
   ```powershell
   npm install
   ```

3. **启动开发服务器**
   ```powershell
   npm run dev
   ```

4. **或使用启动脚本**
   ```powershell
   .\scripts\start_frontend.ps1
   ```

### 问题 2: 端口被占用

#### 症状
- 启动时显示 "Port 5173 is already in use"
- 或启动失败

#### 解决方案

1. **查找占用端口的进程**
   ```powershell
   netstat -ano | findstr ":5173"
   ```

2. **停止占用端口的进程**
   ```powershell
   # 找到进程 ID 后
   Stop-Process -Id <进程ID>
   ```

3. **或使用其他端口**
   ```powershell
   # 修改 vite.config.ts 或使用环境变量
   $env:PORT=5174
   npm run dev
   ```

### 问题 3: 依赖未安装

#### 症状
- 启动时显示 "Cannot find module"
- 或构建错误

#### 解决方案

```powershell
cd D:\MyWorkspace\Causor-MyOpenClaw\openclaw-studio-frontend
npm install
```

### 问题 4: 页面空白或错误

#### 症状
- 页面可以访问，但显示空白
- 浏览器控制台有错误

#### 解决方案

1. **打开浏览器开发者工具** (F12)
2. **查看 Console 标签页**，检查错误信息
3. **查看 Network 标签页**，检查资源加载情况
4. **检查后端服务**是否正常运行

### 问题 5: API 连接失败

#### 症状
- 页面可以访问，但无法加载数据
- 控制台显示 API 请求失败

#### 解决方案

1. **检查后端服务**
   ```powershell
   # 检查后端是否运行
   netstat -ano | findstr ":8000"
   
   # 测试后端 API
   curl http://localhost:8000/health
   ```

2. **检查 API 配置**
   - 查看 `openclaw-studio-frontend/.env` 文件
   - 确保 `VITE_API_BASE_URL=http://localhost:8000`

3. **重启后端服务**
   ```powershell
   .\scripts\restart_backend.ps1
   ```

## 🚀 启动步骤

### 完整启动流程

1. **启动后端服务**
   ```powershell
   # 设置 API Key
   $env:QWEN_API_KEY='sk-fe321dca0bf146ca99df33876ad56bbb'
   
   # 启动后端
   python start_backend.py
   ```

2. **启动前端服务**（新终端）
   ```powershell
   cd D:\MyWorkspace\Causor-MyOpenClaw\openclaw-studio-frontend
   npm run dev
   ```

3. **访问前端**
   - 打开浏览器访问: http://localhost:5173

## 📋 验证清单

- [ ] 后端服务正在运行（端口 8000）
- [ ] 前端服务正在运行（端口 5173）
- [ ] 浏览器可以访问 http://localhost:5173
- [ ] 浏览器控制台没有错误
- [ ] API 请求正常（Network 标签页）

## 🔧 调试技巧

### 1. 查看前端日志

前端服务启动后，会在终端显示：
- 服务地址
- 编译信息
- 错误信息

### 2. 查看浏览器控制台

按 F12 打开开发者工具：
- **Console**: JavaScript 错误和日志
- **Network**: API 请求和响应
- **Elements**: HTML 结构

### 3. 清除缓存

如果页面显示异常，尝试：
- 硬刷新: `Ctrl + Shift + R` 或 `Ctrl + F5`
- 清除浏览器缓存
- 清除 localStorage

## 📞 获取帮助

如果以上方法都无法解决问题：

1. **收集错误信息**
   - 浏览器控制台错误
   - 前端服务终端输出
   - 后端服务日志

2. **检查相关文档**
   - [用户使用指南](USER_GUIDE.md)
   - [故障排查指南](TROUBLESHOOTING.md)

---

**最后更新**: 2026-03-06
