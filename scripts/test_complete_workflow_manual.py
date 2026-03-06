#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手动测试完整工作流
包括：生成代码补丁、生成测试建议
"""

import requests
import json
import time
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"
CASE_ID = "case-e13da6ed"

def print_step(step_num, title):
    """打印步骤标题"""
    print("\n" + "=" * 60)
    print(f"步骤 {step_num}: {title}")
    print("=" * 60)

def get_tasks():
    """获取任务列表"""
    try:
        response = requests.get(f"{BASE_URL}/cases/{CASE_ID}/plan", timeout=10)
        if response.status_code == 200:
            plan = response.json()
            tasks = plan.get('tasks', [])
            print(f"从计划中获取到 {len(tasks)} 个任务")
            return tasks
        elif response.status_code == 404:
            print("计划不存在，请先生成计划")
            return []
        else:
            print(f"获取计划失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"获取任务列表失败: {e}")
        return []

def generate_patch(task_id, task_title, task_description):
    """生成代码补丁"""
    print(f"\n正在为任务生成补丁: {task_title}")
    
    coding_data = {
        "task_title": task_title,
        "task_description": task_description,
        "related_files": []
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/cases/{CASE_ID}/tasks/{task_id}/code",
            json=coding_data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            patches = result.get('patches', [])
            if patches:
                print(f"  SUCCESS: 生成了 {len(patches)} 个补丁")
                for patch in patches:
                    print(f"    - {patch.get('file_path', 'N/A')}")
                return True
            else:
                print(f"  WARNING: 未生成补丁")
                return False
        else:
            print(f"  ERROR: 生成补丁失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  错误详情: {error_data.get('detail', 'N/A')}")
            except:
                print(f"  响应: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print(f"  ERROR: 请求超时（超过 120 秒）")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def generate_test():
    """生成测试建议"""
    print_step(3, "生成测试建议")
    
    # 获取所有补丁
    try:
        patches_response = requests.get(f"{BASE_URL}/cases/{CASE_ID}/patches", timeout=10)
        patches = []
        if patches_response.status_code == 200:
            patches = patches_response.json()
        
        # 构建测试请求
        test_data = {
            "changes": [
                {
                    "file_path": patch.get("file_path", ""),
                    "diff": patch.get("diff", "")
                }
                for patch in patches
            ]
        }
    except:
        test_data = {"changes": []}
    
    try:
        print("正在生成测试建议，请稍候...")
        response = requests.post(
            f"{BASE_URL}/cases/{CASE_ID}/test",
            json=test_data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: 测试建议生成成功")
            print(f"  测试 ID: {result.get('test_id', 'N/A')}")
            
            issues = result.get('potential_issues', [])
            test_cases = result.get('test_cases', [])
            checklist = result.get('manual_checklist', [])
            
            print(f"  潜在问题: {len(issues)} 个")
            if issues:
                for i, issue in enumerate(issues[:3], 1):
                    print(f"    {i}. [{issue.get('severity', 'N/A')}] {issue.get('description', 'N/A')[:50]}...")
            
            print(f"  测试用例: {len(test_cases)} 个")
            if test_cases:
                for i, tc in enumerate(test_cases[:3], 1):
                    print(f"    {i}. {tc.get('description', 'N/A')[:50]}...")
            
            print(f"  验收清单: {len(checklist)} 项")
            if checklist:
                for i, item in enumerate(checklist[:3], 1):
                    print(f"    {i}. {item[:50]}...")
            
            print(f"\n前端查看: http://localhost:5173/cases/{CASE_ID}/test")
            return True
        else:
            print(f"ERROR: 生成测试建议失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误详情: {error_data.get('detail', 'N/A')}")
            except:
                print(f"响应: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print("ERROR: 请求超时（超过 120 秒）")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("OpenClaw Studio 完整工作流测试")
    print("=" * 60)
    print(f"\n案例 ID: {CASE_ID}")
    
    # 步骤 1: 获取任务列表
    print_step(1, "获取任务列表")
    tasks = get_tasks()
    if not tasks:
        print("ERROR: 未找到任务，请先生成计划")
        return
    
    print(f"找到 {len(tasks)} 个任务:")
    for i, task in enumerate(tasks, 1):
        print(f"  {i}. [{task.get('id', 'N/A')}] {task.get('title', 'N/A')}")
    
    # 步骤 2: 生成代码补丁
    print_step(2, "生成代码补丁")
    
    # 只为第一个任务生成补丁（避免时间过长）
    if len(tasks) > 0:
        task = tasks[0]
        task_id = task.get('id', '')
        task_title = task.get('title', '')
        task_description = task.get('description', '')
        
        if not task_id:
            print("ERROR: 任务 ID 为空")
            return
        
        success = generate_patch(task_id, task_title, task_description)
        if success:
            print(f"\n前端查看: http://localhost:5173/cases/{CASE_ID}/execution")
        else:
            print("\nWARNING: 补丁生成失败，跳过测试建议生成")
            return
    else:
        print("WARNING: 没有可用的任务")
        return
    
    # 等待一下让补丁保存完成
    time.sleep(2)
    
    # 步骤 3: 生成测试建议
    generate_test()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print(f"\n案例 ID: {CASE_ID}")
    print(f"\n前端访问地址:")
    print(f"  规划视图: http://localhost:5173/cases/{CASE_ID}/plan")
    print(f"  执行视图: http://localhost:5173/cases/{CASE_ID}/execution")
    print(f"  测试视图: http://localhost:5173/cases/{CASE_ID}/test")
    print("\n请在浏览器中访问上述地址查看完整功能！")
    print("=" * 60)

if __name__ == "__main__":
    main()
