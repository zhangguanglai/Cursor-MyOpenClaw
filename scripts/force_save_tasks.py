#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
强制保存任务到数据库（忽略已存在检查）
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.database import Task

CASE_ID = "case-e13da6ed"

def main():
    print("=" * 60)
    print("Force Save Tasks to Database")
    print("=" * 60)
    print()
    
    case_manager = CaseManager()
    
    # Load tasks from plan.json
    plan_json_path = Path(f"cases/{CASE_ID}/plan.json")
    if not plan_json_path.exists():
        print(f"ERROR: plan.json not found at {plan_json_path}")
        return
    
    tasks_data = json.loads(plan_json_path.read_text(encoding="utf-8"))
    print(f"Found {len(tasks_data)} tasks in plan.json")
    print()
    
    # Get existing plan
    plan_data = case_manager.get_plan(CASE_ID)
    if not plan_data:
        print("ERROR: Plan not found in database")
        return
    
    plan = plan_data.get("plan")
    if not plan:
        print("ERROR: Plan object not found")
        return
    
    plan_id = plan.id
    print(f"Plan ID: {plan_id}")
    print()
    
    # Delete existing tasks first
    print("Deleting existing tasks...")
    db = case_manager.db
    cursor = db.conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE case_id = ?", (CASE_ID,))
    db.conn.commit()
    deleted = cursor.rowcount
    print(f"Deleted {deleted} existing tasks")
    print()
    
    # Save tasks to database
    print("Saving tasks to database...")
    saved_count = 0
    
    for task_data in tasks_data:
        original_task_id = task_data.get("id", "")
        if not original_task_id:
            print(f"  WARNING: Task without ID, skipping")
            continue
        
        # Generate new task ID to avoid conflicts
        import uuid
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        
        # Create new task
        import json as json_module
        related_files = json_module.dumps(task_data.get("related_files", [])) if task_data.get("related_files") else None
        
        task = Task(
            id=task_id,
            case_id=CASE_ID,
            plan_id=plan_id,
            title=task_data.get("title", ""),
            description=task_data.get("description", ""),
            status="pending",
            related_files=related_files,
            risk_level=task_data.get("risk_level", "medium"),
        )
        
        try:
            db.create_task(task)
            print(f"  SAVED: Task {task_id} - {task.title[:40]}")
            saved_count += 1
        except Exception as e:
            print(f"  ERROR: Failed to save task {task_id}: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total tasks in plan.json: {len(tasks_data)}")
    print(f"Saved to database: {saved_count}")
    print()
    
    # Verify
    db_tasks = case_manager.get_tasks(CASE_ID)
    print(f"Tasks in database now: {len(db_tasks)}")
    if db_tasks:
        print("\nTask list:")
        for i, task in enumerate(db_tasks, 1):
            print(f"  {i}. [{task.id}] {task.title}")

if __name__ == "__main__":
    main()
