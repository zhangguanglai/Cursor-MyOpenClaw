# Git 安装检测和引导脚本
# 使用方法: .\install_git.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Git 安装检测和引导" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检测 Git
Write-Host "检测 Git..." -ForegroundColor Yellow
$gitInstalled = $false
try {
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Git 已安装: $gitVersion" -ForegroundColor Green
        $gitInstalled = $true
    }
} catch {
    Write-Host "✗ Git 未安装" -ForegroundColor Red
}

# 检测 GitHub CLI
Write-Host "检测 GitHub CLI..." -ForegroundColor Yellow
$ghInstalled = $false
try {
    $ghVersion = gh --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ GitHub CLI 已安装: $ghVersion" -ForegroundColor Green
        $ghInstalled = $true
    }
} catch {
    Write-Host "✗ GitHub CLI 未安装" -ForegroundColor Red
}

Write-Host ""

# 如果都安装了，提供初始化选项
if ($gitInstalled) {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Git 已安装，可以初始化仓库" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $init = Read-Host "是否现在初始化 Git 仓库并推送到 GitHub? (y/n)"
    if ($init -eq "y" -or $init -eq "Y") {
        Write-Host ""
        Write-Host "初始化 Git 仓库..." -ForegroundColor Yellow
        
        # 检查是否已经是 Git 仓库
        if (Test-Path ".git") {
            Write-Host "✓ 已经是 Git 仓库" -ForegroundColor Green
        } else {
            git init
            Write-Host "✓ Git 仓库初始化完成" -ForegroundColor Green
        }
        
        # 添加文件
        Write-Host "添加文件..." -ForegroundColor Yellow
        git add .
        Write-Host "✓ 文件已添加" -ForegroundColor Green
        
        # 检查是否有提交
        $hasCommits = git log --oneline 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "创建初始提交..." -ForegroundColor Yellow
            git commit -m "Initial commit: OpenClaw Core implementation"
            Write-Host "✓ 初始提交已创建" -ForegroundColor Green
        } else {
            Write-Host "✓ 已有提交记录" -ForegroundColor Green
        }
        
        # 检查远程仓库
        $remote = git remote get-url origin 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host ""
            Write-Host "配置远程仓库..." -ForegroundColor Yellow
            $repoUrl = Read-Host "请输入 GitHub 仓库 URL (例如: https://github.com/zhangguanglai/Causor-MyOpenClaw.git)"
            if ($repoUrl) {
                git remote add origin $repoUrl
                Write-Host "✓ 远程仓库已添加" -ForegroundColor Green
            }
        } else {
            Write-Host "✓ 远程仓库已配置: $remote" -ForegroundColor Green
        }
        
        # 如果安装了 GitHub CLI，提供创建仓库选项
        if ($ghInstalled) {
            Write-Host ""
            $createRepo = Read-Host "是否使用 GitHub CLI 创建仓库? (y/n)"
            if ($createRepo -eq "y" -or $createRepo -eq "Y") {
                Write-Host "使用 GitHub CLI 创建仓库..." -ForegroundColor Yellow
                gh repo create Causor-MyOpenClaw --public --source=. --remote=origin --push
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✓ 仓库已创建并推送" -ForegroundColor Green
                }
            }
        }
        
        # 推送代码
        Write-Host ""
        $push = Read-Host "是否现在推送到 GitHub? (y/n)"
        if ($push -eq "y" -or $push -eq "Y") {
            Write-Host "推送到 GitHub..." -ForegroundColor Yellow
            git branch -M main
            git push -u origin main
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ 代码已推送到 GitHub" -ForegroundColor Green
            } else {
                Write-Host "✗ 推送失败，请检查远程仓库配置" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "需要安装 Git" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "安装选项:" -ForegroundColor Yellow
    Write-Host "1. 手动下载安装 (推荐)" -ForegroundColor White
    Write-Host "   访问: https://git-scm.com/download/win" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. 使用 winget 安装 (Windows 11/10)" -ForegroundColor White
    Write-Host "   运行: winget install --id Git.Git -e --source winget" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. 使用 Chocolatey 安装 (如果已安装)" -ForegroundColor White
    Write-Host "   运行: choco install git -y" -ForegroundColor Gray
    Write-Host ""
    
    $install = Read-Host "是否使用 winget 尝试安装? (y/n)"
    if ($install -eq "y" -or $install -eq "Y") {
        Write-Host ""
        Write-Host "尝试使用 winget 安装 Git..." -ForegroundColor Yellow
        winget install --id Git.Git -e --source winget
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Git 安装完成，请重启 PowerShell 后运行此脚本" -ForegroundColor Green
        } else {
            Write-Host "✗ winget 安装失败，请手动下载安装" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
