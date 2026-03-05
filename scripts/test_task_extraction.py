"""
测试任务提取逻辑

测试 PlanningAgent 的任务提取功能
"""

import sys
import io
from pathlib import Path

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openclaw_core.agents import PlanningAgent

def test_task_extraction():
    """测试任务提取"""
    print("=" * 60)
    print("任务提取测试")
    print("=" * 60)
    
    # 读取一个实际的计划文件
    plan_file = Path("cases/case-3af5da41/plan.md")
    if not plan_file.exists():
        print(f"❌ 计划文件不存在: {plan_file}")
        return
    
    content = plan_file.read_text(encoding="utf-8")
    print(f"\n计划文件长度: {len(content)} 字符")
    print(f"计划内容预览（前 500 字符）:\n{content[:500]}...\n")
    
    # 测试任务提取
    print("\n[测试] 提取任务...")
    tasks = PlanningAgent._extract_tasks_from_response(content)
    
    print(f"\n提取结果: {len(tasks)} 个任务")
    
    if tasks:
        print("\n任务列表:")
        for i, task in enumerate(tasks, 1):
            print(f"\n{i}. {task.get('title', 'N/A')}")
            print(f"   ID: {task.get('id', 'N/A')}")
            print(f"   描述: {task.get('description', 'N/A')[:100]}...")
            print(f"   风险等级: {task.get('risk_level', 'N/A')}")
    else:
        print("\n⚠️  没有提取到任务")
        print("\n尝试查找可能包含任务的部分...")
        
        import re
        # 查找所有可能的任务标记
        task_markers = re.findall(r"(?:任务|Task|##|###).*", content[:2000], re.IGNORECASE)
        if task_markers:
            print("\n找到的可能任务标记:")
            for marker in task_markers[:10]:
                print(f"  - {marker[:80]}...")


if __name__ == "__main__":
    try:
        test_task_extraction()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
