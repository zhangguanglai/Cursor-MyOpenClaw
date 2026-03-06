#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中所有任务
"""

import sys
import sqlite3
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("=" * 60)
    print("Check All Tasks in Database")
    print("=" * 60)
    print()
    
    db_path = Path("openclaw_studio.db")
    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all tasks
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    
    print(f"Total tasks in database: {len(rows)}")
    print()
    
    if rows:
        print("All tasks:")
        for i, row in enumerate(rows, 1):
            row_dict = dict(row)
            print(f"  {i}. ID: {row_dict.get('id', 'N/A')}")
            print(f"     Case ID: {row_dict.get('case_id', 'N/A')}")
            print(f"     Title: {row_dict.get('title', 'N/A')[:50]}")
            print()
    
    # Check tasks for specific case
    case_id = "case-e13da6ed"
    cursor.execute("SELECT * FROM tasks WHERE case_id = ?", (case_id,))
    case_tasks = cursor.fetchall()
    
    print(f"Tasks for case {case_id}: {len(case_tasks)}")
    print()
    
    conn.close()

if __name__ == "__main__":
    main()
