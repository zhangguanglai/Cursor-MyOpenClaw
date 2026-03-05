# 启动 OpenClaw Studio 前后端服务

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动 OpenClaw Studio 服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查后端服务是否已在运行
$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $backendRunning = $true
        Write-Host "✅ 后端服务已在运行 (http://localhost:8000)" -ForegroundColor Green
    }
} catch {
    $backendRunning = $false
}

# 检查前端服务是否已在运行
$frontendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $frontendRunning = $true
        Write-Host "✅ 前端服务已在运行 (http://localhost:5173)" -ForegroundColor Green
    }
} catch {
    $frontendRunning = $false
}

# 启动后端服务
if (-not $backendRunning) {
    Write-Host "启动后端服务..." -ForegroundColor Yellow
    $backendScript = Join-Path $PSScriptRoot "start_backend.py"
    Start-Process python -ArgumentList $backendScript -WindowStyle Normal
    Write-Host "✅ 后端服务启动命令已执行" -ForegroundColor Green
    Write-Host "   后端地址: http://localhost:8000" -ForegroundColor Gray
    Write-Host "   API 文档: http://localhost:8000/docs" -ForegroundColor Gray
} else {
    Write-Host "后端服务已在运行，跳过启动" -ForegroundColor Gray
}

# 等待后端启动
Start-Sleep -Seconds 3

# 启动前端服务
if (-not $frontendRunning) {
    Write-Host "启动前端服务..." -ForegroundColor Yellow
    $frontendDir = Join-Path $PSScriptRoot "openclaw-studio-frontend"
    Push-Location $frontendDir
    Start-Process npm -ArgumentList "run", "dev" -WindowStyle Normal
    Pop-Location
    Write-Host "✅ 前端服务启动命令已执行" -ForegroundColor Green
    Write-Host "   前端地址: http://localhost:5173" -ForegroundColor Gray
} else {
    Write-Host "前端服务已在运行，跳过启动" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "服务启动完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "后端 API: http://localhost:8000" -ForegroundColor White
Write-Host "API 文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host "前端界面: http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "提示: 服务已在新的窗口中启动" -ForegroundColor Yellow
Write-Host "     关闭窗口即可停止对应的服务" -ForegroundColor Yellow
Write-Host ""
