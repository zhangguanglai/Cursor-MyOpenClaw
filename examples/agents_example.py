"""
Agent 使用示例

演示如何使用 PlanningAgent、CodingAgent、TestAgent。
"""

import asyncio
import os
from openclaw_core.llm_router import LLMRouter
from openclaw_core.agents import (
    PlanningAgent,
    CodingAgent,
    TestAgent,
    PlanningRequest,
    CodingRequest,
    TestAgentRequest,
)


async def example_planning_agent():
    """PlanningAgent 使用示例"""
    print("=" * 60)
    print("PlanningAgent 示例")
    print("=" * 60)

    # 初始化
    router = LLMRouter()
    agent = PlanningAgent(router, root_dir=".")

    # 构建请求
    request: PlanningRequest = {
        "requirement_description": """
        需求：为 OpenClaw Core 添加一个简单的日志记录功能
        - 支持不同日志级别（DEBUG, INFO, WARNING, ERROR）
        - 可以输出到控制台和文件
        - 支持日志轮转
        """,
        "constraints": [
            "必须兼容现有代码",
            "不引入新的外部依赖（使用标准库）",
            "性能影响最小",
        ],
        "acceptance_criteria": [
            "可以通过配置启用/禁用日志",
            "日志文件可以自动轮转（按大小或时间）",
            "所有现有测试通过",
        ],
        "related_files": [
            "openclaw_core/__init__.py",
        ],
    }

    print("\n生成实现计划...")
    response = await agent.generate_plan(request)

    print("\n" + "=" * 60)
    print("生成的计划（Markdown）:")
    print("=" * 60)
    print(response["plan_markdown"])

    print("\n" + "=" * 60)
    print("提取的子任务:")
    print("=" * 60)
    for i, task in enumerate(response["tasks"], 1):
        print(f"\n任务 {i}: {task.get('title', 'N/A')}")
        print(f"  风险等级: {task.get('risk_level', 'N/A')}")
        if task.get("related_files"):
            print(f"  相关文件: {', '.join(task['related_files'])}")


async def example_coding_agent():
    """CodingAgent 使用示例"""
    print("\n" + "=" * 60)
    print("CodingAgent 示例")
    print("=" * 60)

    router = LLMRouter()
    agent = CodingAgent(router, root_dir=".")

    # 构建请求（基于 PlanningAgent 生成的某个任务）
    request: CodingRequest = {
        "task": {
            "id": "task-1",
            "title": "创建日志模块基础结构",
            "description": "创建 openclaw_core/logger.py，定义基础日志类",
            "estimated_steps": [
                "创建 logger.py 文件",
                "定义 Logger 类",
                "实现基础日志方法（debug, info, warning, error）",
            ],
            "related_files": ["openclaw_core/logger.py"],
            "risk_level": "low",
        },
        "coding_guidelines": "遵循 PEP 8，使用类型提示，添加文档字符串",
        "language": "python",
        "apply_constraints": [
            "只创建新文件，不修改现有文件",
            "使用 Python 标准库 logging 模块",
        ],
    }

    print("\n生成代码修改建议...")
    response = await agent.generate_code(request)

    print("\n" + "=" * 60)
    print("生成的补丁:")
    print("=" * 60)
    for i, patch in enumerate(response["patches"], 1):
        print(f"\n补丁 {i}: {patch['file_path']}")
        print(f"描述: {patch['description']}")
        print(f"Diff:\n{patch['diff']}")

    print("\n" + "=" * 60)
    print("修改理由:")
    print("=" * 60)
    print(response["rationale"])

    if response["test_suggestions"]:
        print("\n" + "=" * 60)
        print("测试建议:")
        print("=" * 60)
        for suggestion in response["test_suggestions"]:
            print(f"- {suggestion}")


async def example_test_agent():
    """TestAgent 使用示例"""
    print("\n" + "=" * 60)
    print("TestAgent 示例")
    print("=" * 60)

    router = LLMRouter()
    agent = TestAgent(router)

    # 构建请求（模拟代码改动）
    request: TestAgentRequest = {
        "changes": [
            {
                "file_path": "openclaw_core/logger.py",
                "diff": """--- a/openclaw_core/logger.py
+++ b/openclaw_core/logger.py
@@ -0,0 +1,20 @@
+import logging
+
+class Logger:
+    def __init__(self, name: str, level: str = "INFO"):
+        self.logger = logging.getLogger(name)
+        self.logger.setLevel(getattr(logging, level))
+    
+    def debug(self, message: str):
+        self.logger.debug(message)
+    
+    def info(self, message: str):
+        self.logger.info(message)
+    
+    def warning(self, message: str):
+        self.logger.warning(message)
+    
+    def error(self, message: str):
+        self.logger.error(message)
""",
            }
        ],
        "context": {
            "related_requirements": ["添加日志记录功能"],
            "runtime_constraints": ["性能敏感", "不能阻塞主流程"],
        },
    }

    print("\n分析代码改动...")
    response = await agent.analyze_changes(request)

    if response["potential_issues"]:
        print("\n" + "=" * 60)
        print("潜在问题:")
        print("=" * 60)
        for issue in response["potential_issues"]:
            print(f"\n[{issue['severity'].upper()}] {issue['description']}")

    if response["test_cases"]:
        print("\n" + "=" * 60)
        print("测试用例建议:")
        print("=" * 60)
        for test_case in response["test_cases"]:
            print(f"\n{test_case['name']} ({test_case['type']})")
            print(f"  目标文件: {test_case['target_file']}")
            if test_case.get("steps"):
                print("  步骤:")
                for step in test_case["steps"]:
                    print(f"    - {step}")

    if response["manual_checklist"]:
        print("\n" + "=" * 60)
        print("人工验收清单:")
        print("=" * 60)
        for item in response["manual_checklist"]:
            print(f"- [ ] {item}")


async def main():
    """主函数"""
    # 检查环境变量
    if not os.environ.get("QWEN_API_KEY") and not os.environ.get("MINIMAX_API_KEY"):
        print("⚠️  警告: 未设置 QWEN_API_KEY 或 MINIMAX_API_KEY 环境变量")
        print("请先设置环境变量后再运行示例\n")
        return

    try:
        await example_planning_agent()
        await example_coding_agent()
        await example_test_agent()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
