"""
案例库数据库管理

使用 SQLite 存储案例元数据，文件系统存储实际内容。
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class Case:
    """需求案例"""
    id: str
    title: str
    description: str
    status: str = "created"  # created, planning, coding, testing, completed, cancelled
    repo_path: Optional[str] = None
    branch: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Plan:
    """实现计划"""
    id: str
    case_id: str
    plan_md_path: str
    plan_json_path: str
    created_at: Optional[str] = None


@dataclass
class Task:
    """子任务"""
    id: str
    case_id: str
    title: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, cancelled
    plan_id: Optional[str] = None
    related_files: Optional[str] = None  # JSON 数组
    risk_level: Optional[str] = None  # low, medium, high
    assigned_to: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class AgentRun:
    """Agent 调用记录"""
    id: str
    case_id: str
    agent_type: str  # planning, coding, test
    task_id: Optional[str] = None
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    model: Optional[str] = None
    status: str = "completed"  # running, completed, failed
    error_message: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class TestRecord:
    """测试记录"""
    id: str
    case_id: str
    summary: str
    details_path: Optional[str] = None
    status: str = "pending"  # pending, passed, failed
    created_at: Optional[str] = None


class CaseDatabase:
    """案例库数据库管理"""

    def __init__(self, db_path: str = "openclaw_studio.db"):
        """
        初始化数据库

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        """初始化数据库表"""
        cursor = self.conn.cursor()

        # Cases 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                repo_path TEXT,
                branch TEXT,
                status TEXT DEFAULT 'created',
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Plans 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                plan_md_path TEXT NOT NULL,
                plan_json_path TEXT NOT NULL,
                created_at TEXT,
                FOREIGN KEY (case_id) REFERENCES cases(id)
            )
        """)

        # Tasks 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                plan_id TEXT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                related_files TEXT,
                risk_level TEXT,
                assigned_to TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (case_id) REFERENCES cases(id),
                FOREIGN KEY (plan_id) REFERENCES plans(id)
            )
        """)

        # Agent Runs 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_runs (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                agent_type TEXT NOT NULL,
                task_id TEXT,
                input_path TEXT,
                output_path TEXT,
                model TEXT,
                status TEXT DEFAULT 'completed',
                error_message TEXT,
                created_at TEXT,
                FOREIGN KEY (case_id) REFERENCES cases(id),
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        """)

        # Test Records 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_records (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                summary TEXT,
                details_path TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                FOREIGN KEY (case_id) REFERENCES cases(id)
            )
        """)

        self.conn.commit()

    def create_case(self, case: Case) -> Case:
        """创建案例"""
        now = datetime.now().isoformat()
        case.created_at = now
        case.updated_at = now

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO cases (id, title, description, repo_path, branch, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            case.id, case.title, case.description, case.repo_path, case.branch,
            case.status, case.created_at, case.updated_at
        ))
        self.conn.commit()
        return case

    def get_case(self, case_id: str) -> Optional[Case]:
        """获取案例"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
        row = cursor.fetchone()
        if row:
            return Case(**dict(row))
        return None

    def list_cases(self, status: Optional[str] = None) -> List[Case]:
        """列出案例"""
        cursor = self.conn.cursor()
        if status:
            cursor.execute("SELECT * FROM cases WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM cases ORDER BY created_at DESC")
        return [Case(**dict(row)) for row in cursor.fetchall()]

    def update_case(self, case_id: str, **kwargs) -> bool:
        """更新案例"""
        kwargs['updated_at'] = datetime.now().isoformat()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [case_id]

        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE cases SET {set_clause} WHERE id = ?", values)
        self.conn.commit()
        return cursor.rowcount > 0

    def create_plan(self, plan: Plan) -> Plan:
        """创建计划"""
        now = datetime.now().isoformat()
        plan.created_at = now

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO plans (id, case_id, plan_md_path, plan_json_path, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (plan.id, plan.case_id, plan.plan_md_path, plan.plan_json_path, plan.created_at))
        self.conn.commit()
        return plan

    def get_plan(self, case_id: str) -> Optional[Plan]:
        """获取案例的计划"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM plans WHERE case_id = ?", (case_id,))
        row = cursor.fetchone()
        if row:
            return Plan(**dict(row))
        return None

    def create_task(self, task: Task) -> Task:
        """创建任务"""
        now = datetime.now().isoformat()
        task.created_at = now
        task.updated_at = now

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (id, case_id, plan_id, title, description, status, related_files, risk_level, assigned_to, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task.id, task.case_id, task.plan_id, task.title, task.description,
            task.status, task.related_files, task.risk_level, task.assigned_to,
            task.created_at, task.updated_at
        ))
        self.conn.commit()
        return task

    def get_tasks(self, case_id: str, status: Optional[str] = None) -> List[Task]:
        """获取案例的任务列表"""
        cursor = self.conn.cursor()
        if status:
            cursor.execute(
                "SELECT * FROM tasks WHERE case_id = ? AND status = ? ORDER BY created_at",
                (case_id, status)
            )
        else:
            cursor.execute("SELECT * FROM tasks WHERE case_id = ? ORDER BY created_at", (case_id,))
        return [Task(**dict(row)) for row in cursor.fetchall()]

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if row:
            return Task(**dict(row))
        return None

    def update_task(self, task_id: str, **kwargs) -> bool:
        """更新任务"""
        kwargs['updated_at'] = datetime.now().isoformat()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [task_id]

        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
        self.conn.commit()
        return cursor.rowcount > 0

    def create_agent_run(self, run: AgentRun) -> AgentRun:
        """创建 Agent 调用记录"""
        now = datetime.now().isoformat()
        run.created_at = now

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO agent_runs (id, case_id, agent_type, task_id, input_path, output_path, model, status, error_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run.id, run.case_id, run.agent_type, run.task_id, run.input_path,
            run.output_path, run.model, run.status, run.error_message, run.created_at
        ))
        self.conn.commit()
        return run

    def get_agent_runs(self, case_id: str, agent_type: Optional[str] = None) -> List[AgentRun]:
        """获取 Agent 调用记录"""
        cursor = self.conn.cursor()
        if agent_type:
            cursor.execute(
                "SELECT * FROM agent_runs WHERE case_id = ? AND agent_type = ? ORDER BY created_at DESC",
                (case_id, agent_type)
            )
        else:
            cursor.execute("SELECT * FROM agent_runs WHERE case_id = ? ORDER BY created_at DESC", (case_id,))
        return [AgentRun(**dict(row)) for row in cursor.fetchall()]

    def create_test_record(self, record: TestRecord) -> TestRecord:
        """创建测试记录"""
        now = datetime.now().isoformat()
        record.created_at = now

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO test_records (id, case_id, summary, details_path, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (record.id, record.case_id, record.summary, record.details_path, record.status, record.created_at))
        self.conn.commit()
        return record

    def get_test_records(self, case_id: str) -> List[TestRecord]:
        """获取测试记录"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM test_records WHERE case_id = ? ORDER BY created_at DESC", (case_id,))
        return [TestRecord(**dict(row)) for row in cursor.fetchall()]

    def close(self):
        """关闭数据库连接"""
        self.conn.close()
