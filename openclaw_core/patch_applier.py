"""
补丁应用工具

提供将补丁应用到代码库的功能，包括：
- 解析补丁文件
- 应用补丁到目标文件
- 冲突检测
- Git 提交集成
"""

import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

from openclaw_core.logger import get_logger
from openclaw_core.git_tools import GitTools

logger = get_logger("openclaw.patch_applier")


class PatchApplyResult(Enum):
    """补丁应用结果"""
    SUCCESS = "success"
    CONFLICT = "conflict"
    ERROR = "error"
    SKIPPED = "skipped"


class PatchApplier:
    """补丁应用器"""

    def __init__(self, repo_path: Optional[str] = None, git_tools: Optional[GitTools] = None):
        """
        初始化补丁应用器

        Args:
            repo_path: Git 仓库路径（如果提供，会自动创建 GitTools）
            git_tools: GitTools 实例（如果提供，优先使用）
        """
        if git_tools:
            self.git_tools = git_tools
            self.repo_path = Path(git_tools.repo_path)
        elif repo_path:
            self.repo_path = Path(repo_path).resolve()
            self.git_tools = GitTools(str(self.repo_path))
        else:
            self.repo_path = None
            self.git_tools = None

    def parse_patch(self, patch_content: str) -> List[Dict[str, Any]]:
        """
        解析补丁内容，提取文件变更信息

        Args:
            patch_content: 补丁内容（diff 格式）

        Returns:
            文件变更列表，每个元素包含：
            - file_path: 文件路径
            - hunks: 变更块列表
        """
        files = []
        current_file = None
        current_hunk = None

        lines = patch_content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]

            # 检测文件头：diff --git a/file b/file
            diff_match = re.match(r'^diff --git a/(.+?) b/(.+?)$', line)
            if diff_match:
                if current_file:
                    files.append(current_file)
                current_file = {
                    'file_path': diff_match.group(1),
                    'hunks': []
                }
                i += 1
                continue

            # 检测变更块：@@ -start,count +start,count @@
            hunk_match = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
            if hunk_match and current_file:
                if current_hunk:
                    current_file['hunks'].append(current_hunk)
                old_start = int(hunk_match.group(1))
                old_count = int(hunk_match.group(2)) if hunk_match.group(2) else 1
                new_start = int(hunk_match.group(3))
                new_count = int(hunk_match.group(4)) if hunk_match.group(4) else 1

                current_hunk = {
                    'old_start': old_start,
                    'old_count': old_count,
                    'new_start': new_start,
                    'new_count': new_count,
                    'lines': []
                }
                i += 1
                continue

            # 收集变更行
            if current_hunk:
                current_hunk['lines'].append(line)
            i += 1

        if current_file:
            if current_hunk:
                current_file['hunks'].append(current_hunk)
            files.append(current_file)

        return files

    def apply_patch(
        self,
        patch_content: str,
        target_file: Optional[str] = None,
        dry_run: bool = False
    ) -> Tuple[PatchApplyResult, str, Optional[Dict[str, Any]]]:
        """
        应用补丁到代码库

        Args:
            patch_content: 补丁内容
            target_file: 目标文件路径（如果补丁只包含一个文件）
            dry_run: 是否为试运行（不实际应用）

        Returns:
            (结果, 消息, 详细信息)
        """
        if not self.repo_path:
            return PatchApplyResult.ERROR, "未指定仓库路径", None

        try:
            # 解析补丁
            files = self.parse_patch(patch_content)
            if not files:
                return PatchApplyResult.ERROR, "无法解析补丁内容", None

            results = []
            for file_info in files:
                file_path = file_info['file_path']
                target_path = self.repo_path / file_path

                # 检查文件是否存在
                if not target_path.exists():
                    # 如果是新文件，创建目录
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target_path.write_text('', encoding='utf-8')
                    logger.info(f"创建新文件: {file_path}")

                # 读取原文件内容
                original_content = target_path.read_text(encoding='utf-8')
                original_lines = original_content.split('\n')

                # 应用每个变更块
                new_lines = original_lines.copy()
                offset = 0  # 由于前面的修改导致的偏移

                for hunk in file_info['hunks']:
                    old_start = hunk['old_start'] - 1  # 转换为 0-based 索引
                    old_count = hunk['old_count']
                    new_start = hunk['new_start'] - 1 + offset
                    new_lines_to_add = []

                    # 处理变更块中的行
                    for line in hunk['lines']:
                        if line.startswith(' '):
                            # 上下文行，跳过
                            continue
                        elif line.startswith('-'):
                            # 删除行
                            continue
                        elif line.startswith('+'):
                            # 添加行
                            new_lines_to_add.append(line[1:])

                    # 检查冲突
                    if old_start < len(new_lines):
                        # 检查上下文是否匹配
                        context_match = True
                        for i, hunk_line in enumerate(hunk['lines'][:3]):  # 检查前几行上下文
                            if hunk_line.startswith(' '):
                                expected_line = hunk_line[1:]
                                actual_idx = old_start + i
                                if actual_idx < len(new_lines):
                                    if new_lines[actual_idx] != expected_line:
                                        context_match = False
                                        break

                        if not context_match:
                            return PatchApplyResult.CONFLICT, f"文件 {file_path} 存在冲突", {
                                'file_path': file_path,
                                'hunk': hunk
                            }

                    # 应用变更
                    if not dry_run:
                        # 删除旧行
                        if old_start < len(new_lines):
                            del new_lines[old_start:old_start + old_count]
                            offset -= old_count

                        # 插入新行
                        for i, new_line in enumerate(new_lines_to_add):
                            new_lines.insert(old_start + i, new_line)
                            offset += 1

                # 写入文件
                if not dry_run:
                    new_content = '\n'.join(new_lines)
                    target_path.write_text(new_content, encoding='utf-8')
                    logger.info(f"已应用补丁到文件: {file_path}")

                results.append({
                    'file_path': file_path,
                    'status': 'applied' if not dry_run else 'would_apply'
                })

            return PatchApplyResult.SUCCESS, f"成功应用补丁到 {len(results)} 个文件", {
                'files': results
            }

        except Exception as e:
            logger.error(f"应用补丁时出错: {e}", exc_info=True)
            return PatchApplyResult.ERROR, f"应用补丁失败: {str(e)}", None

    def apply_patch_with_git(
        self,
        patch_content: str,
        commit_message: str,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        dry_run: bool = False
    ) -> Tuple[PatchApplyResult, str, Optional[Dict[str, Any]]]:
        """
        应用补丁并提交到 Git

        Args:
            patch_content: 补丁内容
            commit_message: 提交信息
            author_name: 作者名称
            author_email: 作者邮箱
            dry_run: 是否为试运行

        Returns:
            (结果, 消息, 详细信息)
        """
        if not self.git_tools:
            return PatchApplyResult.ERROR, "未配置 Git 工具", None

        try:
            # 先试运行检查冲突
            result, msg, details = self.apply_patch(patch_content, dry_run=True)
            if result == PatchApplyResult.CONFLICT:
                return result, msg, details
            if result == PatchApplyResult.ERROR:
                return result, msg, details

            # 实际应用
            if not dry_run:
                result, msg, details = self.apply_patch(patch_content, dry_run=False)
                if result != PatchApplyResult.SUCCESS:
                    return result, msg, details

                # 获取变更的文件列表
                files = details.get('files', []) if details else []
                file_paths = [f['file_path'] for f in files]

                # 添加到 Git 暂存区
                for file_path in file_paths:
                    target_path = self.repo_path / file_path
                    if target_path.exists():
                        self.git_tools._run_git_command('add', file_path)

                # 提交
                commit_args = ['commit', '-m', commit_message]
                if author_name and author_email:
                    commit_args.extend(['--author', f'{author_name} <{author_email}>'])

                self.git_tools._run_git_command(*commit_args)
                logger.info(f"已提交补丁: {commit_message}")

                return PatchApplyResult.SUCCESS, f"成功应用并提交补丁: {msg}", {
                    'files': files,
                    'commit_message': commit_message
                }
            else:
                return PatchApplyResult.SUCCESS, f"试运行成功: {msg}", details

        except Exception as e:
            logger.error(f"应用补丁并提交时出错: {e}", exc_info=True)
            return PatchApplyResult.ERROR, f"应用补丁并提交失败: {str(e)}", None
