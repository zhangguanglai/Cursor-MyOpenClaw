# Git 和 GitHub 快速开始指南

## 🚀 最快的方式（3 步）

### 1. 安装 Git

**选项 A：使用 winget（Windows 11/10）**
```powershell
winget install --id Git.Git -e --source winget
```

**选项 B：手动下载**
- 访问：https://git-scm.com/download/win
- 下载并运行安装程序
- 安装时选择默认选项即可

**选项 C：使用自动化脚本**
```powershell
.\install_git.ps1
```

### 2. 配置 Git（首次使用）

```powershell
git config --global user.name "zhangguanglai"
git config --global user.email "your-email@example.com"
```

### 3. 初始化并推送到 GitHub

**使用自动化脚本（最简单）：**
```powershell
.\setup_github.ps1
```

**或手动执行：**
```powershell
# 初始化仓库
git init
git add .
git commit -m "Initial commit: OpenClaw Core"

# 在 GitHub 上创建仓库后，连接并推送
git remote add origin https://github.com/zhangguanglai/Causor-MyOpenClaw.git
git branch -M main
git push -u origin main
```

## 📋 详细步骤

### 步骤 1：检查 Git 是否已安装

```powershell
git --version
```

如果显示版本号，说明已安装。如果提示"找不到命令"，需要先安装。

### 步骤 2：安装 Git（如果未安装）

#### 方法 A：使用 winget（推荐）

```powershell
winget install --id Git.Git -e --source winget
```

安装完成后，**重启 PowerShell**。

#### 方法 B：手动下载安装

1. 访问：https://git-scm.com/download/win
2. 下载最新版本的 Git for Windows
3. 运行安装程序，使用默认选项
4. 重启 PowerShell

### 步骤 3：配置 Git

```powershell
# 设置用户名和邮箱（替换为你的信息）
git config --global user.name "zhangguanglai"
git config --global user.email "your-email@example.com"

# 设置默认分支名
git config --global init.defaultBranch main

# 验证配置
git config --list
```

### 步骤 4：初始化仓库

在项目目录中运行：

```powershell
cd D:\MyWorkspace\Causor-MyOpenClaw

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 创建初始提交
git commit -m "Initial commit: OpenClaw Core implementation

- LLMRouter: 多模型统一路由层
- PlanningAgent: 规划 Agent
- CodingAgent: 编码 Agent
- TestAgent: 测试 Agent
- 完整的测试覆盖和示例代码"
```

### 步骤 5：在 GitHub 上创建仓库

#### 方法 A：使用 GitHub CLI（如果已安装）

```powershell
# 安装 GitHub CLI（如果未安装）
winget install --id GitHub.cli

# 登录 GitHub
gh auth login

# 创建仓库并推送
gh repo create Causor-MyOpenClaw --public --source=. --remote=origin --push
```

#### 方法 B：在 GitHub 网站上创建

1. 访问：https://github.com/new
2. 仓库名称：`Causor-MyOpenClaw`
3. 描述：`基于 OpenClaw 的 AI 原生研发内核`
4. 选择 Public 或 Private
5. **不要**勾选 "Initialize this repository with a README"
6. 点击 "Create repository"

### 步骤 6：连接远程仓库并推送

```powershell
# 添加远程仓库
git remote add origin https://github.com/zhangguanglai/Causor-MyOpenClaw.git

# 设置主分支名
git branch -M main

# 推送到 GitHub
git push -u origin main
```

如果提示输入用户名和密码：
- 用户名：你的 GitHub 用户名
- 密码：使用 **Personal Access Token**（不是 GitHub 密码）

#### 创建 Personal Access Token

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 设置名称：`OpenClaw Core`
4. 选择权限：至少勾选 `repo`
5. 点击 "Generate token"
6. **复制 token**（只显示一次）
7. 在推送时，密码处输入这个 token

## ✅ 验证

推送成功后，访问：
- 仓库：https://github.com/zhangguanglai/Causor-MyOpenClaw
- Actions：https://github.com/zhangguanglai/Causor-MyOpenClaw/actions

你应该能看到：
- ✅ 所有代码文件
- ✅ CI 工作流自动运行

## 🔧 常见问题

### Q: 安装 Git 后 PowerShell 仍找不到命令？

**A:** 需要重启 PowerShell 或重新加载环境变量：
```powershell
# 重新加载 PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### Q: 推送时提示认证失败？

**A:** GitHub 已不再支持密码认证，需要使用 Personal Access Token：
1. 创建 Token：https://github.com/settings/tokens
2. 推送时，用户名输入 GitHub 用户名，密码输入 Token

### Q: 想使用 SSH 而不是 HTTPS？

**A:** 
1. 生成 SSH 密钥：`ssh-keygen -t ed25519 -C "your-email@example.com"`
2. 添加 SSH 密钥到 GitHub：https://github.com/settings/keys
3. 使用 SSH URL：`git remote set-url origin git@github.com:zhangguanglai/Causor-MyOpenClaw.git`

### Q: 不想安装 Git，有其他方法吗？

**A:** 可以：
1. 使用 GitHub Desktop（图形界面）
2. 使用 VS Code 的 Git 集成
3. 使用在线工具（如 GitHub Web 界面）

## 📚 更多资源

- Git 官方文档：https://git-scm.com/doc
- GitHub 文档：https://docs.github.com
- Git 教程：https://git-scm.com/book

## 🎯 推荐工作流

1. **开发时**：
   ```powershell
   git add .
   git commit -m "描述你的更改"
   git push
   ```

2. **创建新功能**：
   ```powershell
   git checkout -b feature/your-feature
   # 开发...
   git add .
   git commit -m "实现功能 X"
   git push origin feature/your-feature
   # 在 GitHub 上创建 Pull Request
   ```
