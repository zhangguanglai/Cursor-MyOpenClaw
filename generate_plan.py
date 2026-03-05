"""生成实现计划"""

import sys
import io
import asyncio

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_core.llm_router import LLMRouter
from openclaw_core.agents import PlanningAgent, PlanningRequest

async def main():
    case_id = "case-1fadf9d2"
    
    manager = CaseManager()
    case = manager.get_case(case_id)
    
    if not case:
        print(f"❌ 案例不存在: {case_id}")
        return
    
    print(f"[PLAN] 为案例 {case_id} 生成实现计划...")
    
    # 构建规划请求
    request: PlanningRequest = {
        "requirement_description": case.description,
        "related_files": [
            "docs/mvp_studio.md",
            "openclaw_studio/case_manager.py",
            "openclaw_core/agents.py",
            "openclaw_cli/cli.py"
        ],
    }
    
    # 调用 PlanningAgent
    router = LLMRouter()
    agent = PlanningAgent(router, root_dir=case.repo_path or ".")
    
    try:
        response = await agent.generate_plan(request)
        
        # 保存计划
        plan = manager.save_plan(
            case_id=case_id,
            plan_markdown=response["plan_markdown"],
            tasks=response["tasks"] if response["tasks"] else [],
        )
        
        # 记录 Agent 调用
        manager.record_agent_run(
            case_id=case_id,
            agent_type="planning",
            input_data=request,
            output_data={"plan_id": plan.id, "tasks_count": len(response["tasks"])},
            model=router.select_model("planning"),
        )
        
        print(f"✅ 计划已生成: {plan.id}")
        print(f"   任务数量: {len(response['tasks'])}")
        print(f"   计划文件: {plan.plan_md_path}")
        
        # 显示任务列表
        if response.get("tasks"):
            print(f"\n任务列表:")
            for i, task in enumerate(response["tasks"], 1):
                print(f"  {i}. {task.get('title', 'N/A')}")
                print(f"     风险: {task.get('risk_level', 'medium')}")
        
    except Exception as e:
        print(f"❌ 生成计划失败: {e}")
        import traceback
        traceback.print_exc()
        manager.record_agent_run(
            case_id=case_id,
            agent_type="planning",
            input_data=request,
            status="failed",
            error_message=str(e),
        )

if __name__ == "__main__":
    asyncio.run(main())
