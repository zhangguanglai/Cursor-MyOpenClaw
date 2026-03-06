#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整工作流测试脚本

测试从创建案例到归档的完整流程
"""

import requests
import json
import time
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:8000/api/v1"

def print_step(step_num, title):
    """打印步骤标题"""
    print("\n" + "=" * 60)
    print(f"步骤 {step_num}: {title}")
    print("=" * 60)

def check_service():
    """检查服务是否运行"""
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=3)
        if response.status_code == 200:
            print("[成功] 后端服务运行正常")
            return True
        else:
            print(f"[失败] 后端服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"[失败] 无法连接到后端服务: {e}")
        print("请确保后端服务已启动: python start_backend.py")
        return False

def create_case():
    """创建测试案例"""
    print_step(1, "创建案例")
    
    case_data = {
        "title": "完整流程测试案例",
        "description": """这是一个用于测试完整开发流程的案例。

## 需求描述

实现一个简单的待办事项管理功能，包括：
- 添加待办事项
- 标记完成
- 删除待办事项
- 列表展示

## 技术要求
- 使用 React 组件
- 状态管理使用 useState
- 数据持久化到 localStorage

## 验收标准
- [ ] 可以添加新的待办事项
- [ ] 可以标记待办事项为完成
- [ ] 可以删除待办事项
- [ ] 列表正确显示所有待办事项"""
    }
    
    try:
        response = requests.post(f"{BASE_URL}/cases", json=case_data, timeout=10)
        if response.status_code == 200:
            case = response.json()
            print(f"[成功] 案例创建成功")
            print(f"  案例 ID: {case['id']}")
            print(f"  标题: {case['title']}")
            print(f"  状态: {case['status']}")
            print(f"\n前端访问: http://localhost:5173/cases/{case['id']}/plan")
            return case
        else:
            print(f"[失败] 创建案例失败: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"[错误] {e}")
        return None

def generate_plan(case_id):
    """生成计划"""
    print_step(2, "生成实现计划")
    
    planning_data = {
        "requirement_description": "实现一个简单的待办事项管理功能",
        "related_files": []
    }
    
    try:
        print("正在生成计划，请稍候...")
        response = requests.post(
            f"{BASE_URL}/cases/{case_id}/planning",
            json=planning_data,
            timeout=120  # 计划生成可能需要较长时间
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[成功] 计划生成成功")
            print(f"  计划 ID: {result.get('plan_id', 'N/A')}")
            print(f"  任务数量: {len(result.get('tasks', []))}")
            
            # 显示任务列表
            tasks = result.get('tasks', [])
            if tasks:
                print("\n生成的任务:")
                for i, task in enumerate(tasks[:5], 1):  # 只显示前5个
                    print(f"  {i}. {task.get('title', 'N/A')}")
                if len(tasks) > 5:
                    print(f"  ... 还有 {len(tasks) - 5} 个任务")
            
            print(f"\n前端查看: http://localhost:5173/cases/{case_id}/plan")
            return True
        else:
            print(f"[失败] 生成计划失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"[错误] {e}")
        return False

def get_tasks(case_id):
    """获取任务列表"""
    try:
        # 通过获取计划来获取任务
        response = requests.get(f"{BASE_URL}/cases/{case_id}/plan", timeout=10)
        if response.status_code == 200:
            plan = response.json()
            return plan.get('tasks', [])
        return []
    except:
        return []

def generate_patch(case_id, task_id, task_title):
    """生成代码补丁"""
    print(f"\n正在为任务生成补丁: {task_title}")
    
    coding_data = {
        "task_title": task_title,
        "task_description": f"实现任务: {task_title}",
        "related_files": []
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/cases/{case_id}/coding",
            json=coding_data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            patches = result.get('patches', [])
            if patches:
                print(f"  [成功] 生成了 {len(patches)} 个补丁")
                for patch in patches:
                    print(f"    - {patch.get('file_path', 'N/A')}")
                return True
            else:
                print(f"  [警告] 未生成补丁")
                return False
        else:
            print(f"  [失败] 生成补丁失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"  [错误] {e}")
        return False

def generate_test(case_id):
    """生成测试建议"""
    print_step(4, "生成测试建议")
    
    test_data = {
        "patches": [],
        "related_files": []
    }
    
    try:
        print("正在生成测试建议，请稍候...")
        response = requests.post(
            f"{BASE_URL}/cases/{case_id}/test",
            json=test_data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"[成功] 测试建议生成成功")
            print(f"  测试 ID: {result.get('test_id', 'N/A')}")
            
            issues = result.get('potential_issues', [])
            test_cases = result.get('test_cases', [])
            checklist = result.get('manual_checklist', [])
            
            print(f"  潜在问题: {len(issues)} 个")
            print(f"  测试用例: {len(test_cases)} 个")
            print(f"  验收清单: {len(checklist)} 项")
            
            print(f"\n前端查看: http://localhost:5173/cases/{case_id}/test")
            return True
        else:
            print(f"[失败] 生成测试建议失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"[错误] {e}")
        return False

def check_history(case_id):
    """检查历史记录"""
    print_step(5, "查看历史记录")
    
    try:
        response = requests.get(
            f"{BASE_URL}/cases/{case_id}/history",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            history = result.get('history', [])
            print(f"[成功] 找到 {len(history)} 条历史记录")
            
            # 按类型统计
            type_counts = {}
            for item in history:
                item_type = item.get('type', 'unknown')
                type_counts[item_type] = type_counts.get(item_type, 0) + 1
            
            print("\n历史记录统计:")
            for item_type, count in type_counts.items():
                print(f"  {item_type}: {count} 条")
            
            print(f"\n前端查看: http://localhost:5173/cases/{case_id}/history")
            return True
        else:
            print(f"[失败] 获取历史记录失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"[错误] {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("OpenClaw Studio 完整工作流测试")
    print("=" * 60)
    
    # 检查服务
    if not check_service():
        return
    
    # 创建案例
    case = create_case()
    if not case:
        return
    
    case_id = case['id']
    
    # 生成计划
    if not generate_plan(case_id):
        print("\n[警告] 计划生成失败，跳过后续步骤")
        return
    
    # 等待一下让计划保存完成
    time.sleep(2)
    
    # 获取任务并生成补丁
    print_step(3, "生成代码补丁")
    tasks = get_tasks(case_id)
    if tasks:
        # 只为第一个任务生成补丁（避免时间过长）
        if len(tasks) > 0:
            task = tasks[0]
            task_id = task.get('id', '')
            task_title = task.get('title', '')
            generate_patch(case_id, task_id, task_title)
            print(f"\n前端查看: http://localhost:5173/cases/{case_id}/execution")
    else:
        print("[警告] 未找到任务，跳过补丁生成")
    
    # 生成测试建议
    time.sleep(1)
    generate_test(case_id)
    
    # 查看历史
    time.sleep(1)
    check_history(case_id)
    
    # 总结
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print(f"\n案例 ID: {case_id}")
    print(f"\n前端访问地址:")
    print(f"  规划视图: http://localhost:5173/cases/{case_id}/plan")
    print(f"  执行视图: http://localhost:5173/cases/{case_id}/execution")
    print(f"  测试视图: http://localhost:5173/cases/{case_id}/test")
    print(f"  历史视图: http://localhost:5173/cases/{case_id}/history")
    print("\n请在浏览器中访问上述地址查看完整功能！")
    print("=" * 60)

if __name__ == "__main__":
    main()
