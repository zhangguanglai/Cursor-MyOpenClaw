# 服务启动状态

## ✅ 服务已成功启动

### 后端服务
- **状态**: ✅ 运行正常
- **地址**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 前端服务
- **状态**: ✅ 运行正常
- **地址**: http://localhost:5173

## 📝 启动说明

### 启动方式

#### 方式 1: 使用启动脚本（推荐）
```powershell
# 在项目根目录执行
python start_backend.py
```

```powershell
# 在 openclaw-studio-frontend 目录执行
npm run dev
```

#### 方式 2: 使用 PowerShell 脚本
```powershell
# 在项目根目录执行
.\start_services.ps1
```

### 停止服务

- **后端**: 在运行后端服务的终端窗口按 `Ctrl+C`
- **前端**: 在运行前端服务的终端窗口按 `Ctrl+C`

## 🔍 验证服务

### 检查后端服务
```bash
# 健康检查
curl http://localhost:8000/health

# API 文档
# 浏览器访问: http://localhost:8000/docs
```

### 检查前端服务
```bash
# 浏览器访问: http://localhost:5173
```

## 📊 服务信息

- **后端端口**: 8000
- **前端端口**: 5173
- **后端框架**: FastAPI (Uvicorn)
- **前端框架**: React + Vite

## ⚠️ 注意事项

1. 确保端口 8000 和 5173 未被其他程序占用
2. 后端服务需要 Python 环境和所有依赖包
3. 前端服务需要 Node.js 和 npm 环境
4. 首次启动前端需要运行 `npm install` 安装依赖

## 🐛 故障排查

### 后端服务无法启动
1. 检查 Python 环境是否正确
2. 检查依赖是否安装: `pip install -r requirements.txt`
3. 检查端口 8000 是否被占用
4. 查看后端启动日志中的错误信息

### 前端服务无法启动
1. 检查 Node.js 和 npm 是否安装
2. 检查依赖是否安装: `cd openclaw-studio-frontend && npm install`
3. 检查端口 5173 是否被占用
4. 查看前端启动日志中的错误信息

### 前后端无法通信
1. 检查后端 CORS 配置
2. 检查前端 API 地址配置
3. 检查防火墙设置

---

**最后更新**: 2026-03-06
