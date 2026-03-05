"""执行 TestAgent 为 Web API 模块生成测试建议"""

import sys
import io
import asyncio
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_core.llm_router import LLMRouter
from openclaw_core.agents import TestAgent

async def main():
    case_id = "case-1fadf9d2"
    
    print("=" * 60)
    print("执行 TestAgent 生成测试建议")
    print("=" * 60)
    print(f"\n案例 ID: {case_id}")
    
    # 初始化
    manager = CaseManager()
    router = LLMRouter()
    agent = TestAgent(router)
    
    # 获取案例
    case = manager.get_case(case_id)
    if not case:
        print(f"❌ 案例不存在: {case_id}")
        return
    
    print(f"✅ 案例: {case.title}")
    
    # 获取所有补丁
    patches = manager.get_patches(case_id)
    print(f"\n📦 找到 {len(patches)} 个补丁")
    
    if not patches:
        print("⚠️  没有找到代码补丁，无法生成测试建议")
        return
    
    # 构建测试请求
    changes = []
    for patch_info in patches:
        patch_content = manager.storage.load_patch(case_id, patch_info["task_id"])
        if patch_content:
            file_path = patch_info.get("file_path", "unknown")
            changes.append({
                "file_path": file_path,
                "diff": patch_content[:5000],  # 限制长度
            })
            print(f"  ✅ {file_path}")
    
    if not changes:
        print("⚠️  没有有效的补丁内容")
        return
    
    # 构建 TestAgentRequest
    test_request = {
        "changes": changes,
        "context": {
            "related_requirements": [
                "使用 FastAPI 实现 OpenClaw Studio 后端 API",
                "提供 RESTful 接口供前端调用",
                "集成 OpenClaw Core 的 Agent 调用",
            ],
            "runtime_constraints": [
                "Python 3.11+",
                "FastAPI 框架",
                "异步处理",
            ],
        },
    }
    
    print(f"\n🤖 调用 TestAgent...")
    print(f"   变更文件数: {len(changes)}")
    
    try:
        # 调用 TestAgent
        result = await agent.analyze_changes(test_request)
        
        print(f"\n✅ TestAgent 执行成功")
        print(f"   潜在问题: {len(result.get('potential_issues', []))}")
        print(f"   测试用例: {len(result.get('test_cases', []))}")
        print(f"   验收清单: {len(result.get('manual_checklist', []))}")
        
        # 保存测试结果
        suggestions_text = f"""# 测试建议

## 潜在问题
{chr(10).join([f"- [{issue.get('severity', 'medium')}] {issue.get('description', '')}" for issue in result.get('potential_issues', [])])}

## 测试用例
{chr(10).join([f"### {tc.get('name', 'N/A')}\n{tc.get('description', '')}" for tc in result.get('test_cases', [])])}

## 验收清单
{chr(10).join([f"- {item}" for item in result.get('manual_checklist', [])])}
"""
        
        checklist = result.get("manual_checklist", [])
        
        manager.save_test_results(case_id, suggestions_text, checklist)
        
        # 更新案例状态
        manager.update_case_status(case_id, "testing")
        
        # 记录 Agent 调用
        manager.record_agent_run(
            case_id=case_id,
            agent_type="test",
            input_data=test_request,
            output_data={
                "issues_count": len(result.get("potential_issues", [])),
                "test_cases_count": len(result.get("test_cases", [])),
            },
            model=router.select_model("summary"),
        )
        
        print(f"\n📝 测试结果已保存")
        print(f"   文件: cases/{case_id}/test_results.md")
        
        # 显示部分结果
        if result.get('potential_issues'):
            print(f"\n⚠️  潜在问题（前3个）:")
            for issue in result.get('potential_issues', [])[:3]:
                print(f"   - [{issue.get('severity', 'medium')}] {issue.get('description', '')[:80]}")
        
        if result.get('test_cases'):
            print(f"\n🧪 测试用例（前3个）:")
            for tc in result.get('test_cases', [])[:3]:
                print(f"   - {tc.get('name', 'N/A')}")
        
        if checklist:
            print(f"\n✅ 验收清单（前5个）:")
            for item in checklist[:5]:
                print(f"   - {item}")
        
    except Exception as e:
        print(f"\n❌ TestAgent 执行失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        manager.close()

if __name__ == "__main__":
    asyncio.run(main())
