"""
测试 LLM API 连接

验证 API Key 配置和 LLM API 连接是否正常
"""

import sys
import io
import asyncio
import os

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pathlib import Path
from openclaw_core.llm_router import LLMRouter, LLMMessage
from openclaw_core.logger import get_logger

logger = get_logger("openclaw.test_llm")


async def test_llm_connection():
    """测试 LLM API 连接"""
    print("=" * 60)
    print("LLM API 连接测试")
    print("=" * 60)
    
    # 检查 API Key
    print("\n[检查] API Key 配置")
    qwen_key = os.environ.get("QWEN_API_KEY")
    minimax_key = os.environ.get("MINIMAX_API_KEY")
    
    print(f"QWEN_API_KEY: {'✅ 已设置' if qwen_key else '❌ 未设置'}")
    print(f"MINIMAX_API_KEY: {'✅ 已设置' if minimax_key else '❌ 未设置'}")
    
    if not qwen_key and not minimax_key:
        print("\n⚠️  警告: 没有配置任何 API Key，LLM 功能将无法使用")
        print("   请设置环境变量:")
        print("   $env:QWEN_API_KEY='your_key'")
        print("   或")
        print("   $env:MINIMAX_API_KEY='your_key'")
        return False
    
    # 测试 LLMRouter
    print("\n[测试] LLMRouter 初始化")
    try:
        router = LLMRouter()
        print("✅ LLMRouter 初始化成功")
    except Exception as e:
        print(f"❌ LLMRouter 初始化失败: {e}")
        return False
    
    # 测试简单对话
    print("\n[测试] 简单对话测试")
    try:
        messages: list[LLMMessage] = [
            {"role": "user", "content": "你好，请回复'测试成功'"}
        ]
        print("   发送消息: 你好，请回复'测试成功'")
        print("   等待响应...")
        
        response = await router.complete_chat(messages, task_type="summary")
        content = response.get("content", "")
        
        if content:
            print(f"✅ 收到响应: {content[:100]}...")
            return True
        else:
            print("❌ 响应为空")
            return False
    except Exception as e:
        print(f"❌ 对话测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_planning_agent():
    """测试 PlanningAgent"""
    print("\n" + "=" * 60)
    print("PlanningAgent 测试")
    print("=" * 60)
    
    from openclaw_core.agents import PlanningAgent
    
    try:
        router = LLMRouter()
        agent = PlanningAgent(router)
        
        print("\n[测试] 生成简单计划")
        request = {
            "requirement_description": "添加一个简单的日志功能，记录用户操作",
            "related_files": [],
        }
        
        print("   需求: 添加一个简单的日志功能，记录用户操作")
        print("   等待 PlanningAgent 响应...")
        
        response = await agent.generate_plan(request)
        
        plan_markdown = response.get("plan_markdown", "")
        tasks = response.get("tasks", [])
        
        print(f"✅ 计划生成成功")
        print(f"   计划长度: {len(plan_markdown)} 字符")
        print(f"   任务数量: {len(tasks)}")
        
        if tasks:
            print("\n   任务列表:")
            for i, task in enumerate(tasks[:5], 1):  # 只显示前5个
                print(f"   {i}. {task.get('title', 'N/A')}")
            if len(tasks) > 5:
                print(f"   ... 还有 {len(tasks) - 5} 个任务")
        else:
            print("   ⚠️  警告: 没有生成任务")
        
        return len(tasks) > 0
    except Exception as e:
        print(f"❌ PlanningAgent 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    try:
        # 测试 LLM 连接
        llm_ok = await test_llm_connection()
        
        if not llm_ok:
            print("\n⚠️  LLM 连接测试失败，跳过 PlanningAgent 测试")
            return
        
        # 测试 PlanningAgent
        planning_ok = await test_planning_agent()
        
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)
        print(f"LLM 连接: {'✅ 通过' if llm_ok else '❌ 失败'}")
        print(f"PlanningAgent: {'✅ 通过' if planning_ok else '❌ 失败'}")
        
        if llm_ok and planning_ok:
            print("\n🎉 所有测试通过！")
        else:
            print("\n⚠️  部分测试失败，请检查配置和日志")
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
