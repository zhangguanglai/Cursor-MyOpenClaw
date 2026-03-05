"""创建完善规划视图功能的案例"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager

def main():
    print("=" * 60)
    print("创建完善规划视图功能案例")
    print("=" * 60)
    
    manager = CaseManager()
    
    case = manager.create_case(
        title="完善规划视图功能",
        description="""完善 OpenClaw Studio 前端规划视图，提供完整的计划管理和编辑功能。

功能目标：
1. 实现 Markdown 编辑器（支持编辑计划）
   - 支持实时编辑 plan.md
   - 保存编辑后的计划
   - 预览模式切换

2. 实现任务列表表格
   - 显示所有子任务（从 plan.json 解析）
   - 显示任务状态（pending/completed）
   - 显示任务风险级别
   - 支持任务筛选和排序

3. 任务状态管理
   - 更新任务状态
   - 任务详情查看和编辑
   - 任务关联文件显示

4. 优化计划展示
   - 更好的 Markdown 渲染（使用 react-markdown）
   - 代码块语法高亮
   - 表格渲染支持
   - 链接和图片支持

用户场景：
- 用户查看生成的计划，需要更好的 Markdown 渲染
- 用户需要编辑计划内容
- 用户需要查看和管理任务列表
- 用户需要更新任务状态

验收标准：
- Markdown 编辑器可以正常编辑和保存
- 任务列表正确显示所有任务
- 任务状态可以更新
- Markdown 渲染美观易读
- 响应式设计支持

技术约束：
- 使用 react-markdown + remark-gfm
- 使用 Ant Design 组件（Table, Card, Button）
- 与现有 API 集成（planning.ts）
- TypeScript 类型安全""",
        repo_path=".",
        branch="main"
    )
    
    print(f"\n✅ 案例创建成功")
    print(f"   案例 ID: {case.id}")
    print(f"   标题: {case.title}")
    print(f"   状态: {case.status}")
    
    manager.close()
    
    print(f"\n下一步: 运行 'python generate_planning_view_plan.py {case.id}' 生成计划")
    return case.id

if __name__ == "__main__":
    case_id = main()
    print(f"\n案例 ID: {case_id}")
