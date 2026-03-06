#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试后端服务环境变量
通过API检查后端服务是否能读取到环境变量
"""

import requests
import json

def test_backend_env():
    """测试后端服务环境"""
    print("=" * 60)
    print("测试后端服务环境变量")
    print("=" * 60)
    print()
    
    # 测试规划API，获取详细错误信息
    url = "http://localhost:8000/api/v1/cases/case-e13da6ed/planning"
    data = {
        "requirement_description": "实现用户认证系统",
        "related_files": []
    }
    
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    print()
    print("发送请求...")
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: 规划API调用成功")
            print(f"计划ID: {result.get('plan_id', 'N/A')}")
            print(f"任务数量: {len(result.get('tasks', []))}")
            return True
        else:
            print(f"ERROR: 规划API调用失败")
            print(f"状态码: {response.status_code}")
            print()
            print("响应内容:")
            print(response.text)
            print()
            
            # 尝试解析JSON错误详情
            try:
                error_data = response.json()
                if isinstance(error_data, dict) and 'detail' in error_data:
                    print("错误详情:")
                    print(error_data['detail'])
            except:
                pass
            
            return False
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_backend_env()
