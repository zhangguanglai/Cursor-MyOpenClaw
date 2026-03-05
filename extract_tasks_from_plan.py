"""从计划中提取任务列表"""

import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.database import Task
import uuid
from datetime import datetime

def main():
    case_id = "case-1fadf9d2"
    manager = CaseManager()
    
    # 读取计划文件
    plan_path = Path(f"cases/{case_id}/plan.md")
    if not plan_path.exists():
        print(f"❌ 计划文件不存在: {plan_path}")
        return
    
    plan_content = plan_path.read_text(encoding='utf-8')
    
    # 从计划中提取任务（基于计划的结构）
    tasks = [
        {
            "id": "task-001",
            "title": "创建 FastAPI 项目结构",
            "description": "创建 openclaw_studio/api/ 目录结构，包括 main.py、v1/ 子目录、dependencies.py",
            "related_files": [],
            "risk_level": "low"
        },
        {
            "id": "task-002",
            "title": "实现 Pydantic 模型定义",
            "description": "创建 openclaw_studio/models.py，定义所有 API 的请求和响应模型",
            "related_files": ["openclaw_studio/case_manager.py"],
            "risk_level": "low"
        },
        {
            "id": "task-003",
            "title": "实现依赖注入模块",
            "description": "创建 openclaw_studio/api/dependencies.py，提供 CaseManager 和 Agent 的单例注入",
            "related_files": ["openclaw_studio/case_manager.py", "openclaw_core/llm_router.py"],
            "risk_level": "low"
        },
        {
            "id": "task-004",
            "title": "实现 FastAPI 主应用",
            "description": "创建 openclaw_studio/api/main.py，初始化 FastAPI app，配置 CORS、异常处理、路由注册",
            "related_files": [],
            "risk_level": "low"
        },
        {
            "id": "task-005",
            "title": "实现案例管理 API",
            "description": "创建 openclaw_studio/api/v1/cases.py，实现 CRUD 操作（GET /cases, POST /cases, GET /cases/{id}）",
            "related_files": ["openclaw_studio/case_manager.py", "openclaw_studio/models.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-006",
            "title": "实现规划 API",
            "description": "创建 openclaw_studio/api/v1/planning.py，实现 POST /cases/{id}/planning，异步调用 PlanningAgent",
            "related_files": ["openclaw_core/agents.py", "openclaw_studio/api/dependencies.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-007",
            "title": "实现编码 API",
            "description": "创建 openclaw_studio/api/v1/coding.py，实现 POST /cases/{id}/tasks/{task_id}/code，调用 CodingAgent",
            "related_files": ["openclaw_core/agents.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-008",
            "title": "实现测试 API",
            "description": "创建 openclaw_studio/api/v1/testing.py，实现 POST /cases/{id}/test，调用 TestAgent",
            "related_files": ["openclaw_core/agents.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-009",
            "title": "实现历史记录 API",
            "description": "创建 openclaw_studio/api/v1/history.py，实现 GET /cases/{id}/history，聚合展示完整闭环",
            "related_files": ["openclaw_studio/case_manager.py"],
            "risk_level": "low"
        },
        {
            "id": "task-010",
            "title": "添加 FastAPI 依赖和启动脚本",
            "description": "更新 requirements.txt 添加 fastapi、uvicorn，创建启动脚本",
            "related_files": ["requirements.txt"],
            "risk_level": "low"
        },
        {
            "id": "task-011",
            "title": "编写 API 测试",
            "description": "创建 tests/test_api.py，编写基础 API 测试用例",
            "related_files": ["openclaw_studio/api/main.py"],
            "risk_level": "low"
        }
    ]
    
    # 保存任务到数据库
    plan = manager.get_plan(case_id)
    if plan:
        plan_id = plan["plan"].id
        created_count = 0
        for task_data in tasks:
            task_id = task_data["id"]
            # 检查任务是否已存在
            existing_task = manager.get_task(task_id)
            if existing_task:
                print(f"  ⏭️  任务已存在: {task_id}")
                continue
            
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
            manager.db.create_task(task)
            created_count += 1
        print(f"✅ 已创建 {created_count} 个新任务（共 {len(tasks)} 个）")
        print("\n任务列表:")
        for task in tasks:
            print(f"  {task['id']}: {task['title']}")
    else:
        print("❌ 计划不存在，请先生成计划")

if __name__ == "__main__":
    main()
