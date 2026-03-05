"""创建完善历史视图功能的案例"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager

def main():
    print("=" * 60)
    print("创建完善历史视图功能案例")
    print("=" * 60)
    
    manager = CaseManager()
    
    case = manager.create_case(
        title="完善历史视图功能",
        description="""完善 OpenClaw Studio 前端历史视图，提供完整的案例开发历史时间线展示功能。

功能目标：
1. 时间线展示
   - 显示案例的完整开发历史（按时间顺序）
   - 包括：案例创建、计划生成、任务创建、代码生成、测试执行、补丁应用等事件
   - 使用 Ant Design Timeline 组件
   - 支持事件类型筛选
   - 支持时间范围筛选

2. 事件详情展示
   - 点击事件查看详细信息
   - 显示事件相关的数据（计划内容、补丁内容、测试结果等）
   - 支持 Markdown 渲染
   - 支持代码高亮

3. 事件筛选和搜索
   - 按事件类型筛选（创建、规划、编码、测试、应用）
   - 按时间范围筛选
   - 搜索事件描述

4. 统计信息
   - 显示案例总体统计（任务数、补丁数、测试次数等）
   - 显示各阶段耗时
   - 显示 Agent 调用统计

用户场景：
- 用户查看案例的完整开发历史
- 用户需要了解某个时间点的状态
- 用户需要查看特定类型的事件
- 用户需要分析开发效率

验收标准：
- 时间线正确显示所有事件
- 事件详情可以正确查看
- 筛选和搜索功能正常
- 统计信息准确
- UI 美观易用

技术约束：
- 使用 Ant Design Timeline 组件
- 使用 react-markdown 渲染内容
- 与现有 API 集成（history.ts）
- TypeScript 类型安全""",
        repo_path=".",
        branch="main"
    )
    
    print(f"\n✅ 案例创建成功")
    print(f"   案例 ID: {case.id}")
    print(f"   标题: {case.title}")
    print(f"   状态: {case.status}")
    
    manager.close()
    
    print(f"\n下一步: 运行 'python generate_history_view_plan.py {case.id}' 生成计划")
    return case.id

if __name__ == "__main__":
    case_id = main()
    print(f"\n案例 ID: {case_id}")
