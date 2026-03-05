"""为所有任务生成代码"""

import sys
import io
import asyncio

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_core.llm_router import LLMRouter
from openclaw_core.agents import CodingAgent, CodingRequest

async def generate_code_for_task(case_id: str, task_id: str):
    """为单个任务生成代码"""
    manager = CaseManager()
    case = manager.get_case(case_id)
    task = manager.get_task(task_id)
    
    if not case:
        print(f"❌ 案例不存在: {case_id}")
        return False
    
    if not task:
        print(f"❌ 任务不存在: {task_id}")
        return False
    
    print(f"\n[CODE] 为任务 {task_id} 生成代码...")
    print(f"   任务: {task.title}")
    print(f"   描述: {task.description[:60]}..." if len(task.description or "") > 60 else f"   描述: {task.description}")
    
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
        
        return True
        
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
        return False

async def main():
    case_id = "case-1fadf9d2"
    manager = CaseManager()
    
    # 获取所有待处理的任务
    tasks = manager.get_tasks(case_id)
    pending_tasks = [t for t in tasks if t.status == "pending"]
    
    print("=" * 60)
    print("为所有任务生成代码")
    print("=" * 60)
    print(f"\n案例: {case_id}")
    print(f"总任务数: {len(tasks)}")
    print(f"待处理任务: {len(pending_tasks)}")
    print(f"已完成任务: {sum(1 for t in tasks if t.status == 'completed')}")
    print()
    
    if not pending_tasks:
        print("✅ 所有任务都已完成！")
        return
    
    # 按任务 ID 排序
    pending_tasks.sort(key=lambda t: t.id)
    
    success_count = 0
    fail_count = 0
    
    for i, task in enumerate(pending_tasks, 1):
        print(f"\n[{i}/{len(pending_tasks)}] 处理任务: {task.id}")
        success = await generate_code_for_task(case_id, task.id)
        if success:
            success_count += 1
        else:
            fail_count += 1
        
        # 添加延迟，避免 API 限流
        if i < len(pending_tasks):
            print("   等待 2 秒...")
            await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("代码生成完成")
    print("=" * 60)
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {fail_count}")
    print(f"📊 总计: {len(pending_tasks)}")

if __name__ == "__main__":
    asyncio.run(main())
