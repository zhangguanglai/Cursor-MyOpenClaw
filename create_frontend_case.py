"""创建 Web 前端开发案例"""

import sys
import io
import asyncio
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager

def main():
    print("=" * 60)
    print("创建 Web 前端开发案例")
    print("=" * 60)
    
    manager = CaseManager()
    
    case = manager.create_case(
        title="实现 Web 控制台前端界面",
        description="""使用 React + TypeScript 实现 OpenClaw Studio 前端界面，提供可视化 Web UI。

功能目标：
- 实现需求中心视图（案例列表、创建/编辑案例）
- 实现规划视图（计划展示、任务列表、Markdown 编辑器）
- 实现执行视图（任务列表、补丁展示、Diff 预览）
- 实现测试视图（测试建议、验收清单）
- 实现历史视图（时间线展示）
- 与 FastAPI 后端 API 集成
- 提供响应式设计，支持不同屏幕尺寸

用户场景：
- 用户通过 Web UI 创建和管理案例
- 用户通过 Web UI 触发 Agent 生成计划、代码、测试建议
- 用户通过 Web UI 查看补丁、diff 和历史记录
- 用户通过 Web UI 执行验收清单

验收标准：
- 所有核心视图正常工作
- 前后端联调成功
- 界面清晰易用
- 响应式设计
- 基础测试覆盖

技术约束：
- React 18+
- TypeScript
- Vite 构建工具
- Ant Design 或 Material-UI
- 与现有 FastAPI 后端集成""",
        repo_path=".",
        branch="main"
    )
    
    print(f"\n✅ 案例创建成功")
    print(f"   案例 ID: {case.id}")
    print(f"   标题: {case.title}")
    print(f"   状态: {case.status}")
    
    manager.close()
    
    print(f"\n下一步: 运行 'python generate_frontend_plan.py {case.id}' 生成计划")
    return case.id

if __name__ == "__main__":
    case_id = main()
    print(f"\n案例 ID: {case_id}")
