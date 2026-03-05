"""调试版：检查 TestAgent 的 LLM 响应"""

import sys
import io
import asyncio
from pathlib import Path
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_core.llm_router import LLMRouter
from openclaw_core.agents import TestAgent

async def main():
    case_id = "case-1fadf9d2"
    
    print("=" * 60)
    print("调试版 TestAgent - 检查 LLM 响应")
    print("=" * 60)
    
    # 初始化
    manager = CaseManager()
    router = LLMRouter()
    agent = TestAgent(router)
    
    # 使用一个简单的测试用例
    test_request = {
        "changes": [
            {
                "file_path": "openclaw_studio/api/main.py",
                "diff": """# FastAPI 主应用

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```
""",
            }
        ],
        "context": {
            "related_requirements": ["FastAPI 后端 API"],
            "runtime_constraints": ["Python 3.11+", "FastAPI"],
        },
    }
    
    print("\n🤖 调用 TestAgent...")
    
    try:
        # 直接调用 LLM 看看响应
        from openclaw_core.llm_router import LLMMessage
        
        system_prompt = """你是一个专业的测试工程师和代码审查专家。你的任务是：
1. 分析代码改动，识别潜在风险和边界情况
2. 生成针对性的测试用例（单元测试、集成测试、端到端测试）
3. 提供人工验收清单

请确保：
- 测试用例覆盖主要功能和边界情况
- 识别潜在的安全和性能问题
- 提供清晰的测试步骤和断言

请按照以下格式输出：

## 潜在问题

- [严重程度: high/medium/low] 问题描述

## 测试用例

### 测试用例名称
测试描述和步骤

## 人工验收

- 验收项 1
- 验收项 2
"""
        
        user_message = """## 代码改动

### openclaw_studio/api/main.py
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```
"""
        
        messages: list[LLMMessage] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        
        print("📤 发送请求到 LLM...")
        response = await router.complete_chat(
            messages,
            task_type="summary",
            temperature=0.5,
            max_tokens=3000,
        )
        
        content = response["content"]
        print(f"\n📥 LLM 响应 (前 500 字符):")
        print("-" * 60)
        print(content[:500])
        print("-" * 60)
        
        # 保存完整响应
        output_file = Path(f"cases/{case_id}/agent_runs/test_debug_response.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "content": content,
                "full_response": response,
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 完整响应已保存到: {output_file}")
        
        # 测试解析
        print("\n🔍 测试解析结果...")
        potential_issues = agent._extract_issues(content)
        test_cases = agent._extract_test_cases(content)
        manual_checklist = agent._extract_list_section(content, "manual", "人工验收")
        
        print(f"   潜在问题: {len(potential_issues)}")
        print(f"   测试用例: {len(test_cases)}")
        print(f"   验收清单: {len(manual_checklist)}")
        
        if potential_issues:
            print("\n⚠️  潜在问题:")
            for issue in potential_issues[:3]:
                print(f"   - [{issue.get('severity')}] {issue.get('description')[:80]}")
        
        if test_cases:
            print("\n🧪 测试用例:")
            for tc in test_cases[:3]:
                print(f"   - {tc.get('name')}")
        
        if manual_checklist:
            print("\n✅ 验收清单:")
            for item in manual_checklist[:5]:
                print(f"   - {item}")
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        manager.close()

if __name__ == "__main__":
    asyncio.run(main())
