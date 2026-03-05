"""
案例文件存储管理

管理案例相关的文件系统结构。
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid


class CaseStorage:
    """案例文件存储管理"""

    def __init__(self, base_path: str = "cases"):
        """
        初始化存储

        Args:
            base_path: 案例库根目录
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)

    def get_case_dir(self, case_id: str) -> Path:
        """获取案例目录"""
        case_dir = self.base_path / case_id
        case_dir.mkdir(exist_ok=True)
        return case_dir

    def save_plan_markdown(self, case_id: str, content: str) -> Path:
        """保存计划 Markdown"""
        case_dir = self.get_case_dir(case_id)
        plan_path = case_dir / "plan.md"
        plan_path.write_text(content, encoding="utf-8")
        return plan_path

    def load_plan_markdown(self, case_id: str) -> Optional[str]:
        """加载计划 Markdown"""
        case_dir = self.get_case_dir(case_id)
        plan_path = case_dir / "plan.md"
        if plan_path.exists():
            return plan_path.read_text(encoding="utf-8")
        return None

    def save_plan_json(self, case_id: str, tasks: List[Dict[str, Any]]) -> Path:
        """保存计划 JSON（任务列表）"""
        case_dir = self.get_case_dir(case_id)
        plan_json_path = case_dir / "plan.json"
        plan_json_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
        return plan_json_path

    def load_plan_json(self, case_id: str) -> Optional[List[Dict[str, Any]]]:
        """加载计划 JSON"""
        case_dir = self.get_case_dir(case_id)
        plan_json_path = case_dir / "plan.json"
        if plan_json_path.exists():
            return json.loads(plan_json_path.read_text(encoding="utf-8"))
        return None

    def save_patch(self, case_id: str, task_id: str, patch_content: str, description: str = "") -> Path:
        """保存代码补丁"""
        case_dir = self.get_case_dir(case_id)
        patches_dir = case_dir / "patches"
        patches_dir.mkdir(exist_ok=True)

        patch_path = patches_dir / f"{task_id}.patch"
        patch_path.write_text(patch_content, encoding="utf-8")

        # 保存补丁元数据
        metadata = {
            "task_id": task_id,
            "description": description,
            "file_path": str(patch_path)
        }
        metadata_path = patches_dir / f"{task_id}.meta.json"
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

        return patch_path

    def load_patch(self, case_id: str, task_id: str) -> Optional[str]:
        """加载代码补丁"""
        case_dir = self.get_case_dir(case_id)
        patch_path = case_dir / "patches" / f"{task_id}.patch"
        if patch_path.exists():
            return patch_path.read_text(encoding="utf-8")
        return None

    def list_patches(self, case_id: str) -> List[Dict[str, Any]]:
        """列出所有补丁"""
        case_dir = self.get_case_dir(case_id)
        patches_dir = case_dir / "patches"
        if not patches_dir.exists():
            return []

        patches = []
        for patch_file in patches_dir.glob("*.patch"):
            task_id = patch_file.stem
            metadata_path = patches_dir / f"{task_id}.meta.json"
            metadata = {}
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            patches.append({
                "task_id": task_id,
                "file_path": str(patch_file),
                "description": metadata.get("description", ""),
            })
        return patches

    def save_test_suggestions(self, case_id: str, content: str) -> Path:
        """保存测试建议"""
        case_dir = self.get_case_dir(case_id)
        tests_dir = case_dir / "tests"
        tests_dir.mkdir(exist_ok=True)

        suggestions_path = tests_dir / "suggestions.md"
        suggestions_path.write_text(content, encoding="utf-8")
        return suggestions_path

    def save_test_checklist(self, case_id: str, checklist: List[str]) -> Path:
        """保存测试验收清单"""
        case_dir = self.get_case_dir(case_id)
        tests_dir = case_dir / "tests"
        tests_dir.mkdir(exist_ok=True)

        checklist_path = tests_dir / "checklist.md"
        content = "# 验收清单\n\n" + "\n".join([f"- [ ] {item}" for item in checklist])
        checklist_path.write_text(content, encoding="utf-8")
        return checklist_path
    
    def load_test_suggestions(self, case_id: str) -> Optional[str]:
        """加载测试建议"""
        case_dir = self.get_case_dir(case_id)
        suggestions_path = case_dir / "tests" / "suggestions.md"
        if suggestions_path.exists():
            return suggestions_path.read_text(encoding="utf-8")
        return None
    
    def load_test_checklist(self, case_id: str) -> Optional[List[str]]:
        """加载测试验收清单"""
        case_dir = self.get_case_dir(case_id)
        checklist_path = case_dir / "tests" / "checklist.md"
        if checklist_path.exists():
            content = checklist_path.read_text(encoding="utf-8")
            # 解析 markdown 列表项
            lines = content.split("\n")
            checklist = []
            for line in lines:
                line = line.strip()
                if line.startswith("- [ ]") or line.startswith("- [x]") or line.startswith("* [ ]") or line.startswith("* [x]"):
                    # 提取文本部分
                    text = line.split("]", 1)[1].strip() if "]" in line else line[2:].strip()
                    if text:
                        checklist.append(text)
            return checklist if checklist else None
        return None

    def save_summary(self, case_id: str, content: str) -> Path:
        """保存案例总结"""
        case_dir = self.get_case_dir(case_id)
        summary_path = case_dir / "summary.md"
        summary_path.write_text(content, encoding="utf-8")
        return summary_path

    def load_summary(self, case_id: str) -> Optional[str]:
        """加载案例总结"""
        case_dir = self.get_case_dir(case_id)
        summary_path = case_dir / "summary.md"
        if summary_path.exists():
            return summary_path.read_text(encoding="utf-8")
        return None

    def save_agent_input(self, case_id: str, run_id: str, agent_type: str, input_data: Dict[str, Any]) -> Path:
        """保存 Agent 输入"""
        case_dir = self.get_case_dir(case_id)
        agent_runs_dir = case_dir / "agent_runs"
        agent_runs_dir.mkdir(exist_ok=True)

        input_path = agent_runs_dir / f"{run_id}_{agent_type}_input.json"
        input_path.write_text(json.dumps(input_data, ensure_ascii=False, indent=2), encoding="utf-8")
        return input_path

    def save_agent_output(self, case_id: str, run_id: str, agent_type: str, output_data: Dict[str, Any]) -> Path:
        """保存 Agent 输出"""
        case_dir = self.get_case_dir(case_id)
        agent_runs_dir = case_dir / "agent_runs"
        agent_runs_dir.mkdir(exist_ok=True)

        output_path = agent_runs_dir / f"{run_id}_{agent_type}_output.json"
        output_path.write_text(json.dumps(output_data, ensure_ascii=False, indent=2), encoding="utf-8")
        return output_path
