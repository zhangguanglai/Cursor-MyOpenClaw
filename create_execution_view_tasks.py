"""为完善执行视图功能创建详细任务列表"""

import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.database import Task

def main():
    if len(sys.argv) < 2:
        print("用法: python create_execution_view_tasks.py <case_id>")
        return
    
    case_id = sys.argv[1]
    
    print("=" * 60)
    print("创建完善执行视图功能任务列表")
    print("=" * 60)
    print(f"\n案例 ID: {case_id}")
    
    manager = CaseManager()
    
    # 基于需求创建详细任务列表
    tasks = [
        {
            "id": "task-001",
            "title": "实现 Diff 预览组件",
            "description": "创建 DiffPreview 组件，使用 react-diff-view 或 react-syntax-highlighter 显示代码差异。支持 side-by-side 和 unified 两种显示模式，代码语法高亮，行号显示。",
            "related_files": ["openclaw-studio-frontend/src/components/DiffPreview.tsx"],
            "risk_level": "medium"
        },
        {
            "id": "task-002",
            "title": "实现任务列表和代码生成功能",
            "description": "在执行视图中显示任务列表，支持选择任务并触发 CodingAgent 生成代码补丁。显示生成进度，补丁生成后自动刷新列表。",
            "related_files": ["openclaw-studio-frontend/src/features/execution/ExecutionView.tsx", "openclaw-studio-frontend/src/services/coding.ts"],
            "risk_level": "high"
        },
        {
            "id": "task-003",
            "title": "优化补丁列表显示",
            "description": "优化补丁列表，添加排序功能（按任务 ID、生成时间），添加筛选功能（按任务 ID、文件路径），显示补丁元数据（任务 ID、描述、生成时间）。",
            "related_files": ["openclaw-studio-frontend/src/features/execution/ExecutionView.tsx"],
            "risk_level": "medium"
        },
        {
            "id": "task-004",
            "title": "实现补丁应用状态跟踪",
            "description": "添加补丁应用状态管理，支持标记补丁为已应用，显示应用状态，记录应用历史。",
            "related_files": ["openclaw-studio-frontend/src/features/execution/ExecutionView.tsx", "openclaw_studio/api/v1/coding.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-005",
            "title": "实现复制补丁功能",
            "description": "添加复制补丁内容、复制补丁文件路径、复制补丁描述的功能。使用 Ant Design 的 Button 和 message 组件。",
            "related_files": ["openclaw-studio-frontend/src/features/execution/ExecutionView.tsx"],
            "risk_level": "low"
        },
        {
            "id": "task-006",
            "title": "集成 Diff 预览到执行视图",
            "description": "将 DiffPreview 组件集成到 ExecutionView 中，支持点击补丁查看详细 diff。使用 Modal 或 Drawer 显示。",
            "related_files": ["openclaw-studio-frontend/src/features/execution/ExecutionView.tsx"],
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
    print(f"   运行: python generate_execution_view_code.py {case_id}")

if __name__ == "__main__":
    main()
