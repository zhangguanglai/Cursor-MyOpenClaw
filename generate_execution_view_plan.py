"""为完善执行视图功能生成实现计划"""

import sys
import io
import asyncio

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_core.llm_router import LLMRouter
from openclaw_core.agents import PlanningAgent

async def main():
    if len(sys.argv) < 2:
        print("用法: python generate_execution_view_plan.py <case_id>")
        return
    
    case_id = sys.argv[1]
    
    print("=" * 60)
    print("生成完善执行视图功能计划")
    print("=" * 60)
    print(f"\n案例 ID: {case_id}")
    
    manager = CaseManager()
    router = LLMRouter()
    agent = PlanningAgent(llm_router=router, root_dir=".")
    
    case = manager.get_case(case_id)
    if not case:
        print(f"❌ 案例不存在: {case_id}")
        return
    
    print(f"✅ 案例: {case.title}")
    
    # 构建规划请求
    request = {
        "requirement_description": case.description or "",
        "related_files": [
            "openclaw-studio-frontend/src/features/execution/ExecutionView.tsx",
            "openclaw-studio-frontend/src/services/coding.ts",
            "openclaw-studio-frontend/src/services/types.ts",
            "openclaw_studio/api/v1/coding.py",
            "openclaw_studio/models.py",
        ],
    }
    
    print(f"\n🤖 调用 PlanningAgent...")
    print(f"   相关文件: {len(request['related_files'])} 个")
    
    try:
        result = await agent.generate_plan(request)
        
        print(f"\n✅ 计划生成成功")
        print(f"   计划长度: {len(result['plan_markdown'])} 字符")
        print(f"   任务数量: {len(result.get('tasks', []))}")
        
        # 保存计划
        plan = manager.save_plan(
            case_id=case_id,
            plan_markdown=result["plan_markdown"],
            tasks=result.get("tasks", []),
        )
        
        # 记录 Agent 调用
        manager.record_agent_run(
            case_id=case_id,
            agent_type="planning",
            input_data=request,
            output_data={
                "plan_id": plan.id,
                "tasks_count": len(result.get("tasks", [])),
            },
            model=router.select_model("planning"),
        )
        
        print(f"\n📝 计划已保存")
        print(f"   计划 ID: {plan.id}")
        print(f"   文件: cases/{case_id}/plan.md")
        
        # 显示任务列表
        if result.get("tasks"):
            print(f"\n📋 任务列表:")
            for i, task in enumerate(result.get("tasks", [])[:10], 1):
                task_id = task.get("id", f"task-{i:03d}")
                title = task.get("title", "N/A")
                print(f"   {i}. [{task_id}] {title}")
            if len(result.get("tasks", [])) > 10:
                print(f"   ... 还有 {len(result.get('tasks', [])) - 10} 个任务")
        
    except Exception as e:
        print(f"\n❌ 计划生成失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        manager.close()

if __name__ == "__main__":
    asyncio.run(main())
