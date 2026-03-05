"""
核心 Agent 实现

包含 PlanningAgent、CodingAgent、TestAgent 的实现。
"""

import json
import logging
from typing import Dict, List, Any, Optional, TypedDict
from pathlib import Path

from openclaw_core.llm_router import LLMRouter, LLMMessage
from openclaw_core.tools import CodeReader, CodeSearcher, ProjectStructure

logger = logging.getLogger(__name__)


class PlanningRequest(TypedDict, total=False):
    """PlanningAgent 输入格式"""
    requirement_description: str
    codebase_overview: Optional[str]
    related_files: Optional[List[str]]
    constraints: Optional[List[str]]
    acceptance_criteria: Optional[List[str]]


class Task(TypedDict, total=False):
    """子任务定义"""
    id: str
    title: str
    description: str
    estimated_steps: List[str]
    related_files: List[str]
    risk_level: str  # "low" | "medium" | "high"


class PlanningResponse(TypedDict):
    """PlanningAgent 输出格式"""
    plan_markdown: str
    tasks: List[Task]


class PlanningAgent:
    """规划 Agent：从需求生成实现计划"""

    def __init__(self, llm_router: LLMRouter, root_dir: Optional[str] = None):
        """
        初始化 PlanningAgent

        Args:
            llm_router: LLMRouter 实例
            root_dir: 项目根目录，用于代码搜索
        """
        self.llm_router = llm_router
        self.code_reader = CodeReader()
        self.code_searcher = CodeSearcher(root_dir)
        self.project_structure = ProjectStructure(root_dir)

    async def generate_plan(self, request: PlanningRequest) -> PlanningResponse:
        """
        生成实现计划

        Args:
            request: 规划请求

        Returns:
            规划响应（包含 Markdown 计划和子任务列表）
        """
        # 收集上下文
        context_parts = []

        # 1. 项目结构概览
        structure = self.project_structure.get_structure()
        context_parts.append(f"## 项目结构\n```\n{structure}\n```\n")

        # 2. 相关文件内容（如果提供）
        if request.get("related_files"):
            context_parts.append("## 相关文件内容\n")
            files_content = self.code_reader.read_files(request["related_files"])
            for file_path, content in files_content.items():
                context_parts.append(f"### {file_path}\n```python\n{content[:2000]}\n```\n")  # 限制长度

        # 3. 构建系统提示词
        system_prompt = """你是一个经验丰富的软件架构师和开发规划专家。你的任务是：
1. 分析用户需求，识别关键功能点和约束条件
2. 将需求拆解为可执行的子任务
3. 评估每个子任务的风险和复杂度
4. 生成清晰的实现计划（Markdown 格式）

请确保：
- 计划具体、可执行
- 子任务粒度适中（每个任务 1-3 小时工作量）
- 明确标注风险等级和依赖关系
- 提供测试建议和验收标准"""

        # 4. 构建用户消息
        user_parts = [f"## 需求描述\n{request['requirement_description']}\n"]

        if request.get("constraints"):
            user_parts.append(f"## 约束条件\n" + "\n".join(f"- {c}" for c in request["constraints"]) + "\n")

        if request.get("acceptance_criteria"):
            user_parts.append(f"## 验收标准\n" + "\n".join(f"- {c}" for c in request["acceptance_criteria"]) + "\n")

        if context_parts:
            user_parts.append("\n".join(context_parts))

        user_message = "\n".join(user_parts)

        # 5. 调用 LLM
        messages: List[LLMMessage] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        response = await self.llm_router.complete_chat(
            messages,
            task_type="planning",
            temperature=0.7,
            max_tokens=4000,
        )

        # 6. 解析响应（尝试提取结构化数据）
        content = response["content"]
        plan_markdown = content

        # 尝试从响应中提取 JSON 格式的任务列表
        tasks = self._extract_tasks_from_response(content)

        return PlanningResponse(
            plan_markdown=plan_markdown,
            tasks=tasks,
        )

    @staticmethod
    def _extract_tasks_from_response(content: str) -> List[Task]:
        """
        从 LLM 响应中提取结构化任务列表

        Args:
            content: LLM 响应内容

        Returns:
            任务列表
        """
        # 尝试查找 JSON 代码块
        import re
        json_match = re.search(r"```json\s*(\[.*?\])\s*```", content, re.DOTALL)
        if json_match:
            try:
                tasks_data = json.loads(json_match.group(1))
                return [Task(**task) if isinstance(task, dict) else task for task in tasks_data]
            except json.JSONDecodeError:
                pass

        # 如果无法解析 JSON，返回空列表（由用户手动补充）
        return []


class CodingRequest(TypedDict, total=False):
    """CodingAgent 输入格式"""
    task: Dict[str, Any]
    current_files_content: Optional[Dict[str, str]]
    coding_guidelines: Optional[str]
    language: Optional[str]
    apply_constraints: Optional[List[str]]


