"""从计划中提取任务并保存到数据库"""

import sys
import io
import json
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.database import Task

def extract_tasks_from_plan(plan_md: str) -> list:
    """从计划 Markdown 中提取任务"""
    tasks = []
    
    # 查找所有任务相关的章节
    # 模式1: ## 任务 X 或 ### 任务 X
    # 模式2: - [ ] 任务描述
    # 模式3: 数字编号的任务列表
    
    # 尝试提取编号任务
    task_patterns = [
        r'(?:^|\n)(?:#{1,3}\s+)?(?:任务|Task|步骤|Step)\s*(\d+)[：:]\s*(.+?)(?=\n(?:任务|Task|步骤|Step|\Z))',
        r'(?:^|\n)(?:#{1,3}\s+)?(\d+)\.\s+(.+?)(?=\n\d+\.|\n##|\Z)',
        r'(?:^|\n)-\s+\[?\s*(?:任务|Task)\s*(\d+)?\]?\s*[：:]\s*(.+?)(?=\n-|\n##|\Z)',
    ]
    
    for pattern in task_patterns:
        matches = re.finditer(pattern, plan_md, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        for match in matches:
            if len(match.groups()) >= 2:
                task_num = match.group(1) if match.group(1) else str(len(tasks) + 1)
                title = match.group(2).strip()
                
                # 清理标题
                title = re.sub(r'\*\*', '', title)
                title = re.sub(r'`.*?`', '', title)
                title = title.split('\n')[0].strip()
                
                if title and len(title) > 5:  # 过滤太短的标题
                    tasks.append({
                        "id": f"task-{task_num.zfill(3)}",
                        "title": title[:100],  # 限制长度
                        "description": match.group(0)[:500],  # 包含上下文
                        "related_files": [],
                        "risk_level": "medium"
                    })
    
    # 如果没找到，尝试按章节提取
    if not tasks:
        # 查找所有二级和三级标题作为任务
        section_pattern = r'(?:^|\n)(#{2,3})\s+(.+?)(?=\n#{1,3}|\Z)'
        matches = re.finditer(section_pattern, plan_md, re.MULTILINE)
        for i, match in enumerate(matches, 1):
            level = len(match.group(1))
            title = match.group(2).strip()
            
            # 跳过一些通用章节
            skip_keywords = ['整体', '架构', '技术', '目录', '总结', '参考', '注意事项']
            if any(kw in title for kw in skip_keywords):
                continue
            
            if level >= 2 and title and len(title) > 5:
                tasks.append({
                    "id": f"task-{i:03d}",
                    "title": title[:100],
                    "description": match.group(0)[:500],
                    "related_files": [],
                    "risk_level": "medium"
                })
    
    return tasks[:20]  # 限制最多20个任务

def main():
    case_id = "case-8b994138"
    
    print("=" * 60)
    print("提取前端开发任务")
    print("=" * 60)
    print(f"\n案例 ID: {case_id}")
    
    manager = CaseManager()
    
    # 获取计划
    plan_data = manager.get_plan(case_id)
    if not plan_data:
        print("❌ 计划不存在")
        return
    
    plan_md = plan_data.get("markdown", "")
    if not plan_md:
        print("❌ 计划内容为空")
        return
    
    print(f"✅ 计划长度: {len(plan_md)} 字符")
    
    # 提取任务
    tasks = extract_tasks_from_plan(plan_md)
    
    print(f"\n📋 提取到 {len(tasks)} 个任务")
    
    if not tasks:
        print("⚠️  未能自动提取任务，将创建默认任务列表")
        # 创建默认任务列表
        tasks = [
            {"id": "task-001", "title": "搭建 React + TypeScript 项目结构", "description": "使用 Vite 创建项目，配置 TypeScript、ESLint、Prettier", "related_files": [], "risk_level": "low"},
            {"id": "task-002", "title": "安装和配置核心依赖", "description": "安装 Ant Design、TanStack Query、Zustand、react-markdown 等", "related_files": [], "risk_level": "low"},
            {"id": "task-003", "title": "实现 API 客户端封装", "description": "创建 axios 实例和 TanStack Query hooks", "related_files": [], "risk_level": "medium"},
            {"id": "task-004", "title": "实现需求中心视图", "description": "案例列表、创建/编辑案例表单", "related_files": [], "risk_level": "medium"},
            {"id": "task-005", "title": "实现规划视图", "description": "计划展示、任务列表、Markdown 编辑器", "related_files": [], "risk_level": "medium"},
            {"id": "task-006", "title": "实现执行视图", "description": "任务列表、补丁展示、Diff 预览", "related_files": [], "risk_level": "medium"},
            {"id": "task-007", "title": "实现测试视图", "description": "测试建议、验收清单", "related_files": [], "risk_level": "medium"},
            {"id": "task-008", "title": "实现历史视图", "description": "时间线展示、Agent 调用记录", "related_files": [], "risk_level": "low"},
            {"id": "task-009", "title": "实现路由和导航", "description": "React Router 配置、导航菜单", "related_files": [], "risk_level": "low"},
            {"id": "task-010", "title": "实现响应式设计", "description": "适配不同屏幕尺寸", "related_files": [], "risk_level": "medium"},
            {"id": "task-011", "title": "前后端联调和测试", "description": "验证所有 API 端点，测试完整流程", "related_files": [], "risk_level": "high"},
        ]
    
    # 显示任务列表
    print("\n📋 任务列表:")
    for task in tasks:
        print(f"   {task['id']}: {task['title']}")
    
    # 更新计划 JSON
    plan_json_path = Path(f"cases/{case_id}/plan.json")
    plan_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(plan_json_path, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 计划 JSON 已更新: {plan_json_path}")
    
    # 保存任务到数据库
    plan = plan_data.get("plan")
    if plan:
        plan_id = plan.id
        
        for task_data in tasks:
            task_id = task_data["id"]
            related_files = json.dumps(task_data.get("related_files", [])) if task_data.get("related_files") else None
            
            # 检查任务是否已存在
            existing_task = manager.get_task(task_id)
            if existing_task:
                print(f"   ⏭️  任务 {task_id} 已存在，跳过")
                continue
            
            task = Task(
                id=task_id,
                case_id=case_id,
                plan_id=plan_id,
                title=task_data["title"],
                description=task_data.get("description", ""),
                status="pending",
                related_files=related_files,
                risk_level=task_data.get("risk_level", "medium"),
            )
            
            try:
                manager.db.create_task(task)
                print(f"   ✅ 任务 {task_id} 已创建")
            except Exception as e:
                print(f"   ⚠️  任务 {task_id} 创建失败: {e}")
    
    manager.close()
    
    print(f"\n✅ 任务提取完成")
    print(f"   总任务数: {len(tasks)}")
    print(f"\n下一步: 开始为任务生成代码")

if __name__ == "__main__":
    main()
