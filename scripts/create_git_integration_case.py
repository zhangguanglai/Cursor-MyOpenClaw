"""
创建 Git 深度集成案例
"""

import sys
import io
from pathlib import Path

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openclaw_studio.case_manager import CaseManager

def create_git_integration_case():
    """创建 Git 深度集成案例"""
    case_manager = CaseManager()
    
    case = case_manager.create_case(
        title="实现 Git 深度集成",
        description="""实现与 Git 仓库的深度集成，支持代码状态查看和操作。

## 需求描述

在 OpenClaw Studio 中实现 Git 深度集成功能，使系统能够：
1. 获取 Git 仓库信息（分支、提交历史等）
2. 读取代码差异（diff）
3. 创建和管理分支
4. 获取文件内容（支持不同 ref）
5. 在案例详情页显示 Git 状态
6. 在补丁页面显示 Git diff
7. 支持创建新分支（可选）

## 技术约束

- 使用 GitPython 或 subprocess 调用 Git 命令
- 与现有 CaseManager 和工具集整合
- 提供 RESTful API 端点
- 前端展示 Git 状态和 diff

## 验收标准

- [ ] 实现 GitTools 类，提供完整的 Git 操作接口
- [ ] 集成到 CaseManager，在创建案例时验证 Git 仓库
- [ ] 提供 API 端点：git-status, git-diff, git-branches
- [ ] 前端可以显示 Git 状态和 diff
- [ ] 支持创建新分支（可选）
- [ ] 编写单元测试和集成测试
""",
        repo_path=".",
        branch="main"
    )
    
    print(f"✅ 案例创建成功！")
    print(f"案例 ID: {case.id}")
    print(f"标题: {case.title}")
    print(f"\n下一步：运行以下命令生成计划")
    print(f"python scripts/generate_plan.py {case.id}")

if __name__ == "__main__":
    create_git_integration_case()
