#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试规划 API 脚本
"""

import requests
import json
import sys

def test_planning_api(case_id):
    """测试规划 API"""
    url = f"http://localhost:8000/api/v1/cases/{case_id}/planning"
    
    data = {
        "requirement_description": "实现用户认证系统",
        "related_files": []
    }
    
    print("=" * 60)
    print("测试规划 API")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print("=" * 60)
    
    try:
        print("\n发送请求...")
        response = requests.post(url, json=data, timeout=120)
        
        print(f"\n状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n[成功] 计划生成成功！")
            print(f"计划 ID: {result.get('plan_id', 'N/A')}")
            print(f"任务数量: {len(result.get('tasks', []))}")
            print(f"计划内容长度: {len(result.get('plan_markdown', ''))}")
            return True
        else:
            print(f"\n[失败] 状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n[错误] 请求超时（超过 120 秒）")
        return False
    except requests.exceptions.ConnectionError:
        print("\n[错误] 无法连接到后端服务")
        print("请确保后端服务已启动: python start_backend.py")
        return False
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python debug_planning_api.py <case_id>")
        print("示例: python debug_planning_api.py case-e13da6ed")
        sys.exit(1)
    
    case_id = sys.argv[1]
    test_planning_api(case_id)