class Patch(TypedDict):
    """代码补丁"""
    file_path: str
    description: str
    diff: str


class CodingResponse(TypedDict):
    """CodingAgent 输出格式"""
    patches: List[Patch]
    rationale: str
    followup_suggestions: List[str]
    risks: List[str]
    test_suggestions: List[str]


class CodingAgent:
    """编码 Agent：根据任务生成代码修改建议"""

    def __init__(self, llm_router: LLMRouter, root_dir: Optional[str] = None):
        """
        初始化 CodingAgent

        Args:
            llm_router: LLMRouter 实例
            root_dir: 项目根目录
        """
        self.llm_router = llm_router
        self.code_reader = CodeReader()
        self.code_searcher = CodeSearcher(root_dir)

    async def generate_code(self, request: CodingRequest) -> CodingResponse:
        """
        生成代码修改建议

        Args:
            request: 编码请求

        Returns:
            编码响应（包含补丁、解释、建议等）
        """
        task = request["task"]
        related_files = task.get("related_files", [])

        # 读取相关文件内容
        files_content = {}
        if related_files:
            files_content = self.code_reader.read_files(related_files)
        elif request.get("current_files_content"):
            files_content = request["current_files_content"]

        # 构建系统提示词
        system_prompt = """你是一个专业的代码生成助手。你的任务是：
1. 分析任务需求和相关代码上下文
2. 生成精确的代码修改建议（以 unified diff 格式）
3. 提供清晰的修改理由和风险分析
4. 给出测试建议和后续改进方向

请确保：
- 补丁格式清晰，易于应用
- 保持代码风格一致
- 考虑边界情况和错误处理
- 提供必要的注释"""

        # 构建用户消息
        user_parts = [
            f"## 任务描述\n{task.get('title', '')}\n{task.get('description', '')}\n",
        ]

        if task.get("estimated_steps"):
            user_parts.append("## 建议步骤\n" + "\n".join(f"- {step}" for step in task["estimated_steps"]) + "\n")

        if files_content:
            user_parts.append("## 相关文件内容\n")
            for file_path, content in files_content.items():
                user_parts.append(f"### {file_path}\n```python\n{content}\n```\n")

        if request.get("coding_guidelines"):
            user_parts.append(f"## 代码规范\n{request['coding_guidelines']}\n")

        if request.get("apply_constraints"):
            user_parts.append("## 约束条件\n" + "\n".join(f"- {c}" for c in request["apply_constraints"]) + "\n")

        user_message = "\n".join(user_parts)

        # 调用 LLM
        messages: List[LLMMessage] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        response = await self.llm_router.complete_chat(
            messages,
            task_type="coding",
            temperature=0.3,  # 代码生成使用较低温度
            max_tokens=4000,
        )

        # 解析响应
        content = response["content"]
        patches = self._extract_patches_from_response(content, related_files)
        rationale = self._extract_section(content, "rationale", "理由")
        followup_suggestions = self._extract_list_section(content, "followup", "后续建议")
        risks = self._extract_list_section(content, "risk", "风险")
        test_suggestions = self._extract_list_section(content, "test", "测试建议")

        return CodingResponse(
            patches=patches,
            rationale=rationale or "无特殊说明",
            followup_suggestions=followup_suggestions,
            risks=risks,
            test_suggestions=test_suggestions,
        )

    @staticmethod
    def _extract_patches_from_response(content: str, related_files: List[str]) -> List[Patch]:
        """从响应中提取补丁"""
        patches = []
        import re

        # 查找 diff 代码块
        diff_pattern = r"```(?:diff|patch)?\s*\n(.*?)\n```"
        matches = re.finditer(diff_pattern, content, re.DOTALL)

        for i, match in enumerate(matches):
            diff_content = match.group(1)
            # 尝试从 diff 中提取文件路径
            file_path = related_files[i] if i < len(related_files) else f"file_{i+1}.py"
            file_match = re.search(r"^\+\+\+ (.*?)$", diff_content, re.MULTILINE)
            if file_match:
                file_path = file_match.group(1).strip()

            patches.append(Patch(
                file_path=file_path,
                description=f"代码修改 {i+1}",
                diff=diff_content,
            ))

        # 如果没有找到 diff，尝试从整个响应中提取
        if not patches and related_files:
            patches.append(Patch(
                file_path=related_files[0],
                description="代码修改建议",
                diff=content,
            ))

        return patches

    @staticmethod
    def _extract_section(content: str, keyword: str, label: str) -> str:
        """提取特定章节内容"""
        import re
        pattern = rf"##\s*{label}.*?\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _extract_list_section(content: str, keyword: str, label: str) -> List[str]:
        """提取列表章节"""
        import re
        pattern = rf"##\s*{label}.*?\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if not match:
            return []

        text = match.group(1)
        # 提取列表项
        items = re.findall(r"^[-*]\s*(.+)$", text, re.MULTILINE)
        return [item.strip() for item in items]


