#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试任务数据库问题
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openclaw_studio.database import CaseDatabase

CASE_ID = "case-e13da6ed"

def main():
    print("=" * 60)
    print("Debug Tasks in Database")
    print("=" * 60)
    print()
    
    db = CaseDatabase()
    
    # Direct SQL query
    cursor = db.conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE case_id = ?", (CASE_ID,))
    rows = cursor.fetchall()
    
    print(f"Direct SQL query found {len(rows)} tasks")
    print()
    
    if rows:
        print("Tasks from direct query:")
        for i, row in enumerate(rows, 1):
            row_dict = dict(row)
            print(f"  {i}. ID: {row_dict.get('id', 'N/A')}")
            print(f"     Title: {row_dict.get('title', 'N/A')[:50]}")
            print(f"     Case ID: {row_dict.get('case_id', 'N/A')}")
            print(f"     Plan ID: {row_dict.get('plan_id', 'N/A')}")
            print()
    
    # Use get_tasks method
    tasks = db.get_tasks(CASE_ID)
    print(f"get_tasks() method found {len(tasks)} tasks")
    print()
    
    # Check get_task for each task ID
    if rows:
        print("Testing get_task() for each task:")
        for row in rows:
            task_id = dict(row).get('id', '')
            if task_id:
                task = db.get_task(task_id)
                if task:
                    print(f"  {task_id}: Found - {task.title[:40]}")
                else:
                    print(f"  {task_id}: NOT FOUND")

if __name__ == "__main__":
    main()
