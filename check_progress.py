"""检查开发进展"""

import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from pathlib import Path

def main():
    case_id = "case-1fadf9d2"
    manager = CaseManager()
    
    case = manager.get_case(case_id)
    tasks = manager.get_tasks(case_id)
    plan = manager.get_plan(case_id)
    
    print("=" * 60)
    print("Web API 模块开发进展报告")
    print("=" * 60)
    print()
    
    if case:
        print(f"📋 案例信息:")
        print(f"   ID: {case.id}")
        print(f"   标题: {case.title}")
        print(f"   状态: {case.status}")
        print(f"   创建时间: {case.created_at}")
        print()
    
    if plan:
        print(f"📝 计划信息:")
        print(f"   计划 ID: {plan['plan'].id}")
        print(f"   计划文件: {plan['plan'].plan_md_path}")
        print()
    
    if tasks:
        print(f"✅ 任务进度:")
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == "completed")
        in_progress = sum(1 for t in tasks if t.status == "in_progress")
        pending = sum(1 for t in tasks if t.status == "pending")
        
        print(f"   总任务数: {total}")
        print(f"   ✅ 已完成: {completed}")
        print(f"   🚧 进行中: {in_progress}")
        print(f"   ⏳ 待处理: {pending}")
        print(f"   完成率: {completed/total*100:.1f}%")
        print()
        
        print("任务列表:")
        for task in tasks:
            status_icon = {
                "completed": "✅",
                "in_progress": "🚧",
                "pending": "⏳"
            }.get(task.status, "❓")
            print(f"   {status_icon} {task.id}: {task.title} ({task.status})")
        print()
    
    # 检查补丁
    patches_dir = Path(f"cases/{case_id}/patches")
    if patches_dir.exists():
        patches = list(patches_dir.glob("*.patch"))
        print(f"📦 代码补丁:")
        print(f"   补丁数量: {len(patches)}")
        for patch in patches:
            print(f"   - {patch.name}")
        print()
    
    # 检查 Agent 调用
    agent_runs_dir = Path(f"cases/{case_id}/agent_runs")
    if agent_runs_dir.exists():
        runs = list(agent_runs_dir.glob("*.json"))
        planning_runs = sum(1 for r in runs if "planning" in r.name)
        coding_runs = sum(1 for r in runs if "coding" in r.name)
        test_runs = sum(1 for r in runs if "test" in r.name)
        
        print(f"🤖 Agent 调用记录:")
        print(f"   PlanningAgent: {planning_runs} 次")
        print(f"   CodingAgent: {coding_runs} 次")
        print(f"   TestAgent: {test_runs} 次")
        print(f"   总计: {len(runs)} 次")
        print()
    
    print("=" * 60)
    print("下一步建议:")
    print("1. 继续使用 CodingAgent 生成剩余任务的代码")
    print("2. 验证和应用已生成的补丁")
    print("3. 运行测试验证功能")
    print("4. 使用 TestAgent 生成测试建议")
    print("=" * 60)

if __name__ == "__main__":
    main()
