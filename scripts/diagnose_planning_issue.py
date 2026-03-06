#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断规划API问题
"""

import os
import sys
import asyncio
import requests
from pathlib import Path

# 设置 API Key
os.environ['QWEN_API_KEY'] = 'sk-fe321dca0bf146ca99df33876ad56bbb'

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_llm_router_init():
    """测试 LLMRouter 初始化"""
    print("=" * 60)
    print("测试 LLMRouter 初始化")
    print("=" * 60)
    print()
    
    try:
        from openclaw_core.llm_router import LLMRouter
        
        print("正在初始化 LLMRouter...")
        router = LLMRouter()
        print("SUCCESS: LLMRouter 初始化成功")
        print(f"可用 Provider: {list(router.providers.keys())}")
        return router
    except Exception as e:
        print(f"ERROR: LLMRouter 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_planning_agent(router):
    """测试 PlanningAgent"""
    print()
    print("=" * 60)
    print("测试 PlanningAgent")
    print("=" * 60)
    print()
    
    try:
        from openclaw_core.agents import PlanningAgent
        
        print("正在初始化 PlanningAgent...")
        agent = PlanningAgent(llm_router=router, root_dir=".")
        print("SUCCESS: PlanningAgent 初始化成功")
        
        print()
        print("测试生成计划...")
        request = {
            "requirement_description": "实现用户认证系统",
            "related_files": []
        }
        
        result = await agent.generate_plan(request)
        
        print("SUCCESS: 计划生成成功")
        print(f"计划长度: {len(result.get('plan_markdown', ''))} 字符")
        print(f"任务数量: {len(result.get('tasks', []))}")
        return True
    except Exception as e:
        print(f"ERROR: PlanningAgent 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_api():
    """测试后端API"""
    print()
    print("=" * 60)
    print("测试后端 API")
    print("=" * 60)
    print()
    
    url = "http://localhost:8000/api/v1/cases/case-e13da6ed/planning"
    data = {
        "requirement_description": "实现用户认证系统",
        "related_files": []
    }
    
    try:
        print(f"URL: {url}")
        print("发送请求...")
        response = requests.post(url, json=data, timeout=60)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: API 调用成功")
            print(f"计划ID: {result.get('plan_id', 'N/A')}")
            print(f"任务数量: {len(result.get('tasks', []))}")
            return True
        else:
            print(f"ERROR: API 调用失败")
            print(f"响应: {response.text}")
            
            # 尝试解析错误详情
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    print(f"错误详情: {error_data['detail']}")
            except:
                pass
            
            return False
    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print()
    print("=" * 60)
    print("规划API问题诊断")
    print("=" * 60)
    print()
    
    # 检查环境变量
    qwen_key = os.environ.get('QWEN_API_KEY')
    print(f"QWEN_API_KEY: {'SET' if qwen_key else 'NOT SET'}")
    if qwen_key:
        print(f"  Value: {qwen_key[:20]}...")
    print()
    
    # 测试 LLMRouter
    router = test_llm_router_init()
    if not router:
        print()
        print("=" * 60)
        print("诊断结果: LLMRouter 初始化失败")
        print("=" * 60)
        print()
        print("建议:")
        print("1. 检查 API Key 是否正确")
        print("2. 检查网络连接")
        print("3. 查看后端服务日志")
        return
    
    # 测试 PlanningAgent
    agent_ok = await test_planning_agent(router)
    if not agent_ok:
        print()
        print("=" * 60)
        print("诊断结果: PlanningAgent 测试失败")
        print("=" * 60)
        print()
        print("建议:")
        print("1. 检查 LLM API 连接")
        print("2. 查看错误堆栈信息")
        return
    
    # 测试后端API
    api_ok = test_backend_api()
    
    # 总结
    print()
    print("=" * 60)
    print("诊断结果汇总")
    print("=" * 60)
    print()
    print(f"LLMRouter: {'OK' if router else 'FAIL'}")
    print(f"PlanningAgent: {'OK' if agent_ok else 'FAIL'}")
    print(f"Backend API: {'OK' if api_ok else 'FAIL'}")
    print()
    
    if not api_ok and agent_ok:
        print("问题分析:")
        print("- PlanningAgent 可以正常工作")
        print("- 但后端 API 返回错误")
        print("- 可能是后端服务启动时环境变量未设置")
        print()
        print("解决方案:")
        print("1. 停止后端服务")
        print("2. 设置环境变量: $env:QWEN_API_KEY='sk-fe321dca0bf146ca99df33876ad56bbb'")
        print("3. 重启后端服务: python start_backend.py")

if __name__ == "__main__":
    asyncio.run(main())
