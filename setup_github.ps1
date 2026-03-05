# GitHub 仓库设置脚本
# 使用方法: .\setup_github.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub 仓库设置向导" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Git
Write-Host "检查 Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Git 已安装" -ForegroundColor Green
    } else {
        Write-Host "✗ Git 未安装，请先运行 .\install_git.ps1" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Git 未安装，请先运行 .\install_git.ps1" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 步骤 1: 初始化 Git 仓库
if (-not (Test-Path ".git")) {
    Write-Host "步骤 1: 初始化 Git 仓库..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Git 仓库已初始化" -ForegroundColor Green
} else {
    Write-Host "✓ Git 仓库已存在" -ForegroundColor Green
}

Write-Host ""

# 步骤 2: 配置 Git（如果未配置）
Write-Host "步骤 2: 检查 Git 配置..." -ForegroundColor Yellow
$userName = git config user.name
$userEmail = git config user.email

if (-not $userName) {
    Write-Host "需要配置 Git 用户名和邮箱" -ForegroundColor Yellow
    $name = Read-Host "请输入你的用户名 (例如: zhangguanglai)"
    $email = Read-Host "请输入你的邮箱"
    
    if ($name -and $email) {
        git config --global user.name $name
        git config --global user.email $email
        Write-Host "✓ Git 配置完成" -ForegroundColor Green
    }
} else {
    Write-Host "✓ Git 已配置: $userName <$userEmail>" -ForegroundColor Green
}

Write-Host ""

# 步骤 3: 添加文件
Write-Host "步骤 3: 添加文件到 Git..." -ForegroundColor Yellow
git add .
$status = git status --short
if ($status) {
    Write-Host "✓ 文件已添加" -ForegroundColor Green
} else {
    Write-Host "✓ 没有新文件需要添加" -ForegroundColor Green
}

Write-Host ""

# 步骤 4: 创建提交
Write-Host "步骤 4: 创建提交..." -ForegroundColor Yellow
$hasCommits = git log --oneline -1 2>&1
if ($LASTEXITCODE -ne 0 -or -not $hasCommits) {
    git commit -m "Initial commit: OpenClaw Core implementation

- LLMRouter: 多模型统一路由层
- PlanningAgent: 规划 Agent
- CodingAgent: 编码 Agent
- TestAgent: 测试 Agent
- 完整的测试覆盖和示例代码"
    Write-Host "✓ 初始提交已创建" -ForegroundColor Green
} else {
    Write-Host "✓ 已有提交记录" -ForegroundColor Green
}

Write-Host ""

# 步骤 5: 配置远程仓库
Write-Host "步骤 5: 配置远程仓库..." -ForegroundColor Yellow
$remote = git remote get-url origin 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "选择配置方式:" -ForegroundColor Cyan
    Write-Host "1. 使用 GitHub CLI 创建仓库（推荐，需要先登录: gh auth login）" -ForegroundColor White
    Write-Host "2. 手动添加远程仓库 URL" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "请选择 (1/2)"
    
    if ($choice -eq "1") {
        # 检查 GitHub CLI
        try {
            $ghVersion = gh --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "使用 GitHub CLI 创建仓库..." -ForegroundColor Yellow
                gh repo create Causor-MyOpenClaw --public --source=. --remote=origin --push
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✓ 仓库已创建并推送" -ForegroundColor Green
                    Write-Host ""
                    Write-Host "仓库地址: https://github.com/zhangguanglai/Causor-MyOpenClaw" -ForegroundColor Cyan
                    exit 0
                }
            }
        } catch {
            Write-Host "✗ GitHub CLI 未安装或未登录" -ForegroundColor Red
        }
    }
    
    # 手动配置
    Write-Host ""
    Write-Host "请输入 GitHub 仓库 URL:" -ForegroundColor Yellow
    Write-Host "格式: https://github.com/zhangguanglai/Causor-MyOpenClaw.git" -ForegroundColor Gray
    $repoUrl = Read-Host "仓库 URL"
    
    if ($repoUrl) {
        git remote add origin $repoUrl
        Write-Host "✓ 远程仓库已添加" -ForegroundColor Green
    } else {
        Write-Host "✗ 未提供仓库 URL" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ 远程仓库已配置: $remote" -ForegroundColor Green
}

Write-Host ""

# 步骤 6: 推送到 GitHub
Write-Host "步骤 6: 推送到 GitHub..." -ForegroundColor Yellow
$push = Read-Host "是否现在推送到 GitHub? (y/n)"
if ($push -eq "y" -or $push -eq "Y") {
    git branch -M main
    Write-Host "推送代码..." -ForegroundColor Yellow
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "✓ 代码已成功推送到 GitHub!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        $remote = git remote get-url origin
        $repoUrl = $remote -replace '\.git$', ''
        Write-Host "仓库地址: $repoUrl" -ForegroundColor Cyan
        Write-Host "Actions: $repoUrl/actions" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "✗ 推送失败" -ForegroundColor Red
        Write-Host ""
        Write-Host "可能的原因:" -ForegroundColor Yellow
        Write-Host "1. 仓库不存在，请先在 GitHub 上创建仓库" -ForegroundColor White
        Write-Host "2. 认证失败，请检查 GitHub 凭证" -ForegroundColor White
        Write-Host "3. 网络问题" -ForegroundColor White
        Write-Host ""
        Write-Host "解决方法:" -ForegroundColor Yellow
        Write-Host "1. 访问 https://github.com/new 创建仓库" -ForegroundColor White
        Write-Host "2. 使用 GitHub CLI: gh auth login" -ForegroundColor White
        Write-Host "3. 或使用 Personal Access Token" -ForegroundColor White
    }
} else {
    Write-Host "跳过推送，你可以稍后运行: git push -u origin main" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
