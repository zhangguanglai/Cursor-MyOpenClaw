# 启动前端服务脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动 OpenClaw Studio 前端服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$frontendDir = "D:\MyWorkspace\Causor-MyOpenClaw\openclaw-studio-frontend"

# 检查目录是否存在
if (-not (Test-Path $frontendDir)) {
    Write-Host "[错误] 前端目录不存在: $frontendDir" -ForegroundColor Red
    exit 1
}

Write-Host "[1/3] 检查前端目录..." -ForegroundColor Yellow
Write-Host "   目录: $frontendDir" -ForegroundColor Gray
Write-Host ""

# 检查 node_modules
Write-Host "[2/3] 检查依赖..." -ForegroundColor Yellow
$nodeModulesPath = Join-Path $frontendDir "node_modules"
if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "   node_modules 不存在，需要安装依赖" -ForegroundColor Yellow
    Write-Host "   正在安装依赖（这可能需要几分钟）..." -ForegroundColor Yellow
    Set-Location $frontendDir
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 依赖安装失败" -ForegroundColor Red
        exit 1
    }
    Write-Host "   ✅ 依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "   ✅ 依赖已安装" -ForegroundColor Green
}
Write-Host ""

# 检查端口占用
Write-Host "[3/3] 检查端口 5173..." -ForegroundColor Yellow
$port5173 = netstat -ano | findstr ":5173" | findstr "LISTENING"
if ($port5173) {
    Write-Host "   ⚠️  端口 5173 已被占用" -ForegroundColor Yellow
    Write-Host "   如果前端服务已在运行，请访问: http://localhost:5173" -ForegroundColor Gray
    Write-Host "   如果需要重启，请先停止现有服务" -ForegroundColor Gray
    Write-Host ""
    $continue = Read-Host "   是否继续启动? (y/n)"
    if ($continue -ne "y") {
        exit 0
    }
} else {
    Write-Host "   ✅ 端口 5173 可用" -ForegroundColor Green
}
Write-Host ""

# 启动前端服务
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动前端开发服务器..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服务地址: http://localhost:5173" -ForegroundColor Yellow
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Gray
Write-Host ""

Set-Location $frontendDir
npm run dev
