# Git 安装与配置指南

## 方法一：安装 Git for Windows（推荐）

### 1. 下载 Git

访问官方下载页面：
- **官方下载**: https://git-scm.com/download/win
- **镜像下载**: https://mirrors.tuna.tsinghua.edu.cn/git-for-windows/

### 2. 安装步骤

1. 运行下载的安装程序（如 `Git-2.43.0-64-bit.exe`）
2. 安装选项建议：
   - ✅ 选择 "Use Visual Studio Code as Git's default editor"（如果使用 VS Code）
   - ✅ 选择 "Git from the command line and also from 3rd-party software"
   - ✅ 选择 "Use bundled OpenSSH"
   - ✅ 选择 "Use the OpenSSL library"
   - ✅ 选择 "Checkout Windows-style, commit Unix-style line endings"
   - ✅ 选择 "Use MinTTY (the default terminal of MSYS2)"
3. 点击 "Install" 完成安装

### 3. 验证安装

打开新的 PowerShell 或命令提示符，运行：

```powershell
git --version
```

如果显示版本号（如 `git version 2.43.0.windows.1`），说明安装成功。

### 4. 配置 Git

```powershell
# 配置用户名和邮箱（替换为你的信息）
git config --global user.name "zhangguanglai"
git config --global user.email "your-email@example.com"

# 配置默认分支名
git config --global init.defaultBranch main

# 配置行尾处理（Windows）
git config --global core.autocrlf true
```

## 方法二：使用 GitHub CLI（gh）

GitHub CLI 提供了更简单的 GitHub 操作方式，但需要先安装 Git。

### 1. 安装 GitHub CLI

**使用 winget（Windows 11/10）：**
```powershell
winget install --id GitHub.cli
```

**或手动下载：**
- 访问：https://cli.github.com/
- 下载 Windows 安装程序

### 2. 验证安装

```powershell
gh --version
```

### 3. 登录 GitHub

```powershell
gh auth login
```

按照提示选择：
- GitHub.com
- HTTPS
- 登录方式（浏览器或 token）

## 方法三：使用 Chocolatey（如果已安装）

如果你已经安装了 Chocolatey 包管理器：

```powershell
# 安装 Git
choco install git -y

# 安装 GitHub CLI
choco install gh -y
```

## 快速安装脚本

我创建了一个 PowerShell 脚本来自动检测和安装 Git，见 `install_git.ps1`。

## 安装后初始化仓库

安装 Git 后，运行以下命令初始化仓库：

```powershell
cd D:\MyWorkspace\Causor-MyOpenClaw

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 创建初始提交
git commit -m "Initial commit: OpenClaw Core implementation"

# 添加远程仓库（替换为你的仓库 URL）
git remote add origin https://github.com/zhangguanglai/Causor-MyOpenClaw.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 使用 GitHub CLI 创建仓库（无需手动创建）

如果你安装了 GitHub CLI 并已登录：

```powershell
# 在项目目录中
cd D:\MyWorkspace\Causor-MyOpenClaw

# 初始化 Git
git init
git add .
git commit -m "Initial commit"

# 使用 GitHub CLI 创建仓库并推送
gh repo create Causor-MyOpenClaw --public --source=. --remote=origin --push
```

这会自动：
1. 在 GitHub 上创建仓库
2. 添加远程仓库
3. 推送代码

## 常见问题

### Q: 安装后 PowerShell 仍找不到 git 命令？

**A:** 需要重启 PowerShell 或重新加载环境变量：
```powershell
# 重新加载环境变量
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### Q: 如何检查 Git 是否在 PATH 中？

**A:** 运行：
```powershell
$env:Path -split ';' | Select-String git
```

### Q: 不想安装 Git，有其他方法吗？

**A:** 可以：
1. 使用 GitHub Desktop（图形界面）
2. 使用 VS Code 的 Git 集成
3. 使用在线 Git 工具（如 GitHub Web 界面）

## 推荐方案

**最简单的方式**：
1. 下载并安装 Git for Windows
2. 使用 GitHub CLI (`gh`) 创建仓库并推送

**最快的方式**：
1. 如果已安装 Chocolatey：`choco install git gh -y`
2. 使用 `gh repo create` 命令创建仓库
