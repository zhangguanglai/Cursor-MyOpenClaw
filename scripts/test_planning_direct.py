#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接测试规划功能
"""

import os
import sys
import asyncio
from pathlib import Path

# 设置 API Key
os.environ['QWEN_API_KEY'] = 'sk-fe321dca0bf146ca99df33876ad56bbb'

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openclaw_core.llm_router import LLMRouter
from openclaw_core.agents import PlanningAgent

async def test_planning():
    """测试规划功能"""
    print("=" * 60)
    print("直接测试规划功能")
    print("=" * 60)
    print()
    
    # 检查 API Key
    qwen_key = os.environ.get('QWEN_API_KEY')
    if not qwen_key:
        print("❌ QWEN_API_KEY 未设置")
        return False
    
    print(f"✅ QWEN_API_KEY: {qwen_key[:20]}...")
    print()
    
    try:
        # 初始化 LLMRouter
        print("[1/3] 初始化 LLMRouter...")
        router = LLMRouter()
        print("✅ LLMRouter 初始化成功")
        print()
        
        # 初始化 PlanningAgent
        print("[2/3] 初始化 PlanningAgent...")
        agent = PlanningAgent(llm_router=router, root_dir=".")
        print("✅ PlanningAgent 初始化成功")
        print()
        
        # 测试生成计划
        print("[3/3] 生成计划...")
        request = {
            "requirement_description": "实现用户认证系统，包括登录、注册、密码重置功能",
            "related_files": []
        }
        
        print(f"   需求: {request['requirement_description']}")
        print("   等待响应（可能需要 10-30 秒）...")
        print()
        
        result = await agent.generate_plan(request)
        
        print("✅ 计划生成成功！")
        print(f"   计划长度: {len(result.get('plan_markdown', ''))} 字符")
        print(f"   任务数量: {len(result.get('tasks', []))}")
        print()
        
        if result.get('tasks'):
            print("任务列表:")
            for i, task in enumerate(result['tasks'][:5], 1):
                print(f"   {i}. {task.get('title', 'N/A')}")
            if len(result['tasks']) > 5:
                print(f"   ... 还有 {len(result['tasks']) - 5} 个任务")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_planning())
    sys.exit(0 if success else 1)
