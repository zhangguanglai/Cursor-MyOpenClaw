"""创建完善测试视图功能的案例"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager

def main():
    print("=" * 60)
    print("创建完善测试视图功能案例")
    print("=" * 60)
    
    manager = CaseManager()
    
    case = manager.create_case(
        title="完善测试视图功能",
        description="""完善 OpenClaw Studio 前端测试视图，提供完整的测试建议和验收清单功能。

功能目标：
1. 测试建议展示
   - 显示潜在问题列表（问题描述、严重程度、关联文件）
   - 显示测试用例列表（描述、步骤、预期结果）
   - 使用 Markdown 渲染优化显示
   - 支持问题筛选（按严重程度）
   - 支持测试用例展开/折叠

2. 验收清单功能
   - 显示验收清单列表（checkbox 格式）
   - 支持勾选/取消勾选
   - 显示完成进度
   - 保存验收状态（可选）

3. 测试结果管理
   - 显示测试结果历史
   - 支持重新生成测试建议
   - 显示测试生成时间

4. Markdown 渲染优化
   - 使用 react-markdown + remark-gfm
   - 代码块语法高亮
   - 列表渲染优化

用户场景：
- 用户查看代码补丁后，需要查看测试建议
- 用户需要查看潜在问题和测试用例
- 用户需要跟踪验收清单进度
- 用户需要重新生成测试建议

验收标准：
- 测试建议正确显示（潜在问题、测试用例）
- 验收清单可以交互（checkbox）
- Markdown 渲染美观易读
- 可以重新生成测试建议
- 测试结果可以保存和查看

技术约束：
- 使用 react-markdown + remark-gfm
- 使用 Ant Design 组件（Card, List, Checkbox, Tag, Button）
- 与现有 API 集成（testing.ts）
- TypeScript 类型安全""",
        repo_path=".",
        branch="main"
    )
    
    print(f"\n✅ 案例创建成功")
    print(f"   案例 ID: {case.id}")
    print(f"   标题: {case.title}")
    print(f"   状态: {case.status}")
    
    manager.close()
    
    print(f"\n下一步: 运行 'python generate_testing_view_plan.py {case.id}' 生成计划")
    return case.id

if __name__ == "__main__":
    case_id = main()
    print(f"\n案例 ID: {case_id}")
