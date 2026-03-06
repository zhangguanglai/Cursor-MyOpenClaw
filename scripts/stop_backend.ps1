# 停止后端服务脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "停止 OpenClaw Studio 后端服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 查找占用端口 8000 的进程
Write-Host "[1/2] 查找占用端口 8000 的进程..." -ForegroundColor Yellow
$portInfo = netstat -ano | findstr ":8000" | findstr "LISTENING"
if ($portInfo) {
    $pid = ($portInfo -split '\s+')[-1]
    Write-Host "   找到进程 ID: $pid" -ForegroundColor Gray
    
    try {
        $process = Get-Process -Id $pid -ErrorAction Stop
        Write-Host "   进程名称: $($process.ProcessName)" -ForegroundColor Gray
        Write-Host "   启动时间: $($process.StartTime)" -ForegroundColor Gray
        Write-Host ""
        
        Write-Host "[2/2] 停止进程..." -ForegroundColor Yellow
        Stop-Process -Id $pid -Force
        Write-Host "   ✅ 进程已停止" -ForegroundColor Green
        
        # 等待端口释放
        Start-Sleep -Seconds 2
        
        # 验证
        $stillRunning = netstat -ano | findstr ":8000" | findstr "LISTENING"
        if ($stillRunning) {
            Write-Host "   ⚠️  端口可能仍被占用，请手动检查" -ForegroundColor Yellow
        } else {
            Write-Host "   ✅ 端口 8000 已释放" -ForegroundColor Green
        }
    } catch {
        Write-Host "   ❌ 无法停止进程: $_" -ForegroundColor Red
    }
} else {
    Write-Host "   ✅ 端口 8000 未被占用" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
