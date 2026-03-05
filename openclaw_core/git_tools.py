"""
Git 工具类

提供 Git 仓库操作的统一接口，支持：
- 获取仓库信息
- 分支管理
- 代码差异查看
- 提交历史查询
- 文件内容读取
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from openclaw_core.logger import get_logger

logger = get_logger("openclaw.git_tools")


class GitTools:
    """Git 操作工具类"""

    def __init__(self, repo_path: str):
        """
        初始化 Git 工具

        Args:
            repo_path: Git 仓库路径（可以是绝对路径或相对路径）
        """
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise ValueError(f"仓库路径不存在: {self.repo_path}")
        
        # 检查是否是 Git 仓库
        if not self._is_git_repo():
            raise ValueError(f"不是有效的 Git 仓库: {self.repo_path}")

    def _is_git_repo(self) -> bool:
        """检查是否是 Git 仓库"""
        git_dir = self.repo_path / ".git"
        return git_dir.exists() or git_dir.is_file()

    def _run_git_command(self, *args: str, check: bool = True) -> str:
        """
        执行 Git 命令

        Args:
            *args: Git 命令参数
            check: 如果为 True，命令失败时抛出异常

        Returns:
            命令输出（stdout）
        """
        cmd = ["git"] + list(args)
        logger.debug(f"执行 Git 命令: {' '.join(cmd)} (工作目录: {self.repo_path})")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=check,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode != 0 and check:
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Git 命令执行失败: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"执行 Git 命令时出错: {e}")
            raise

    def get_repo_info(self) -> Dict[str, Any]:
        """
        获取仓库基本信息

        Returns:
            包含仓库信息的字典：
            - remote_url: 远程仓库 URL
            - current_branch: 当前分支
            - latest_commit: 最新提交信息
            - is_dirty: 是否有未提交的更改
        """
        try:
            # 获取远程 URL
            try:
                remote_url = self._run_git_command("config", "--get", "remote.origin.url", check=False)
            except Exception:
                remote_url = None

            # 获取当前分支
            current_branch = self.get_current_branch()

            # 获取最新提交
            try:
                commit_hash = self._run_git_command("rev-parse", "HEAD")
                commit_message = self._run_git_command("log", "-1", "--pretty=format:%s")
                commit_author = self._run_git_command("log", "-1", "--pretty=format:%an")
                commit_date = self._run_git_command("log", "-1", "--pretty=format:%ai")
            except Exception:
                commit_hash = None
                commit_message = None
                commit_author = None
                commit_date = None

            # 检查是否有未提交的更改
            is_dirty = self._has_uncommitted_changes()

            return {
                "repo_path": str(self.repo_path),
                "remote_url": remote_url,
                "current_branch": current_branch,
                "latest_commit": {
                    "hash": commit_hash,
                    "message": commit_message,
                    "author": commit_author,
                    "date": commit_date,
                } if commit_hash else None,
                "is_dirty": is_dirty,
            }
        except Exception as e:
            logger.error(f"获取仓库信息失败: {e}")
            raise

    def get_branches(self, remote: bool = False) -> List[str]:
        """
        获取分支列表

        Args:
            remote: 如果为 True，返回远程分支；否则返回本地分支

        Returns:
            分支名称列表
        """
        try:
            if remote:
                output = self._run_git_command("branch", "-r", "--format=%(refname:short)")
            else:
                output = self._run_git_command("branch", "--format=%(refname:short)")
            
            branches = [b.strip() for b in output.split('\n') if b.strip()]
            # 移除远程分支的 "origin/" 前缀（如果存在）
            if remote:
                branches = [b.replace('origin/', '') for b in branches]
            return branches
        except Exception as e:
            logger.error(f"获取分支列表失败: {e}")
            raise

    def get_current_branch(self) -> str:
        """
        获取当前分支名称

        Returns:
            当前分支名称
        """
        try:
            return self._run_git_command("rev-parse", "--abbrev-ref", "HEAD")
        except Exception as e:
            logger.error(f"获取当前分支失败: {e}")
            raise

    def get_diff(self, base: Optional[str] = None, head: Optional[str] = None, file_path: Optional[str] = None) -> str:
        """
        获取代码差异

        Args:
            base: 基准提交/分支（默认为 HEAD）
            head: 目标提交/分支（默认为工作区）
            file_path: 特定文件路径（可选）

        Returns:
            diff 字符串
        """
        try:
            args = ["diff"]
            
            if base:
                args.append(base)
            if head:
                args.append(head)
            if not base and not head:
                # 如果没有指定 base 和 head，显示工作区与暂存区的差异
                args.append("HEAD")
            
            if file_path:
                args.append("--")
                args.append(file_path)
            
            diff = self._run_git_command(*args, check=False)
            return diff
        except Exception as e:
            logger.error(f"获取 diff 失败: {e}")
            raise

    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """
        创建新分支

        Args:
            branch_name: 分支名称
            checkout: 是否切换到新分支

        Returns:
            是否成功创建
        """
        try:
            if checkout:
                self._run_git_command("checkout", "-b", branch_name)
            else:
                self._run_git_command("branch", branch_name)
            logger.info(f"成功创建分支: {branch_name}")
            return True
        except Exception as e:
            logger.error(f"创建分支失败: {e}")
            return False

    def get_commit_history(self, limit: int = 10, branch: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取提交历史

        Args:
            limit: 返回的提交数量
            branch: 分支名称（默认为当前分支）

        Returns:
            提交信息列表，每个包含：
            - hash: 提交哈希
            - message: 提交信息
            - author: 作者
            - date: 提交日期
        """
        try:
            args = ["log", f"-{limit}", "--pretty=format:%H|%an|%ai|%s"]
            if branch:
                args.append(branch)
            
            output = self._run_git_command(*args)
            
            commits = []
            for line in output.split('\n'):
                if not line.strip():
                    continue
                parts = line.split('|', 3)
                if len(parts) >= 4:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3],
                    })
            
            return commits
        except Exception as e:
            logger.error(f"获取提交历史失败: {e}")
            raise

    def get_file_content(self, file_path: str, ref: str = "HEAD") -> str:
        """
        获取文件内容

        Args:
            file_path: 文件路径（相对于仓库根目录）
            ref: Git 引用（commit hash, branch, tag 等，默认为 HEAD）

        Returns:
            文件内容
        """
        try:
            content = self._run_git_command("show", f"{ref}:{file_path}")
            return content
        except Exception as e:
            logger.error(f"获取文件内容失败: {e}")
            raise

    def _has_uncommitted_changes(self) -> bool:
        """检查是否有未提交的更改"""
        try:
            # 检查工作区和暂存区是否有更改
            output = self._run_git_command("status", "--porcelain")
            return bool(output.strip())
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        获取 Git 状态

        Returns:
            状态信息字典：
            - branch: 当前分支
            - is_dirty: 是否有未提交的更改
            - staged_files: 已暂存的文件列表
            - unstaged_files: 未暂存的文件列表
            - untracked_files: 未跟踪的文件列表
        """
        try:
            current_branch = self.get_current_branch()
            is_dirty = self._has_uncommitted_changes()
            
            # 获取状态详情
            status_output = self._run_git_command("status", "--porcelain")
            
            staged_files = []
            unstaged_files = []
            untracked_files = []
            
            for line in status_output.split('\n'):
                if not line.strip():
                    continue
                status_code = line[:2]
                file_path = line[3:].strip()
                
                if status_code[0] == '?' or status_code[1] == '?':
                    untracked_files.append(file_path)
                elif status_code[0] != ' ':
                    staged_files.append(file_path)
                elif status_code[1] != ' ':
                    unstaged_files.append(file_path)
            
            return {
                "branch": current_branch,
                "is_dirty": is_dirty,
                "staged_files": staged_files,
                "unstaged_files": unstaged_files,
                "untracked_files": untracked_files,
            }
        except Exception as e:
            logger.error(f"获取 Git 状态失败: {e}")
            raise
