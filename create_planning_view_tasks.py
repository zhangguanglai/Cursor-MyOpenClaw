"""为完善规划视图功能创建详细任务列表"""

import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.database import Task

def main():
    case_id = "case-ae080ddd"
    
    print("=" * 60)
    print("创建完善规划视图功能任务列表")
    print("=" * 60)
    print(f"\n案例 ID: {case_id}")
    
    manager = CaseManager()
    
    # 基于需求创建详细任务列表
    tasks = [
        {
            "id": "task-001",
            "title": "安装和配置 Markdown 编辑器依赖",
            "description": "安装 react-markdown、remark-gfm、react-syntax-highlighter 等依赖，配置 Markdown 渲染器。",
            "related_files": ["openclaw-studio-frontend/package.json"],
            "risk_level": "low"
        },
        {
            "id": "task-002",
            "title": "实现 Markdown 编辑器组件",
            "description": "创建 MarkdownEditor 组件，支持编辑和预览模式切换。使用 Ant Design Input.TextArea 作为编辑器，react-markdown 作为预览。",
            "related_files": ["openclaw-studio-frontend/src/components/MarkdownEditor.tsx"],
            "risk_level": "medium"
        },
        {
            "id": "task-003",
            "title": "实现计划保存功能",
            "description": "添加保存计划的 API Hook，支持更新 plan.md。创建 useUpdatePlanMutation Hook。",
            "related_files": ["openclaw-studio-frontend/src/services/planning.ts", "openclaw_studio/api/v1/planning.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-004",
            "title": "实现任务列表表格组件",
            "description": "创建 TaskTable 组件，使用 Ant Design Table 显示任务列表。支持显示任务 ID、标题、描述、状态、风险级别、关联文件。",
            "related_files": ["openclaw-studio-frontend/src/features/planning/TaskTable.tsx"],
            "risk_level": "medium"
        },
        {
            "id": "task-005",
            "title": "实现任务状态管理",
            "description": "添加更新任务状态的 API Hook 和功能。支持将任务状态从 pending 更新为 completed。",
            "related_files": ["openclaw-studio-frontend/src/services/planning.ts", "openclaw_studio/api/v1/planning.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-006",
            "title": "优化 Markdown 渲染",
            "description": "使用 react-markdown + remark-gfm 优化计划展示。添加代码块语法高亮、表格渲染、链接支持。",
            "related_files": ["openclaw-studio-frontend/src/features/planning/PlanningView.tsx"],
            "risk_level": "low"
        },
        {
            "id": "task-007",
            "title": "实现任务详情查看",
            "description": "添加任务详情 Modal，显示任务的完整信息（描述、关联文件、风险级别等）。",
            "related_files": ["openclaw-studio-frontend/src/features/planning/TaskDetailModal.tsx"],
            "risk_level": "low"
        },
        {
            "id": "task-008",
            "title": "实现任务筛选和排序",
            "description": "在任务列表表格中添加筛选功能（按状态、风险级别）和排序功能（按创建时间、风险级别）。",
            "related_files": ["openclaw-studio-frontend/src/features/planning/TaskTable.tsx"],
            "risk_level": "low"
        },
        {
            "id": "task-009",
            "title": "集成到规划视图",
            "description": "将 Markdown 编辑器、任务列表等组件集成到 PlanningView 中。优化布局和用户体验。",
            "related_files": ["openclaw-studio-frontend/src/features/planning/PlanningView.tsx"],
            "risk_level": "medium"
        },
        {
            "id": "task-010",
            "title": "添加响应式设计支持",
            "description": "优化规划视图在不同屏幕尺寸下的显示效果。移动端优化编辑器布局。",
            "related_files": ["openclaw-studio-frontend/src/features/planning/PlanningView.tsx"],
            "risk_level": "low"
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
    print(f"   运行: python generate_planning_view_code.py {case_id}")

if __name__ == "__main__":
    main()
