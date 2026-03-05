"""为完善历史视图功能创建详细任务列表"""

import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.database import Task

def main():
    if len(sys.argv) < 2:
        print("用法: python create_history_view_tasks.py <case_id>")
        return
    
    case_id = sys.argv[1]
    
    print("=" * 60)
    print("创建完善历史视图功能任务列表")
    print("=" * 60)
    print(f"\n案例 ID: {case_id}")
    
    manager = CaseManager()
    
    # 基于需求创建详细任务列表
    tasks = [
        {
            "id": "task-001",
            "title": "实现时间线组件",
            "description": "创建 TimelineView 组件，使用 Ant Design Timeline 组件展示案例开发历史。支持事件类型图标、时间显示、事件描述。",
            "related_files": ["openclaw-studio-frontend/src/features/history/TimelineView.tsx"],
            "risk_level": "medium"
        },
        {
            "id": "task-002",
            "title": "实现事件详情 Modal",
            "description": "创建 EventDetailModal 组件，显示事件的详细信息。支持 Markdown 渲染、代码高亮、JSON 格式化。",
            "related_files": ["openclaw-studio-frontend/src/features/history/EventDetailModal.tsx"],
            "risk_level": "medium"
        },
        {
            "id": "task-003",
            "title": "实现事件筛选功能",
            "description": "添加事件类型筛选（创建、规划、编码、测试、应用）和时间范围筛选。使用 Ant Design Select 和 DatePicker。",
            "related_files": ["openclaw-studio-frontend/src/features/history/HistoryView.tsx"],
            "risk_level": "low"
        },
        {
            "id": "task-004",
            "title": "实现统计信息展示",
            "description": "添加统计信息卡片，显示案例总体统计（任务数、补丁数、测试次数等）和各阶段耗时。使用 Ant Design Card 和 Statistic。",
            "related_files": ["openclaw-studio-frontend/src/features/history/StatisticsCard.tsx"],
            "risk_level": "low"
        },
        {
            "id": "task-005",
            "title": "集成到历史视图",
            "description": "将 TimelineView、EventDetailModal、StatisticsCard 等组件集成到 HistoryView 中。优化布局和用户体验。",
            "related_files": ["openclaw-studio-frontend/src/features/history/HistoryView.tsx"],
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
    print(f"   运行: python generate_history_view_code.py {case_id}")

if __name__ == "__main__":
    main()
