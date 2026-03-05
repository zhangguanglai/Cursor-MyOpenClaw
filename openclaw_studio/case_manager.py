"""
案例管理器

整合数据库和文件存储，提供统一的案例管理接口。
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any

from openclaw_studio.database import CaseDatabase, Case, Plan, Task, AgentRun, TestRecord
from openclaw_studio.case_storage import CaseStorage


class CaseManager:
    """案例管理器"""

    def __init__(self, db_path: str = "openclaw_studio.db", cases_dir: str = "cases"):
        """
        初始化案例管理器

        Args:
            db_path: 数据库文件路径
            cases_dir: 案例文件存储目录
        """
        self.db = CaseDatabase(db_path)
        self.storage = CaseStorage(cases_dir)

    def create_case(
        self,
        title: str,
        description: str,
        repo_path: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> Case:
        """
        创建新案例

        Args:
            title: 案例标题
            description: 案例描述
            repo_path: 仓库路径
            branch: 分支名称

        Returns:
            创建的案例对象
        """
        case_id = f"case-{uuid.uuid4().hex[:8]}"
        case = Case(
            id=case_id,
            title=title,
            description=description,
            repo_path=repo_path,
            branch=branch,
        )
        return self.db.create_case(case)

    def get_case(self, case_id: str) -> Optional[Case]:
        """获取案例"""
        return self.db.get_case(case_id)

    def list_cases(self, status: Optional[str] = None) -> List[Case]:
        """列出案例"""
        return self.db.list_cases(status)

    def update_case_status(self, case_id: str, status: str) -> bool:
        """更新案例状态"""
        return self.db.update_case(case_id, status=status)

    def save_plan(
        self,
        case_id: str,
        plan_markdown: str,
        tasks: List[Dict[str, Any]],
    ) -> Plan:
        """
        保存实现计划

        Args:
            case_id: 案例 ID
            plan_markdown: 计划 Markdown 内容
            tasks: 任务列表（JSON 格式）

        Returns:
            计划对象
        """
        # 保存文件
        plan_md_path = self.storage.save_plan_markdown(case_id, plan_markdown)
        plan_json_path = self.storage.save_plan_json(case_id, tasks)

        # 保存到数据库
        plan_id = f"plan-{uuid.uuid4().hex[:8]}"
        plan = Plan(
            id=plan_id,
            case_id=case_id,
            plan_md_path=str(plan_md_path),
            plan_json_path=str(plan_json_path),
        )
        plan = self.db.create_plan(plan)

        # 创建任务记录
        for task_data in tasks:
            task_id = task_data.get("id", f"task-{uuid.uuid4().hex[:8]}")
            related_files = json.dumps(task_data.get("related_files", [])) if task_data.get("related_files") else None
            task = Task(
                id=task_id,
                case_id=case_id,
                plan_id=plan_id,
                title=task_data.get("title", ""),
                description=task_data.get("description", ""),
                status="pending",
                related_files=related_files,
                risk_level=task_data.get("risk_level"),
            )
            self.db.create_task(task)

        # 更新案例状态
        self.db.update_case(case_id, status="planning")

        return plan

    def get_plan(self, case_id: str) -> Optional[Dict[str, Any]]:
        """获取计划"""
        plan = self.db.get_plan(case_id)
        if not plan:
            return None

        plan_md = self.storage.load_plan_markdown(case_id)
        plan_json = self.storage.load_plan_json(case_id)

        return {
            "plan": plan,
            "markdown": plan_md,
            "tasks": plan_json,
        }

    def get_tasks(self, case_id: str, status: Optional[str] = None) -> List[Task]:
        """获取任务列表"""
        return self.db.get_tasks(case_id, status)

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.db.get_task(task_id)

    def update_task_status(self, task_id: str, status: str) -> bool:
        """更新任务状态"""
        return self.db.update_task(task_id, status=status)

    def save_patch(self, case_id: str, task_id: str, patch_content: str, description: str = "") -> Path:
        """保存代码补丁"""
        return self.storage.save_patch(case_id, task_id, patch_content, description)

    def get_patches(self, case_id: str) -> List[Dict[str, Any]]:
        """获取所有补丁"""
        return self.storage.list_patches(case_id)

    def save_test_results(
        self,
        case_id: str,
        suggestions: str,
        checklist: List[str],
    ) -> Dict[str, Path]:
        """保存测试结果"""
        suggestions_path = self.storage.save_test_suggestions(case_id, suggestions)
        checklist_path = self.storage.save_test_checklist(case_id, checklist)

        return {
            "suggestions": suggestions_path,
            "checklist": checklist_path,
        }

    def save_summary(self, case_id: str, content: str) -> Path:
        """保存案例总结"""
        return self.storage.save_summary(case_id, content)

    def record_agent_run(
        self,
        case_id: str,
        agent_type: str,
        task_id: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        status: str = "completed",
        error_message: Optional[str] = None,
    ) -> AgentRun:
        """记录 Agent 调用"""
        run_id = f"run-{uuid.uuid4().hex[:8]}"

        # 保存输入输出文件
        input_path = None
        output_path = None
        if input_data:
            input_path = self.storage.save_agent_input(case_id, run_id, agent_type, input_data)
        if output_data:
            output_path = self.storage.save_agent_output(case_id, run_id, agent_type, output_data)

        # 保存到数据库
        run = AgentRun(
            id=run_id,
            case_id=case_id,
            agent_type=agent_type,
            task_id=task_id,
            input_path=str(input_path) if input_path else None,
            output_path=str(output_path) if output_path else None,
            model=model,
            status=status,
            error_message=error_message,
        )
        return self.db.create_agent_run(run)

    def close(self):
        """关闭资源"""
        self.db.close()
