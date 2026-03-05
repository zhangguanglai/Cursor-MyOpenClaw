"""为完善测试视图功能创建详细任务列表"""

import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.database import Task

def main():
    if len(sys.argv) < 2:
        print("用法: python create_testing_view_tasks.py <case_id>")
        return
    
    case_id = sys.argv[1]
    
    print("=" * 60)
    print("创建完善测试视图功能任务列表")
    print("=" * 60)
    print(f"\n案例 ID: {case_id}")
    
    manager = CaseManager()
    
    # 基于需求创建详细任务列表
    tasks = [
        {
            "id": "task-001",
            "title": "实现测试建议展示组件",
            "description": "创建 TestSuggestions 组件，显示潜在问题列表和测试用例列表。使用 Ant Design List 和 Card 组件，支持问题筛选（按严重程度）和测试用例展开/折叠。",
            "related_files": ["openclaw-studio-frontend/src/features/testing/TestSuggestions.tsx"],
            "risk_level": "medium"
        },
        {
            "id": "task-002",
            "title": "实现验收清单组件",
            "description": "创建 Checklist 组件，显示验收清单列表（checkbox 格式）。支持勾选/取消勾选，显示完成进度，保存验收状态。",
            "related_files": ["openclaw-studio-frontend/src/features/testing/Checklist.tsx"],
            "risk_level": "medium"
        },
        {
            "id": "task-003",
            "title": "优化 Markdown 渲染",
            "description": "在测试视图中使用 react-markdown + remark-gfm 优化 Markdown 渲染。添加代码块语法高亮、列表渲染优化。",
            "related_files": ["openclaw-studio-frontend/src/features/testing/TestingView.tsx"],
            "risk_level": "low"
        },
        {
            "id": "task-004",
            "title": "实现测试结果管理",
            "description": "添加测试结果历史显示、重新生成测试建议功能、显示测试生成时间。",
            "related_files": ["openclaw-studio-frontend/src/features/testing/TestingView.tsx", "openclaw-studio-frontend/src/services/testing.ts"],
            "risk_level": "medium"
        },
        {
            "id": "task-005",
            "title": "集成到测试视图",
            "description": "将 TestSuggestions、Checklist 等组件集成到 TestingView 中。优化布局和用户体验。",
            "related_files": ["openclaw-studio-frontend/src/features/testing/TestingView.tsx"],
            "risk_level": "medium"
        },
    ]
    
    print(f"\n📋 创建 {len(tasks)} 个任务...")
    
    # 获取计划
    plan_data = manager.get_plan(case_id)
    if not plan_data:
        print("❌ 计划不存在")
        return
    
    plan = plan_data.get("plan")
    if not plan:
        print("❌ 计划对象不存在")
        return
    
    plan_id = plan.id
    
    # 更新计划 JSON
    plan_json_path = Path(f"cases/{case_id}/plan.json")
    plan_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(plan_json_path, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 计划 JSON 已更新: {plan_json_path}")
    
    # 保存任务到数据库
    created_count = 0
    updated_count = 0
    
    for task_data in tasks:
        task_id = task_data["id"]
        related_files = json.dumps(task_data.get("related_files", [])) if task_data.get("related_files") else None
        
        # 检查任务是否已存在
        existing_task = manager.get_task(task_id)
        if existing_task:
            # 更新现有任务
            manager.db.update_task(
                task_id,
                title=task_data["title"],
                description=task_data.get("description", ""),
                related_files=related_files,
                risk_level=task_data.get("risk_level", "medium"),
            )
            updated_count += 1
            print(f"   ↻ 任务 {task_id} 已更新")
            continue
        
        task = Task(
            id=task_id,
            case_id=case_id,
            plan_id=plan_id,
            title=task_data["title"],
            description=task_data.get("description", ""),
            status="pending",
            related_files=related_files,
            risk_level=task_data.get("risk_level", "medium"),
        )
        
        try:
            manager.db.create_task(task)
            created_count += 1
            print(f"   ✅ 任务 {task_id} 已创建")
        except Exception as e:
            print(f"   ⚠️  任务 {task_id} 创建失败: {e}")
    
    manager.close()
    
    print(f"\n✅ 任务创建完成")
    print(f"   新建: {created_count}")
    print(f"   更新: {updated_count}")
    print(f"   总计: {len(tasks)}")
    
    print(f"\n📋 任务列表:")
    for task in tasks:
        print(f"   {task['id']}: {task['title']}")
    
    print(f"\n下一步: 开始为任务生成代码")
    print(f"   运行: python generate_testing_view_code.py {case_id}")

if __name__ == "__main__":
    main()
