#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中的任务
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openclaw_studio.case_manager import CaseManager

CASE_ID = "case-e13da6ed"

def main():
    print("=" * 60)
    print("Check Tasks in Database")
    print("=" * 60)
    print()
    
    case_manager = CaseManager()
    
    # Get tasks from database
    tasks = case_manager.get_tasks(CASE_ID)
    print(f"Tasks in database: {len(tasks)}")
    print()
    
    if tasks:
        print("Task list:")
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. [{task.id}] {task.title}")
            print(f"     Description: {task.description[:50] if task.description else 'N/A'}...")
            print(f"     Status: {task.status}")
            print()
    else:
        print("No tasks found in database")
        print()
        print("Checking plan.json file...")
        plan_data = case_manager.get_plan(CASE_ID)
        if plan_data:
            plan_json = case_manager.storage.load_plan_json(CASE_ID)
            if plan_json:
                print(f"Tasks in plan.json: {len(plan_json)}")
                for i, task in enumerate(plan_json[:5], 1):
                    print(f"  {i}. [{task.get('id', 'N/A')}] {task.get('title', 'N/A')}")
            else:
                print("plan.json not found or empty")
        else:
            print("Plan not found")

if __name__ == "__main__":
    main()
