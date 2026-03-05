"""测试 LLM API 连接"""

import asyncio
import os
from openclaw_core.llm_router import LLMRouter, LLMMessage

async def test_api():
    """测试 API 连接"""
    print("Testing LLM API connection...")
    
    # 设置 API Key
    os.environ["QWEN_API_KEY"] = "sk-fe321dca0bf146ca99df33876ad56bbb"
    os.environ["MINIMAX_API_KEY"] = "sk-api-BLD4n5QgBB0I6Ky0zHksHUNTDQeRVaI53dCw5op0NL_L5LwysXeFGuLyZgpkvC1ZQxHeERVaGfAnEqToIxVCFdNQnSf40D1D5OjvCylrLNVwO8YJtq9nE34"
    
    try:
        router = LLMRouter()
        print(f"Available providers: {list(router.providers.keys())}")
        
        # 测试简单调用
        messages: list[LLMMessage] = [
            {"role": "user", "content": "Say hello in one sentence"}
        ]
        
        print("Calling Qwen API...")
        response = await router.complete_chat(
            messages,
            model="qwen/qwen-plus",
            max_tokens=50,
        )
        
        print(f"Success! Response: {response['content']}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_api())
