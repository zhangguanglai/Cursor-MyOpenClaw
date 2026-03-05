"""
LLMRouter 使用示例

演示如何使用 LLMRouter 调用不同的 LLM 模型。
"""

import asyncio
import os
from openclaw_core.llm_router import LLMRouter, LLMMessage


async def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===\n")

    # 初始化 Router（会自动加载 config/llm.yml）
    router = LLMRouter()

    # 准备消息
    messages: list[LLMMessage] = [
        {"role": "user", "content": "请用一句话介绍 Python 编程语言"}
    ]

    # 方式 1：使用任务类型自动选择模型
    print("方式 1：使用任务类型 'summary' 自动选择模型")
    response = await router.complete_chat(messages, task_type="summary")
    print(f"模型: {response['model']}")
    print(f"回复: {response['content']}\n")

    # 方式 2：直接指定模型
    print("方式 2：直接指定模型 'qwen/qwen-plus'")
    response = await router.complete_chat(messages, model="qwen/qwen-plus")
    print(f"回复: {response['content']}\n")


async def example_planning_task():
    """规划任务示例"""
    print("=== 规划任务示例 ===\n")

    router = LLMRouter()

    messages: list[LLMMessage] = [
        {
            "role": "system",
            "content": "你是一个经验丰富的软件架构师，擅长将需求拆解为可执行的开发计划。",
        },
        {
            "role": "user",
            "content": "需求：实现一个用户登录功能，包括邮箱/密码登录和第三方 OAuth 登录。请给出实现计划。",
        },
    ]

    # 使用 planning 任务类型
    response = await router.complete_chat(messages, task_type="planning")
    print(f"使用的模型: {response['model']}")
    print(f"规划结果:\n{response['content']}\n")
    if response.get("usage"):
        print(f"Token 使用: {response['usage']}\n")


async def example_coding_task():
    """编码任务示例"""
    print("=== 编码任务示例 ===\n")

    router = LLMRouter()

    messages: list[LLMMessage] = [
        {
            "role": "system",
            "content": "你是一个专业的 Python 开发工程师，擅长编写清晰、可维护的代码。",
        },
        {
            "role": "user",
            "content": "请实现一个函数，计算斐波那契数列的第 n 项，要求使用递归和记忆化优化。",
        },
    ]

    # 使用 coding 任务类型
    response = await router.complete_chat(messages, task_type="coding")
    print(f"使用的模型: {response['model']}")
    print(f"代码:\n{response['content']}\n")


async def example_with_custom_params():
    """自定义参数示例"""
    print("=== 自定义参数示例 ===\n")

    router = LLMRouter()

    messages: list[LLMMessage] = [
        {"role": "user", "content": "请生成一个创意故事的开头"}
    ]

    # 使用自定义 temperature 和 max_tokens
    response = await router.complete_chat(
        messages,
        task_type="summary",
        temperature=0.9,  # 更高的创造性
        max_tokens=200,  # 限制长度
    )
    print(f"回复: {response['content']}\n")


async def main():
    """主函数"""
    # 检查环境变量
    if not os.environ.get("QWEN_API_KEY") and not os.environ.get("MINIMAX_API_KEY"):
        print("⚠️  警告: 未设置 QWEN_API_KEY 或 MINIMAX_API_KEY 环境变量")
        print("请先设置环境变量后再运行示例\n")
        return

    try:
        await example_basic_usage()
        await example_planning_task()
        await example_coding_task()
        await example_with_custom_params()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
