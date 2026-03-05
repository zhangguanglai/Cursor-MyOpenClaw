"""为完善执行视图功能任务生成代码"""

import sys
import io
import asyncio

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_core.llm_router import LLMRouter
from openclaw_core.agents import CodingAgent

async def generate_code_for_task(case_id: str, task_id: str):
    """为单个任务生成代码"""
    manager = CaseManager()
    router = LLMRouter()
    agent = CodingAgent(llm_router=router, root_dir=".")
    
    task = manager.get_task(task_id)
    if not task:
        print(f"❌ 任务不存在: {task_id}")
        return False
    
    case = manager.get_case(case_id)
    if not case:
        print(f"❌ 案例不存在: {case_id}")
        return False
    
    print(f"\n📝 任务: {task.title}")
    print(f"   描述: {task.description[:100]}...")
    
    # 解析 related_files
    related_files = []
    if task.related_files:
        try:
            import json
            related_files = json.loads(task.related_files)
        except:
            pass
    
    # 构建 CodingRequest
    coding_request = {
        "task": {
            "id": task_id,
            "title": task.title,
            "description": task.description or "",
            "related_files": related_files,
        }
    }
    
    try:
        print(f"   🤖 调用 CodingAgent...")
        result = await agent.generate_code(coding_request)
        
        print(f"   ✅ 代码生成成功")
        print(f"      补丁数量: {len(result.get('patches', []))}")
        
        # 保存补丁
        for patch in result.get("patches", []):
            manager.save_patch(
                case_id=case_id,
                task_id=task_id,
                patch_content=patch.get("diff", ""),
                description=patch.get("description", ""),
            )
            print(f"      - {patch.get('file_path', 'unknown')}")
        
        # 记录 Agent 调用
        manager.record_agent_run(
            case_id=case_id,
            agent_type="coding",
            task_id=task_id,
            input_data=coding_request,
            output_data={"patches_count": len(result.get("patches", []))},
            model=router.select_model("coding"),
        )
        
        return True
        
    except Exception as e:
        print(f"   ❌ 代码生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        manager.close()

async def main():
    if len(sys.argv) < 2:
        print("用法: python generate_execution_view_code.py <case_id> [task_id]")
        return
    
    case_id = sys.argv[1]
    task_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("=" * 60)
    print("生成完善执行视图功能代码")
    print("=" * 60)
    print(f"\n案例 ID: {case_id}")
    
    manager = CaseManager()
    
    if task_id:
        # 生成单个任务
        await generate_code_for_task(case_id, task_id)
    else:
        # 生成所有待处理任务
        tasks = manager.get_tasks(case_id, status="pending")
        print(f"\n📋 找到 {len(tasks)} 个待处理任务")
        
        for task in tasks:
            success = await generate_code_for_task(case_id, task.id)
            if success:
                # 更新任务状态为 completed
                manager.update_task_status(task.id, "completed")
    
    manager.close()
    
    print(f"\n✅ 代码生成完成")

if __name__ == "__main__":
    asyncio.run(main())
