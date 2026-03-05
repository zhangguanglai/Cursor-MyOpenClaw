"""
端到端测试脚本

测试完整的开发流程：创建案例 → 生成计划 → 生成代码 → 测试 → 归档
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

from openclaw_studio.case_manager import CaseManager
from openclaw_core.agents import PlanningAgent, CodingAgent, TestAgent
from openclaw_core.llm_router import LLMRouter
from openclaw_core.logger import get_logger

logger = get_logger("openclaw.e2e_test")


async def test_e2e_flow():
    """测试完整的端到端流程"""
    print("=" * 60)
    print("开始端到端测试")
    print("=" * 60)
    
    case_manager = CaseManager()
    router = LLMRouter()
    
    # 步骤 1: 创建案例
    print("\n[步骤 1/5] 创建测试案例...")
    case = case_manager.create_case(
        title="E2E 测试案例：添加用户认证功能",
        description="""这是一个端到端测试案例，用于验证完整的开发流程。

## 需求描述
添加用户认证功能，包括：
- 用户登录
- 用户注册
- 密码重置

## 验收标准
- [ ] 用户可以注册账号
- [ ] 用户可以登录
- [ ] 用户可以重置密码
""",
        repo_path=".",
        branch="main"
    )
    print(f"✅ 案例创建成功: {case.id}")
    
    # 步骤 2: 生成计划
    print("\n[步骤 2/5] 生成实现计划...")
    planning_agent = PlanningAgent(router)
    plan_request = {
        "requirement_description": case.description,
        "related_files": [],
    }
    plan_response = await planning_agent.generate_plan(plan_request)
    print(f"✅ 计划生成成功: {len(plan_response.get('tasks', []))} 个任务")
    
    # 保存计划
    plan_markdown = plan_response.get('plan_markdown', '')
    tasks = plan_response.get('tasks', [])
    case_manager.save_plan(case.id, plan_markdown, tasks)
    print(f"✅ 计划已保存")
    
    # 步骤 3: 生成代码（选择第一个任务）
    print("\n[步骤 3/5] 生成代码补丁...")
    tasks = case_manager.get_tasks(case.id)
    if tasks:
        task = tasks[0]
        print(f"   选择任务: {task.title}")
        
        coding_agent = CodingAgent(router)
        code_request = {
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description or "",
                "related_files": task.related_files or [],
            },
        }
        code_response = await coding_agent.generate_code(code_request)
        print(f"✅ 代码补丁生成成功")
        
        # 保存补丁
        case_manager.save_patch(
            case.id,
            task.id,
            code_response["file_path"],
            code_response["diff"],
            code_response["description"]
        )
        print(f"✅ 补丁已保存: {code_response['file_path']}")
    else:
        print("⚠️  没有找到任务，跳过代码生成")
    
    # 步骤 4: 生成测试建议
    print("\n[步骤 4/5] 生成测试建议...")
    # 获取补丁列表（通过存储层）
    patches_dir = case_manager.storage.get_case_dir(case.id) / "patches"
    patches = []
    if patches_dir.exists():
        for patch_file in patches_dir.glob("*.patch"):
            patches.append({"id": patch_file.stem, "file_path": patch_file.name})
    if patches:
        patch = patches[0]
        patch_content = case_manager.storage.load_patch(case.id, patch["id"])
        
        test_agent = TestAgent(router)
        test_request = {
            "changes": [{
                "file_path": patch["file_path"],
                "diff": patch_content,
            }],
        }
        test_response = await test_agent.analyze_changes(test_request)
        print(f"✅ 测试建议生成成功: {len(test_response.get('potential_issues', []))} 个问题")
        
        # 保存测试结果
        suggestions_text = f"""# 测试建议

## 潜在问题
{chr(10).join([f"- [{issue.get('severity', 'medium')}] {issue.get('description', '')}" for issue in test_response.get('potential_issues', [])])}

## 测试用例
{chr(10).join([f"### {tc.get('name', 'N/A')}\n{tc.get('description', '')}" for tc in test_response.get('test_cases', [])])}
"""
        checklist = test_response.get("manual_checklist", [])
        case_manager.save_test_results(case.id, suggestions_text, checklist)
        print(f"✅ 测试结果已保存")
    else:
        print("⚠️  没有找到补丁，跳过测试生成")
    
    # 步骤 5: 完成案例（自动归档）
    print("\n[步骤 5/5] 完成案例并归档...")
    case_manager.update_case_status(case.id, "completed")
    print(f"✅ 案例状态已更新为 completed")
    print(f"✅ 案例已自动归档到知识库")
    
    print("\n" + "=" * 60)
    print("端到端测试完成！")
    print("=" * 60)
    print(f"\n测试案例 ID: {case.id}")
    print(f"生成任务数: {len(tasks)}")
    print(f"生成补丁数: {len(patches)}")
    print(f"\n可以查看以下内容：")
    print(f"- 案例详情: cases/{case.id}/")
    print(f"- 计划文件: cases/{case.id}/plan.md")
    print(f"- 补丁文件: cases/{case.id}/patches/")
    print(f"- 测试结果: cases/{case.id}/tests/")
    print(f"- 知识库归档: knowledge_base/cases/{case.id}/")


if __name__ == "__main__":
    try:
        asyncio.run(test_e2e_flow())
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"端到端测试失败: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
