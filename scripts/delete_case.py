#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
删除案例脚本
"""

import requests
import sys

def delete_case(case_id: str):
    """删除指定案例"""
    try:
        response = requests.delete(
            f"http://localhost:8000/api/v1/cases/{case_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("=" * 60)
            print("[成功] 案例删除成功！")
            print("=" * 60)
            print(f"案例 ID: {result.get('case_id', case_id)}")
            print(f"消息: {result.get('message', '')}")
            print("=" * 60)
            return True
        else:
            print(f"[失败] 删除失败: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"[错误] {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python delete_case.py <case_id>")
        print("示例: python delete_case.py case-2a73c7be")
        sys.exit(1)
    
    case_id = sys.argv[1]
    delete_case(case_id)
