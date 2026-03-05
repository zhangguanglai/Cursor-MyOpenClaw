# Git 仓库初始化指南

> **快速开始**：如果你还没有安装 Git，请先查看 `INSTALL_GIT.md` 或运行 `.\install_git.ps1`

## 方法一：使用自动化脚本（推荐）

运行自动化脚本，它会引导你完成所有步骤：

```powershell
.\setup_github.ps1
```

这个脚本会：
1. 检查 Git 是否安装
2. 初始化 Git 仓库
3. 配置 Git 用户信息
4. 添加文件并创建提交
5. 配置远程仓库
6. 推送到 GitHub

## 方法二：手动步骤

### 步骤 1：初始化本地 Git 仓库

```bash
cd D:\MyWorkspace\Causor-MyOpenClaw
git init
git add .
git commit -m "Initial commit: LLMRouter implementation"
```

## 步骤 2：在 GitHub 上创建仓库

1. 访问 https://github.com/zhangguanglai
2. 点击 "New repository"
3. 仓库名称：`Causor-MyOpenClaw`
4. 描述：`基于 OpenClaw 的 AI 原生研发内核`
5. 选择 Public 或 Private
6. **不要**初始化 README、.gitignore 或 license（我们已经有了）
7. 点击 "Create repository"

## 步骤 3：连接远程仓库并推送

```bash
# 添加远程仓库（替换为你的实际仓库 URL）
git remote add origin https://github.com/zhangguanglai/Causor-MyOpenClaw.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 步骤 4：验证 CI

推送后，访问：
https://github.com/zhangguanglai/Causor-MyOpenClaw/actions

你应该能看到 CI 工作流自动运行。

## 后续开发流程

```bash
# 创建新分支
git checkout -b feature/your-feature-name

# 提交更改
git add .
git commit -m "描述你的更改"

# 推送到远程
git push origin feature/your-feature-name

# 在 GitHub 上创建 Pull Request
```
