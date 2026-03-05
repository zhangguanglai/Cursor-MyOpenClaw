"""创建缺失的任务"""

import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.database import Task
from datetime import datetime

def main():
    case_id = "case-1fadf9d2"
    manager = CaseManager()
    
    # 所有 11 个任务的完整定义
    all_tasks = [
        {
            "id": "task-001",
            "title": "创建 FastAPI 项目结构",
            "description": "创建 openclaw_studio/api/ 目录结构，包括 main.py、v1/ 子目录、dependencies.py。需要创建完整的目录结构和 __init__.py 文件。",
            "related_files": [],
            "risk_level": "low"
        },
        {
            "id": "task-002",
            "title": "实现 Pydantic 模型定义",
            "description": "创建 openclaw_studio/models.py，定义所有 API 的请求和响应模型（CaseCreate, CaseOut, PlanningRequestIn, PlanningResponseOut, CodingRequestIn, CodingResponseOut, TestRequestIn, TestResponseOut, CaseHistoryOut 等）。",
            "related_files": ["openclaw_studio/case_manager.py"],
            "risk_level": "low"
        },
        {
            "id": "task-003",
            "title": "实现依赖注入模块",
            "description": "创建 openclaw_studio/api/dependencies.py，提供 CaseManager 和 Agent（PlanningAgent, CodingAgent, TestAgent）的单例注入函数。",
            "related_files": ["openclaw_studio/case_manager.py", "openclaw_core/llm_router.py", "openclaw_core/agents.py"],
            "risk_level": "low"
        },
        {
            "id": "task-004",
            "title": "实现 FastAPI 主应用",
            "description": "创建 openclaw_studio/api/main.py，初始化 FastAPI app，配置 CORS、异常处理、路由注册。包含启动和关闭事件处理。",
            "related_files": [],
            "risk_level": "low"
        },
        {
            "id": "task-005",
            "title": "实现案例管理 API",
            "description": "创建 openclaw_studio/api/v1/cases.py，实现 CRUD 操作：GET /api/v1/cases（列表）、POST /api/v1/cases（创建）、GET /api/v1/cases/{case_id}（详情）、PUT /api/v1/cases/{case_id}（更新）。",
            "related_files": ["openclaw_studio/case_manager.py", "openclaw_studio/models.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-006",
            "title": "实现规划 API",
            "description": "创建 openclaw_studio/api/v1/planning.py，实现 POST /api/v1/cases/{case_id}/planning，异步调用 PlanningAgent 生成实现计划。",
            "related_files": ["openclaw_core/agents.py", "openclaw_studio/api/dependencies.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-007",
            "title": "实现编码 API",
            "description": "创建 openclaw_studio/api/v1/coding.py，实现 POST /api/v1/cases/{case_id}/tasks/{task_id}/code，调用 CodingAgent 生成代码补丁。同时实现 GET /api/v1/cases/{case_id}/patches 获取所有补丁。",
            "related_files": ["openclaw_core/agents.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-008",
            "title": "实现测试 API",
            "description": "创建 openclaw_studio/api/v1/testing.py，实现 POST /api/v1/cases/{case_id}/test，调用 TestAgent 生成测试建议和验收清单。",
            "related_files": ["openclaw_core/agents.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-009",
            "title": "实现历史记录 API",
            "description": "创建 openclaw_studio/api/v1/history.py，实现 GET /api/v1/cases/{case_id}/history，聚合展示完整闭环（案例、计划、补丁、Agent 调用记录等）。",
            "related_files": ["openclaw_studio/case_manager.py"],
            "risk_level": "low"
        },
        {
            "id": "task-010",
            "title": "添加 FastAPI 依赖和启动脚本",
            "description": "更新 requirements.txt 添加 fastapi、uvicorn、pydantic 等依赖。创建启动脚本或更新 setup.py 添加启动命令。",
            "related_files": ["requirements.txt", "setup.py"],
            "risk_level": "low"
        },
        {
            "id": "task-011",
            "title": "编写 API 测试",
            "description": "创建 tests/test_api.py，编写基础 API 测试用例，使用 FastAPI TestClient 测试核心端点（创建案例、生成计划等）。",
            "related_files": ["openclaw_studio/api/main.py"],
            "risk_level": "low"
        }
    ]
    
    # 获取计划
    plan = manager.get_plan(case_id)
    if not plan:
        print("❌ 计划不存在，请先生成计划")
        return
    
    plan_id = plan["plan"].id
    created_count = 0
    
    print(f"📋 创建缺失的任务（共 {len(all_tasks)} 个任务）...\n")
    
    for task_data in all_tasks:
        task_id = task_data["id"]
        existing_task = manager.get_task(task_id)
        
        if existing_task:
            print(f"  ✅ 任务已存在: {task_id} - {task_data['title']}")
        else:
            # 创建新任务
            related_files = json.dumps(task_data["related_files"], ensure_ascii=False) if task_data["related_files"] else None
            task = Task(
                id=task_id,
                case_id=case_id,
                plan_id=plan_id,
                title=task_data["title"],
                description=task_data["description"],
                status="pending",
                related_files=related_files,
                risk_level=task_data["risk_level"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            try:
                manager.db.create_task(task)
                created_count += 1
                print(f"  ➕ 创建任务: {task_id} - {task_data['title']}")
            except Exception as e:
                print(f"  ❌ 创建任务失败 {task_id}: {e}")
    
    print(f"\n✅ 任务创建完成:")
    print(f"   新建任务: {created_count}")
    print(f"   已存在: {len(all_tasks) - created_count}")
    print(f"   总计: {len(all_tasks)}")
    
    # 验证
    tasks = manager.get_tasks(case_id)
    print(f"\n📊 验证结果:")
    print(f"   数据库中的任务数: {len(tasks)}")
    if len(tasks) == len(all_tasks):
        print("   ✅ 所有任务都在数据库中")
        print("\n任务列表:")
        for task in sorted(tasks, key=lambda t: t.id):
            print(f"   {task.id}: {task.title}")
    else:
        print(f"   ⚠️  任务数量不匹配（期望 {len(all_tasks)}，实际 {len(tasks)}）")

if __name__ == "__main__":
    main()
