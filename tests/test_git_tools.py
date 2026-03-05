"""
Git 工具类测试
"""

import pytest
import tempfile
import subprocess
from pathlib import Path

from openclaw_core.git_tools import GitTools


@pytest.fixture
def temp_git_repo():
    """创建临时 Git 仓库用于测试"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / "test_repo"
        repo_path.mkdir()
        
        # 初始化 Git 仓库
        subprocess.run(["git", "init"], cwd=str(repo_path), check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(repo_path), check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(repo_path), check=True)
        
        # 创建初始文件并提交
        (repo_path / "README.md").write_text("# Test Repo\n")
        subprocess.run(["git", "add", "README.md"], cwd=str(repo_path), check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(repo_path), check=True)
        
        yield repo_path


def test_git_tools_init(temp_git_repo):
    """测试 GitTools 初始化"""
    git_tools = GitTools(str(temp_git_repo))
    assert git_tools.repo_path == temp_git_repo.resolve()


def test_git_tools_init_invalid_path():
    """测试使用无效路径初始化 GitTools"""
    with pytest.raises(ValueError, match="仓库路径不存在"):
        GitTools("/nonexistent/path")


def test_get_current_branch(temp_git_repo):
    """测试获取当前分支"""
    git_tools = GitTools(str(temp_git_repo))
    branch = git_tools.get_current_branch()
    assert branch == "main" or branch == "master"


def test_get_branches(temp_git_repo):
    """测试获取分支列表"""
    git_tools = GitTools(str(temp_git_repo))
    branches = git_tools.get_branches()
    assert len(branches) > 0
    assert git_tools.get_current_branch() in branches


def test_create_branch(temp_git_repo):
    """测试创建分支"""
    git_tools = GitTools(str(temp_git_repo))
    success = git_tools.create_branch("test-branch", checkout=True)
    assert success
    assert git_tools.get_current_branch() == "test-branch"


def test_get_file_content(temp_git_repo):
    """测试获取文件内容"""
    git_tools = GitTools(str(temp_git_repo))
    content = git_tools.get_file_content("README.md")
    assert "# Test Repo" in content


def test_get_diff(temp_git_repo):
    """测试获取 diff"""
    git_tools = GitTools(str(temp_git_repo))
    
    # 修改文件
    (temp_git_repo / "README.md").write_text("# Test Repo\n\nModified")
    
    diff = git_tools.get_diff()
    assert "Modified" in diff or len(diff) > 0


def test_get_status(temp_git_repo):
    """测试获取 Git 状态"""
    git_tools = GitTools(str(temp_git_repo))
    
    # 创建新文件
    (temp_git_repo / "new_file.txt").write_text("new content")
    
    status = git_tools.get_status()
    assert status["is_dirty"] is True
    assert "new_file.txt" in status["untracked_files"]


def test_get_commit_history(temp_git_repo):
    """测试获取提交历史"""
    git_tools = GitTools(str(temp_git_repo))
    
    # 创建新提交
    (temp_git_repo / "file2.txt").write_text("content")
    subprocess.run(["git", "add", "file2.txt"], cwd=str(temp_git_repo), check=True)
    subprocess.run(["git", "commit", "-m", "Add file2"], cwd=str(temp_git_repo), check=True)
    
    history = git_tools.get_commit_history(limit=5)
    assert len(history) >= 2
    assert any(commit["message"] == "Add file2" for commit in history)


def test_get_repo_info(temp_git_repo):
    """测试获取仓库信息"""
    git_tools = GitTools(str(temp_git_repo))
    info = git_tools.get_repo_info()
    
    assert "repo_path" in info
    assert "current_branch" in info
    assert "latest_commit" in info
    assert "is_dirty" in info
    assert info["current_branch"] == git_tools.get_current_branch()
