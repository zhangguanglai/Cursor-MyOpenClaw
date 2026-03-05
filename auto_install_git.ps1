# 自动安装 Git 脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Git 自动安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已安装 Git
Write-Host "检查 Git 是否已安装..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Git 已安装: $gitVersion" -ForegroundColor Green
        Write-Host ""
        Write-Host "Git 已安装，无需重复安装。" -ForegroundColor Green
        exit 0
    }
} catch {
    Write-Host "Git 未安装，开始安装..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "正在下载 Git 安装程序..." -ForegroundColor Yellow

# Git 下载 URL（使用官方最新版本）
$gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"
$installerPath = "$env:TEMP\Git-Installer.exe"

try {
    # 下载安装程序
    Invoke-WebRequest -Uri $gitUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "下载完成: $installerPath" -ForegroundColor Green
} catch {
    Write-Host "下载失败，请手动下载:" -ForegroundColor Red
    Write-Host "https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "或使用以下命令手动下载:" -ForegroundColor Yellow
    Write-Host "Invoke-WebRequest -Uri 'https://git-scm.com/download/win' -OutFile '$installerPath'" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "正在安装 Git（静默安装）..." -ForegroundColor Yellow
Write-Host "这可能需要几分钟，请稍候..." -ForegroundColor Yellow

# 静默安装参数
$installArgs = "/VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS=icons,ext\shellhere,assoc,assoc_sh"

try {
    # 运行安装程序
    Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait -NoNewWindow
    
    Write-Host ""
    Write-Host "安装完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "请重启 PowerShell 或运行以下命令重新加载环境变量:" -ForegroundColor Yellow
    Write-Host '$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")' -ForegroundColor Gray
    Write-Host ""
    Write-Host "然后运行以下命令验证安装:" -ForegroundColor Yellow
    Write-Host "git --version" -ForegroundColor Gray
    
    # 清理安装程序
    Remove-Item $installerPath -ErrorAction SilentlyContinue
    
} catch {
    Write-Host "安装过程中出现错误: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "请手动运行安装程序: $installerPath" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安装完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
