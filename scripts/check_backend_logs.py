#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查后端服务状态和配置
"""

import os
import sys
import requests
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_backend_status():
    """检查后端服务状态"""
    print("=" * 60)
    print("检查后端服务状态")
    print("=" * 60)
    print()
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print("✅ 后端服务正在运行")
            print(f"   响应: {response.json()}")
            return True
        else:
            print(f"❌ 后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("   请确保后端服务已启动: python start_backend.py")
        return False
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def check_api_key():
    """检查 API Key 配置"""
    print()
    print("=" * 60)
    print("检查 API Key 配置")
    print("=" * 60)
    print()
    
    qwen_key = os.environ.get('QWEN_API_KEY')
    minimax_key = os.environ.get('MINIMAX_API_KEY')
    
    if qwen_key:
        print(f"✅ QWEN_API_KEY: {qwen_key[:20]}...")
    else:
        print("❌ QWEN_API_KEY: 未设置")
    
    if minimax_key:
        print(f"⚠️  MINIMAX_API_KEY: {minimax_key[:20]}... (可选)")
    else:
        print("⚠️  MINIMAX_API_KEY: 未设置 (可选)")
    
    return bool(qwen_key)

def test_planning_api():
    """测试规划 API"""
    print()
    print("=" * 60)
    print("测试规划 API")
    print("=" * 60)
    print()
    
    case_id = "case-e13da6ed"
    url = f"http://localhost:8000/api/v1/cases/{case_id}/planning"
    
    data = {
        "requirement_description": "实现用户认证系统",
        "related_files": []
    }
    
    print(f"URL: {url}")
    print(f"请求数据: {data}")
    print()
    print("发送请求...")
    
    try:
        response = requests.post(url, json=data, timeout=60)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 规划 API 调用成功")
            print(f"   计划 ID: {result.get('plan_id', 'N/A')}")
            print(f"   任务数量: {len(result.get('tasks', []))}")
            return True
        else:
            print(f"❌ 规划 API 调用失败")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            
            # 尝试解析错误详情
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    print(f"   错误详情: {error_data['detail']}")
            except:
                pass
            
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时（超过 60 秒）")
        return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_router():
    """测试 LLMRouter 初始化"""
    print()
    print("=" * 60)
    print("测试 LLMRouter 初始化")
    print("=" * 60)
    print()
    
    try:
        from openclaw_core.llm_router import LLMRouter
        
        router = LLMRouter()
        print("✅ LLMRouter 初始化成功")
        print(f"   可用 Provider: {list(router.providers.keys())}")
        return True
    except Exception as e:
        print(f"❌ LLMRouter 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print()
    
    # 检查后端服务
    backend_ok = check_backend_status()
    
    # 检查 API Key
    api_key_ok = check_api_key()
    
    # 测试 LLMRouter
    if api_key_ok:
        llm_router_ok = test_llm_router()
    else:
        llm_router_ok = False
        print()
        print("⚠️  跳过 LLMRouter 测试（API Key 未设置）")
    
    # 测试规划 API
    if backend_ok:
        planning_ok = test_planning_api()
    else:
        planning_ok = False
        print()
        print("⚠️  跳过规划 API 测试（后端服务未运行）")
    
    # 总结
    print()
    print("=" * 60)
    print("检查结果汇总")
    print("=" * 60)
    print()
    print(f"后端服务: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"API Key: {'✅ 已配置' if api_key_ok else '❌ 未配置'}")
    print(f"LLMRouter: {'✅ 正常' if llm_router_ok else '❌ 异常'}")
    print(f"规划 API: {'✅ 正常' if planning_ok else '❌ 异常'}")
    print()
    
    if not all([backend_ok, api_key_ok, llm_router_ok, planning_ok]):
        print("⚠️  发现问题，请根据上述信息进行修复")
        print()
        print("建议操作:")
        if not backend_ok:
            print("  1. 启动后端服务: python start_backend.py")
        if not api_key_ok:
            print("  2. 设置 API Key: $env:QWEN_API_KEY='your_key'")
            print("  3. 重启后端服务: .\\scripts\\restart_backend.ps1")
        if not llm_router_ok and api_key_ok:
            print("  4. 重启后端服务以加载新的环境变量")
    else:
        print("🎉 所有检查通过！")
    
    print()
