# Git 安装验证脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "验证 Git 安装" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 重新加载环境变量
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "检查 Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS: Git 已安装!" -ForegroundColor Green
        Write-Host "版本: $gitVersion" -ForegroundColor Green
        Write-Host ""
        
        # 检查 Git 配置
        Write-Host "检查 Git 配置..." -ForegroundColor Yellow
        $userName = git config --global user.name 2>&1
        $userEmail = git config --global user.email 2>&1
        
        if ($userName -and $userEmail) {
            Write-Host "Git 已配置: $userName <$userEmail>" -ForegroundColor Green
        } else {
            Write-Host "Git 尚未配置用户信息" -ForegroundColor Yellow
            Write-Host "运行以下命令配置:" -ForegroundColor Yellow
            Write-Host "  git config --global user.name `"Your Name`"" -ForegroundColor Gray
            Write-Host "  git config --global user.email `"your-email@example.com`"" -ForegroundColor Gray
        }
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Git 安装成功！可以开始使用了" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        exit 0
    }
} catch {
    Write-Host "Git 未找到" -ForegroundColor Red
}

Write-Host ""
Write-Host "如果 Git 仍未找到，请:" -ForegroundColor Yellow
Write-Host "1. 完全关闭当前 PowerShell 窗口" -ForegroundColor White
Write-Host "2. 重新打开 PowerShell" -ForegroundColor White
Write-Host "3. 运行: git --version" -ForegroundColor White
Write-Host ""
Write-Host "或者运行此脚本: .\verify_git.ps1" -ForegroundColor Yellow
