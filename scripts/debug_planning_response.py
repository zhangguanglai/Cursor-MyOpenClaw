"""
调试规划响应

查看 PlanningAgent 的实际响应内容，分析任务提取失败的原因
"""

import sys
import io
import asyncio
from pathlib import Path

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openclaw_core.llm_router import LLMRouter
from openclaw_core.agents import PlanningAgent

async def debug_planning():
    """调试规划响应"""
    print("=" * 60)
    print("规划响应调试")
    print("=" * 60)
    
    router = LLMRouter()
    agent = PlanningAgent(router)
    
    request = {
        "requirement_description": "添加一个简单的日志功能，记录用户操作",
        "related_files": [],
    }
    
    print("\n[步骤 1] 调用 PlanningAgent...")
    print(f"需求: {request['requirement_description']}")
    
    try:
        response = await agent.generate_plan(request)
        
        plan_markdown = response.get("plan_markdown", "")
        tasks = response.get("tasks", [])
        
        print(f"\n[步骤 2] 响应分析")
        print(f"计划长度: {len(plan_markdown)} 字符")
        print(f"任务数量: {len(tasks)}")
        
        # 保存响应到文件以便分析
        debug_file = Path("debug_planning_response.md")
        debug_file.write_text(plan_markdown, encoding="utf-8")
        print(f"\n响应已保存到: {debug_file}")
        
        # 显示响应内容的关键部分
        print("\n[步骤 3] 响应内容分析")
        print("\n前 1000 字符:")
        print("-" * 60)
        print(plan_markdown[:1000])
        print("-" * 60)
        
        # 查找可能的任务部分
        import re
        print("\n[步骤 4] 查找任务相关部分")
        
        # 查找 JSON 代码块
        json_match = re.search(r"```json\s*(\[.*?\])\s*```", plan_markdown, re.DOTALL)
        if json_match:
            print("✅ 找到 JSON 代码块")
            print(f"JSON 内容: {json_match.group(1)[:200]}...")
        else:
            print("❌ 未找到 JSON 代码块")
        
        # 查找任务列表部分
        task_section = re.search(
            r"(?:##|###)\s*任务列表?.*?\n(.*?)(?=\n##|\Z)",
            plan_markdown,
            re.DOTALL | re.IGNORECASE
        )
        if task_section:
            print("✅ 找到任务列表部分")
            print(f"任务列表内容: {task_section.group(1)[:300]}...")
        else:
            print("❌ 未找到任务列表部分")
        
        # 查找所有标题
        headings = re.findall(r"^(##+)\s+(.+)$", plan_markdown, re.MULTILINE)
        if headings:
            print(f"\n找到 {len(headings)} 个标题:")
            for level, title in headings[:10]:
                print(f"  {level} {title}")
        
        # 测试任务提取
        print("\n[步骤 5] 测试任务提取")
        extracted_tasks = PlanningAgent._extract_tasks_from_response(plan_markdown)
        print(f"提取的任务数: {len(extracted_tasks)}")
        
        if extracted_tasks:
            print("\n提取的任务:")
            for i, task in enumerate(extracted_tasks, 1):
                print(f"  {i}. {task.get('title', 'N/A')}")
        else:
            print("⚠️  未能提取任务")
            print("\n尝试手动分析响应格式...")
            
    except Exception as e:
        print(f"\n❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(debug_planning())
    except KeyboardInterrupt:
        print("\n\n调试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
