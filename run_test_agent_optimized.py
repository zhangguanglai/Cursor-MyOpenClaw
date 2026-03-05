"""优化版：使用实际代码文件执行 TestAgent 生成测试建议"""

import sys
import io
import asyncio
from pathlib import Path
import difflib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_core.llm_router import LLMRouter
from openclaw_core.agents import TestAgent

async def main():
    case_id = "case-1fadf9d2"
    
    print("=" * 60)
    print("优化版 TestAgent 执行")
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
    
    # 定义要分析的实际代码文件（已应用的代码）
    code_files = [
        "openclaw_studio/api/main.py",
        "openclaw_studio/api/v1/cases.py",
        "openclaw_studio/api/v1/planning.py",
        "openclaw_studio/api/v1/coding.py",
        "openclaw_studio/api/v1/testing.py",
        "openclaw_studio/api/v1/history.py",
        "openclaw_studio/api/dependencies.py",
        "openclaw_studio/models.py",
        "tests/test_api.py",
    ]
    
    print(f"\n📁 分析 {len(code_files)} 个代码文件...")
    
    # 读取实际代码文件内容
    changes = []
    for file_path in code_files:
        full_path = Path(file_path)
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 只取前 3000 字符（避免过长）
                content_preview = content[:3000]
                if len(content) > 3000:
                    content_preview += f"\n\n... (文件总长度: {len(content)} 字符，已截断)"
                
                changes.append({
                    "file_path": file_path,
                    "diff": f"# {file_path}\n\n```python\n{content_preview}\n```",
                    "new_content": content_preview,
                })
                print(f"  ✅ {file_path} ({len(content)} 字符)")
            except Exception as e:
                print(f"  ⚠️  {file_path}: 读取失败 - {e}")
        else:
            print(f"  ⚠️  {file_path}: 文件不存在")
    
    if not changes:
        print("⚠️  没有找到有效的代码文件")
        return
    
    # 构建 TestAgentRequest（优化格式）
    test_request = {
        "changes": changes,
        "context": {
            "related_requirements": [
                "使用 FastAPI 实现 OpenClaw Studio 后端 API",
                "提供 RESTful 接口供前端调用",
                "集成 OpenClaw Core 的 Agent 调用",
                "支持异步任务处理",
                "提供完整的错误处理和日志记录",
            ],
            "runtime_constraints": [
                "Python 3.11+",
                "FastAPI 框架",
                "异步处理",
                "SQLite 数据库",
                "Pydantic 数据验证",
            ],
        },
    }
    
    print(f"\n🤖 调用 TestAgent...")
    print(f"   变更文件数: {len(changes)}")
    print(f"   总代码量: {sum(len(c.get('new_content', '')) for c in changes)} 字符")
    
    try:
        # 调用 TestAgent
        result = await agent.analyze_changes(test_request)
        
        print(f"\n✅ TestAgent 执行成功")
        print(f"   潜在问题: {len(result.get('potential_issues', []))}")
        print(f"   测试用例: {len(result.get('test_cases', []))}")
        print(f"   验收清单: {len(result.get('manual_checklist', []))}")
        
        # 显示详细结果
        if result.get('potential_issues'):
            print(f"\n⚠️  潜在问题:")
            for i, issue in enumerate(result.get('potential_issues', [])[:5], 1):
                severity = issue.get('severity', 'medium')
                desc = issue.get('description', '')[:100]
                print(f"   {i}. [{severity.upper()}] {desc}")
        
        if result.get('test_cases'):
            print(f"\n🧪 测试用例:")
            for i, tc in enumerate(result.get('test_cases', [])[:5], 1):
                name = tc.get('name', 'N/A')
                print(f"   {i}. {name}")
        
        if result.get('manual_checklist'):
            print(f"\n✅ 验收清单:")
            for i, item in enumerate(result.get('manual_checklist', [])[:10], 1):
                print(f"   {i}. {item}")
        
        # 保存测试结果
        suggestions_text = f"""# 测试建议

## 潜在问题
{chr(10).join([f"- [{issue.get('severity', 'medium')}] {issue.get('description', '')}" for issue in result.get('potential_issues', [])])}

## 测试用例
{chr(10).join([f"### {tc.get('name', 'N/A')}\n{tc.get('description', '')}\n" for tc in result.get('test_cases', [])])}

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
            input_data={
                "files_count": len(changes),
                "files": [c["file_path"] for c in changes],
            },
            output_data={
                "issues_count": len(result.get("potential_issues", [])),
                "test_cases_count": len(result.get("test_cases", [])),
                "checklist_count": len(checklist),
            },
            model=router.select_model("summary"),
        )
        
        print(f"\n📝 测试结果已保存")
        print(f"   文件: cases/{case_id}/test_results.md")
        print(f"   Agent 调用记录: run-xxx_test")
        
    except Exception as e:
        print(f"\n❌ TestAgent 执行失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        manager.close()

if __name__ == "__main__":
    asyncio.run(main())
