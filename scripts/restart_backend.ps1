# 重启后端服务脚本
# 确保环境变量已设置并启动后端服务

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "重启 OpenClaw Studio 后端服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置环境变量
$env:QWEN_API_KEY = "sk-fe321dca0bf146ca99df33876ad56bbb"
Write-Host "[1/3] 环境变量已设置" -ForegroundColor Green
Write-Host "   QWEN_API_KEY: $($env:QWEN_API_KEY.Substring(0, 20))..." -ForegroundColor Gray
Write-Host ""

# 检查端口占用
Write-Host "[2/3] 检查端口 8000..." -ForegroundColor Yellow
$port8000 = netstat -ano | findstr ":8000" | findstr "LISTENING"
if ($port8000) {
    Write-Host "   发现端口 8000 被占用" -ForegroundColor Yellow
    Write-Host "   请手动停止现有的后端服务（Ctrl+C）" -ForegroundColor Yellow
    Write-Host "   或运行: Get-Process python | Stop-Process" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   等待 5 秒后继续..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
} else {
    Write-Host "   端口 8000 可用" -ForegroundColor Green
}
Write-Host ""

# 启动后端服务
Write-Host "[3/3] 启动后端服务..." -ForegroundColor Yellow
Write-Host "   工作目录: $(Get-Location)" -ForegroundColor Gray
Write-Host "   命令: python start_backend.py" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "后端服务正在启动..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "提示: 服务将在新窗口中启动" -ForegroundColor Yellow
Write-Host "     请在新窗口中查看启动日志" -ForegroundColor Yellow
Write-Host ""

# 在新窗口中启动
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; `$env:QWEN_API_KEY='sk-fe321dca0bf146ca99df33876ad56bbb'; python start_backend.py"

Write-Host "✅ 后端服务已在新窗口中启动" -ForegroundColor Green
Write-Host ""
Write-Host "验证服务:" -ForegroundColor Cyan
Write-Host "  访问: http://localhost:8000/health" -ForegroundColor Gray
Write-Host "  API文档: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
