"""
测试 API

提供生成测试建议的接口。
"""

from fastapi import APIRouter, HTTPException, Depends

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.models import TestRequestIn, TestResponseOut
from openclaw_studio.api.dependencies import get_case_manager, get_test_agent
from openclaw_core.agents import TestAgent

router = APIRouter(prefix="/cases", tags=["Testing"])


@router.post("/{case_id}/test", response_model=TestResponseOut)
async def generate_test(
    case_id: str,
    request: TestRequestIn,
    case_manager: CaseManager = Depends(get_case_manager),
    agent: TestAgent = Depends(get_test_agent),
):
    """为案例生成测试建议"""
    case = case_manager.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    try:
        # 构建 TestAgentRequest
        test_request = {
            "changes": request.changes,
        }
        
        # 调用 TestAgent
        result = await agent.analyze_changes(test_request)
        
        # 保存测试结果
        suggestions_text = f"""# 测试建议

## 潜在问题
{chr(10).join([f"- [{issue.get('severity', 'medium')}] {issue.get('description', '')}" for issue in result.get('potential_issues', [])])}

## 测试用例
{chr(10).join([f"### {tc.get('name', 'N/A')}\n{tc.get('description', '')}" for tc in result.get('test_cases', [])])}
"""
        
        checklist = result.get("manual_checklist", [])
        
        case_manager.save_test_results(case_id, suggestions_text, checklist)
        
        # 更新案例状态
        case_manager.update_case_status(case_id, "testing")
        
        # 记录 Agent 调用
        case_manager.record_agent_run(
            case_id=case_id,
            agent_type="test",
            input_data=test_request,
            output_data={
                "issues_count": len(result.get("potential_issues", [])),
                "test_cases_count": len(result.get("test_cases", [])),
            },
            model=agent.llm_router.select_model("summary"),
        )
        
        return TestResponseOut(
            potential_issues=result.get("potential_issues", []),
            test_cases=result.get("test_cases", []),
            manual_checklist=checklist
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test generation failed: {str(e)}")
