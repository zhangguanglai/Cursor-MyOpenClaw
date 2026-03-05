"""
更新案例状态脚本

根据案例的实际进展（计划、任务、补丁、测试）自动更新为正确的状态。
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

from openclaw_studio.case_manager import CaseManager

def determine_case_status(case_manager: CaseManager, case_id: str) -> str:
    """
    根据案例的实际进展确定正确的状态
    
    状态判断逻辑：
    1. 如果没有计划 -> created
    2. 如果有计划但没有补丁 -> planning
    3. 如果有补丁但没有测试 -> coding
    4. 如果有测试 -> testing
    5. 如果所有任务都完成 -> completed
    """
    # 检查是否有计划
    plan_data = case_manager.get_plan(case_id)
    if not plan_data:
        return "created"
    
    # 检查是否有任务
    tasks = case_manager.get_tasks(case_id)
    if not tasks:
        return "planning"
    
    # 检查是否有补丁
    patches = case_manager.get_patches(case_id)
    has_patches = len(patches) > 0
    
    # 检查是否有测试结果
    test_results = case_manager.get_latest_test_results(case_id)
    has_test = test_results is not None
    
    # 检查所有任务是否完成
    all_tasks_completed = all(task.status == "completed" for task in tasks) if tasks else False
    
    # 判断状态
    # 优先级：completed > testing > coding > planning > created
    if all_tasks_completed:
        # 所有任务完成，即使没有测试也标记为 completed
        # （测试是可选的，任务完成是主要标志）
        return "completed"
    elif has_test:
        return "testing"
    elif has_patches:
        return "coding"
    elif plan_data:
        return "planning"
    else:
        return "created"

def update_all_case_statuses():
    """更新所有案例的状态"""
    case_manager = CaseManager()
    
    # 获取所有案例
    cases = case_manager.list_cases()
    
    print(f"找到 {len(cases)} 个案例，开始检查状态...\n")
    
    updated_count = 0
    for case in cases:
        current_status = case.status
        correct_status = determine_case_status(case_manager, case.id)
        
        if current_status != correct_status:
            print(f"案例 {case.id}: {case.title}")
            print(f"  当前状态: {current_status} -> 正确状态: {correct_status}")
            case_manager.update_case_status(case.id, correct_status)
            updated_count += 1
            print(f"  [OK] 已更新\n")
        else:
            print(f"案例 {case.id}: {case.title} - 状态正确 ({current_status})")
    
    print(f"\n完成！共更新了 {updated_count} 个案例的状态。")

if __name__ == "__main__":
    update_all_case_statuses()