class TestAgentRequest(TypedDict, total=False):
    """TestAgent 输入格式"""
    changes: List[Dict[str, Any]]
    context: Optional[Dict[str, Any]]


class PotentialIssue(TypedDict):
    """潜在问题"""
    description: str
    severity: str  # "low" | "medium" | "high"
    related_files: List[str]


class TestCase(TypedDict, total=False):
    """测试用例"""
    name: str
    type: str  # "unit" | "integration" | "e2e"
    steps: List[str]
    target_file: str


class TestResponse(TypedDict):
    """TestAgent 输出格式"""
    potential_issues: List[PotentialIssue]
    test_cases: List[TestCase]
    manual_checklist: List[str]


class TestAgent:
    """测试 Agent：分析代码改动并生成测试建议"""

    def __init__(self, llm_router: LLMRouter):
        """
        初始化 TestAgent

        Args:
            llm_router: LLMRouter 实例
        """
        self.llm_router = llm_router

    async def analyze_changes(self, request: TestAgentRequest) -> TestResponse:
        """
        分析代码改动并生成测试建议

        Args:
            request: 测试请求

        Returns:
            测试响应（包含问题、测试用例、验收清单）
        """
        changes = request["changes"]
        context = request.get("context", {})

        # 构建系统提示词
        system_prompt = """你是一个专业的测试工程师和代码审查专家。你的任务是：
1. 分析代码改动，识别潜在风险和边界情况
2. 生成针对性的测试用例（单元测试、集成测试、端到端测试）
3. 提供人工验收清单

请确保：
- 测试用例覆盖主要功能和边界情况
- 识别潜在的安全和性能问题
- 提供清晰的测试步骤和断言"""

        # 构建用户消息
        user_parts = ["## 代码改动\n"]

        for change in changes:
            file_path = change.get("file_path", "unknown")
            diff = change.get("diff", change.get("new_content", ""))
            user_parts.append(f"### {file_path}\n```diff\n{diff[:2000]}\n```\n")

        if context.get("related_requirements"):
            user_parts.append("## 相关需求\n" + "\n".join(f"- {r}" for r in context["related_requirements"]) + "\n")

        if context.get("runtime_constraints"):
            user_parts.append("## 运行时约束\n" + "\n".join(f"- {c}" for c in context["runtime_constraints"]) + "\n")

        user_message = "\n".join(user_parts)

        # 调用 LLM
        messages: List[LLMMessage] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        response = await self.llm_router.complete_chat(
            messages,
            task_type="summary",  # 测试分析使用 summary 类型
            temperature=0.5,
            max_tokens=3000,
        )

        # 解析响应
        content = response["content"]
        potential_issues = self._extract_issues(content)
        test_cases = self._extract_test_cases(content)
        manual_checklist = self._extract_list_section(content, "manual", "人工验收")

        return TestResponse(
            potential_issues=potential_issues,
            test_cases=test_cases,
            manual_checklist=manual_checklist,
        )

    @staticmethod
    def _extract_issues(content: str) -> List[PotentialIssue]:
        """提取潜在问题"""
        import re
        issues = []
        # 查找问题列表
        pattern = r"##\s*潜在问题.*?\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1)
            # 提取每个问题
            items = re.findall(r"^[-*]\s*(.+?)(?:严重程度[：:]\s*(\w+))?", text, re.MULTILINE | re.IGNORECASE)
            for item in items:
                desc = item[0].strip()
                severity = item[1].strip().lower() if item[1] else "medium"
                if severity not in ["low", "medium", "high"]:
                    severity = "medium"
                issues.append(PotentialIssue(
                    description=desc,
                    severity=severity,
                    related_files=[],
                ))
        return issues

    @staticmethod
    def _extract_test_cases(content: str) -> List[TestCase]:
        """提取测试用例"""
        import re
        test_cases = []
        # 查找测试用例章节
        pattern = r"##\s*测试用例.*?\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            text = match.group(1)
            # 提取每个测试用例
            case_pattern = r"(?:###|##)\s*(.+?)\n(.*?)(?=(?:###|##)|\Z)"
            cases = re.finditer(case_pattern, text, re.DOTALL)
            for case_match in cases:
                name = case_match.group(1).strip()
                details = case_match.group(2)
                # 提取步骤
                steps = re.findall(r"^[-*]\s*(.+)$", details, re.MULTILINE)
                test_cases.append(TestCase(
                    name=name,
                    type="unit",  # 默认类型
                    steps=[s.strip() for s in steps],
                    target_file="tests/test_module.py",
                ))
        return test_cases

    @staticmethod
    def _extract_list_section(content: str, keyword: str, label: str) -> List[str]:
        """提取列表章节"""
        import re
        pattern = rf"##\s*{label}.*?\n(.*?)(?=\n##|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if not match:
            return []

        text = match.group(1)
        items = re.findall(r"^[-*]\s*(.+)$", text, re.MULTILINE)
        return [item.strip() for item in items]
