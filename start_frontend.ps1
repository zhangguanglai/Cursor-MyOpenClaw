# 启动前端开发服务器

Write-Host "=" * 60
Write-Host "启动 OpenClaw Studio 前端开发服务器"
Write-Host "=" * 60
Write-Host ""

# 检查是否在正确的目录
if (-not (Test-Path "openclaw-studio-frontend")) {
    Write-Host "错误: 未找到 openclaw-studio-frontend 目录"
    Write-Host "请确保在项目根目录运行此脚本"
    exit 1
}

# 切换到前端目录
Set-Location openclaw-studio-frontend

# 检查 node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "检测到 node_modules 不存在，正在安装依赖..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "依赖安装失败"
        exit 1
    }
}

# 启动开发服务器
Write-Host ""
Write-Host "启动开发服务器..."
Write-Host "前端地址: http://localhost:5173"
Write-Host "按 Ctrl+C 停止服务器"
Write-Host ""

npm run dev
