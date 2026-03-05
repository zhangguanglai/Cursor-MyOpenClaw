"""为任务生成代码"""

import sys
import io
import asyncio

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_core.llm_router import LLMRouter
from openclaw_core.agents import CodingAgent, CodingRequest

async def main():
    case_id = "case-1fadf9d2"
    # 从命令行参数获取任务 ID，如果没有则使用 task-001
    import sys
    task_id = sys.argv[1] if len(sys.argv) > 1 else "task-001"
    
    manager = CaseManager()
    case = manager.get_case(case_id)
    task = manager.get_task(task_id)
    
    if not case:
        print(f"❌ 案例不存在: {case_id}")
        return
    
    if not task:
        print(f"❌ 任务不存在: {task_id}")
        return
    
    print(f"[CODE] 为任务 {task_id} 生成代码...")
    print(f"   任务: {task.title}")
    
    # 构建编码请求
    related_files = []
    if task.related_files:
        import json
        related_files = json.loads(task.related_files)
    
    request: CodingRequest = {
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description or "",
            "related_files": related_files,
        },
    }
    
    # 调用 CodingAgent
    router = LLMRouter()
    agent = CodingAgent(router, root_dir=case.repo_path or ".")
    
    try:
        response = await agent.generate_code(request)
        
        # 保存补丁
        for patch in response["patches"]:
            manager.save_patch(
                case_id=case_id,
                task_id=task_id,
                patch_content=patch["diff"],
                description=patch["description"],
            )
        
        # 更新任务状态
        manager.update_task_status(task_id, "completed")
        
        # 记录 Agent 调用
        manager.record_agent_run(
            case_id=case_id,
            agent_type="coding",
            task_id=task_id,
            input_data=request,
            output_data={"patches_count": len(response["patches"])},
            model=router.select_model("coding"),
        )
        
        print(f"✅ 代码已生成")
        print(f"   补丁数量: {len(response['patches'])}")
        for i, patch in enumerate(response["patches"], 1):
            print(f"   - {patch.get('file_path', 'unknown')}: {patch.get('description', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 生成代码失败: {e}")
        import traceback
        traceback.print_exc()
        manager.record_agent_run(
            case_id=case_id,
            agent_type="coding",
            task_id=task_id,
            input_data=request,
            status="failed",
            error_message=str(e),
        )

if __name__ == "__main__":
    asyncio.run(main())
