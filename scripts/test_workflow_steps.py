#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试完整工作流步骤
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000/api/v1"
CASE_ID = "case-e13da6ed"

def get_tasks():
    """获取任务列表"""
    try:
        response = requests.get(f"{BASE_URL}/cases/{CASE_ID}/plan", timeout=10)
        if response.status_code == 200:
            plan = response.json()
            tasks = plan.get('tasks', [])
            print(f"Found {len(tasks)} tasks")
            return tasks
        else:
            print(f"Failed to get plan: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_code_patch(task_id, task_title, task_description):
    """生成代码补丁"""
    print(f"\nGenerating patch for task: {task_title}")
    print(f"Task ID: {task_id}")
    
    data = {
        "task_id": task_id,
        "task_title": task_title or "Task",
        "task_description": task_description or "",
        "related_files": []
    }
    
    print(f"Request data: {data}")
    
    try:
        print("Sending request...")
        response = requests.post(
            f"{BASE_URL}/cases/{CASE_ID}/tasks/{task_id}/code",
            json=data,
            timeout=120
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            patches = result.get('patches', [])
            print(f"SUCCESS: Generated {len(patches)} patches")
            for patch in patches:
                print(f"  - {patch.get('file_path', 'N/A')}")
            return True
        else:
            print(f"ERROR: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detail: {error_data.get('detail', 'N/A')}")
            except:
                print(f"Response: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print("ERROR: Request timeout")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def generate_test_suggestions():
    """生成测试建议"""
    print("\n" + "=" * 60)
    print("Step 3: Generate Test Suggestions")
    print("=" * 60)
    
    # Get patches
    try:
        patches_response = requests.get(f"{BASE_URL}/cases/{CASE_ID}/patches", timeout=10)
        patches = []
        if patches_response.status_code == 200:
            patches = patches_response.json()
            print(f"Found {len(patches)} patches")
    except:
        patches = []
    
    # Build test request
    test_data = {
        "changes": [
            {
                "file_path": patch.get("file_path", ""),
                "diff": patch.get("diff", "")
            }
            for patch in patches
        ]
    }
    
    try:
        print("Sending request...")
        response = requests.post(
            f"{BASE_URL}/cases/{CASE_ID}/test",
            json=test_data,
            timeout=120
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Test suggestions generated")
            print(f"  Issues: {len(result.get('potential_issues', []))}")
            print(f"  Test cases: {len(result.get('test_cases', []))}")
            print(f"  Checklist: {len(result.get('manual_checklist', []))}")
            return True
        else:
            print(f"ERROR: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Detail: {error_data.get('detail', 'N/A')}")
            except:
                print(f"Response: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print("ERROR: Request timeout")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("=" * 60)
    print("OpenClaw Studio Workflow Test")
    print("=" * 60)
    print(f"\nCase ID: {CASE_ID}")
    
    # Step 1: Get tasks
    print("\n" + "=" * 60)
    print("Step 1: Get Tasks")
    print("=" * 60)
    tasks = get_tasks()
    
    if not tasks:
        print("ERROR: No tasks found. Please generate a plan first.")
        print("\nTo generate a plan:")
        print("1. Visit: http://localhost:5173/cases/case-e13da6ed/plan")
        print("2. Click 'Generate Plan' button")
        return
    
    print(f"\nTasks list:")
    for i, task in enumerate(tasks, 1):
        print(f"  {i}. [{task.get('id', 'N/A')}] {task.get('title', 'N/A')}")
    
    # Step 2: Generate code patch for first task
    print("\n" + "=" * 60)
    print("Step 2: Generate Code Patch")
    print("=" * 60)
    
    task = tasks[0]
    task_id = task.get('id', '')
    task_title = task.get('title', '')
    task_description = task.get('description', '')
    
    if not task_id:
        print("ERROR: Task ID is empty")
        return
    
    success = generate_code_patch(task_id, task_title, task_description)
    
    if not success:
        print("\nWARNING: Patch generation failed. Skipping test suggestions.")
        return
    
    # Wait a bit
    time.sleep(2)
    
    # Step 3: Generate test suggestions
    generate_test_suggestions()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print(f"\nCase ID: {CASE_ID}")
    print(f"\nFrontend URLs:")
    print(f"  Planning: http://localhost:5173/cases/{CASE_ID}/plan")
    print(f"  Execution: http://localhost:5173/cases/{CASE_ID}/execution")
    print(f"  Testing: http://localhost:5173/cases/{CASE_ID}/test")
    print("=" * 60)

if __name__ == "__main__":
    main()
