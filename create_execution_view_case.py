"""创建完善执行视图功能的案例"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager

def main():
    print("=" * 60)
    print("创建完善执行视图功能案例")
    print("=" * 60)
    
    manager = CaseManager()
    
    case = manager.create_case(
        title="完善执行视图功能",
        description="""完善 OpenClaw Studio 前端执行视图，提供完整的代码补丁管理和预览功能。

功能目标：
1. 实现 Diff 预览组件
   - 使用 react-diff-view 或 react-syntax-highlighter
   - 支持 side-by-side 和 unified 两种显示模式
   - 代码语法高亮
   - 行号显示
   - 折叠/展开功能

2. 为任务生成代码补丁功能
   - 从任务列表中选择任务
   - 触发 CodingAgent 生成补丁
   - 显示生成进度
   - 补丁生成后自动刷新列表

3. 补丁列表优化
   - 补丁排序（按任务 ID、生成时间）
   - 补丁筛选（按任务 ID、文件路径）
   - 补丁状态显示（已生成/已应用）
   - 补丁元数据显示（任务 ID、描述、生成时间）

4. 补丁应用状态跟踪
   - 标记补丁为"已应用"
   - 显示应用状态
   - 应用历史记录

5. 复制补丁功能
   - 一键复制补丁内容
   - 复制补丁文件路径
   - 复制补丁描述

用户场景：
- 用户查看任务列表，选择任务生成代码补丁
- 用户预览补丁内容，查看代码变更
- 用户复制补丁内容，应用到代码库
- 用户跟踪补丁应用状态

验收标准：
- Diff 预览组件正常工作，显示清晰的代码差异
- 可以为任务生成代码补丁
- 补丁列表可以排序和筛选
- 补丁应用状态可以更新
- 补丁内容可以复制

技术约束：
- 使用 react-diff-view 或 react-syntax-highlighter
- 使用 Ant Design 组件（Card, List, Button, Modal）
- 与现有 API 集成（coding.ts）
- TypeScript 类型安全""",
        repo_path=".",
        branch="main"
    )
    
    print(f"\n✅ 案例创建成功")
    print(f"   案例 ID: {case.id}")
    print(f"   标题: {case.title}")
    print(f"   状态: {case.status}")
    
    manager.close()
    
    print(f"\n下一步: 运行 'python generate_execution_view_plan.py {case.id}' 生成计划")
    return case.id

if __name__ == "__main__":
    case_id = main()
    print(f"\n案例 ID: {case_id}")
