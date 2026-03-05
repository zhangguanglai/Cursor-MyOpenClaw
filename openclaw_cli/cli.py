"""
OpenClaw CLI 主入口

使用 click 构建命令行接口。
"""

import click
import asyncio
from pathlib import Path
from typing import Optional

from openclaw_studio.case_manager import CaseManager
from openclaw_core.llm_router import LLMRouter
from openclaw_core.agents import PlanningAgent, CodingAgent, TestAgent, PlanningRequest, CodingRequest, TestAgentRequest
from openclaw_core.logger import get_logger

# 初始化日志
logger = get_logger("openclaw.cli")

# 配置日志文件输出
_logs_dir = Path.home() / ".openclaw" / "logs"
_logs_dir.mkdir(parents=True, exist_ok=True)
logger.add_file_handler(_logs_dir / "cli.log")

# 全局管理器实例
case_manager: Optional[CaseManager] = None
llm_router: Optional[LLMRouter] = None


def get_case_manager() -> CaseManager:
    """获取案例管理器实例"""
    global case_manager
    if case_manager is None:
        case_manager = CaseManager()
    return case_manager


def get_llm_router() -> LLMRouter:
    """获取 LLM Router 实例"""
    global llm_router
    if llm_router is None:
        llm_router = LLMRouter()
    return llm_router


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """OpenClaw - AI 原生研发平台 CLI"""
    pass


@cli.command()
@click.argument('title')
@click.option('--description', '-d', help='需求描述')
@click.option('--repo', '-r', help='Git 仓库路径')
@click.option('--branch', '-b', help='Git 分支名称')
def create_case(title: str, description: Optional[str], repo: Optional[str], branch: Optional[str]):
    """创建新需求案例"""
    logger.info(f"创建案例: {title}")
    
    if not description:
        description = click.prompt('请输入需求描述', type=str)

    manager = get_case_manager()
    case = manager.create_case(
        title=title,
        description=description,
        repo_path=repo,
        branch=branch,
    )

    logger.info(f"案例已创建: {case.id}, 标题: {case.title}")
    click.echo(f"[OK] 案例已创建: {case.id}")
    click.echo(f"   标题: {case.title}")
    click.echo(f"   状态: {case.status}")
    click.echo(f"   创建时间: {case.created_at}")


@cli.command()
@click.option('--status', '-s', help='按状态筛选')
def list_cases(status: Optional[str]):
    """列出所有案例"""
    manager = get_case_manager()
    cases = manager.list_cases(status)

    if not cases:
        click.echo("暂无案例")
        return

    click.echo(f"\n共 {len(cases)} 个案例:\n")
    for case in cases:
        status_color = {
            'created': 'yellow',
            'planning': 'blue',
            'coding': 'cyan',
            'testing': 'magenta',
            'completed': 'green',
            'cancelled': 'red',
        }.get(case.status, 'white')

        click.echo(f"  [{click.style(case.status, fg=status_color)}] {case.id}: {case.title}")
        if case.description:
            desc = case.description[:60] + "..." if len(case.description) > 60 else case.description
            click.echo(f"      {desc}")


@cli.command()
@click.argument('case_id')
def show_case(case_id: str):
    """查看案例详情"""
    manager = get_case_manager()
    case = manager.get_case(case_id)

    if not case:
        click.echo(f"❌ 案例不存在: {case_id}", err=True)
        return

    click.echo(f"\n案例: {case.id}")
    click.echo(f"标题: {case.title}")
    click.echo(f"状态: {case.status}")
    click.echo(f"描述: {case.description}")
    if case.repo_path:
        click.echo(f"仓库: {case.repo_path}")
    if case.branch:
        click.echo(f"分支: {case.branch}")
    click.echo(f"创建时间: {case.created_at}")
    click.echo(f"更新时间: {case.updated_at}")


@cli.command()
@click.argument('case_id')
@click.option('--related-files', '-f', multiple=True, help='相关文件路径')
def plan(case_id: str, related_files: tuple):
    """为案例生成实现计划"""
    logger.info(f"开始为案例 {case_id} 生成实现计划")
    
    manager = get_case_manager()
    case = manager.get_case(case_id)

    if not case:
        logger.error(f"案例不存在: {case_id}")
        click.echo(f"❌ 案例不存在: {case_id}", err=True)
        return

    click.echo(f"[PLAN] 为案例 {case_id} 生成实现计划...")

    # 构建规划请求
    request: PlanningRequest = {
        "requirement_description": case.description,
        "related_files": list(related_files) if related_files else None,
    }

    # 调用 PlanningAgent
    router = get_llm_router()
    agent = PlanningAgent(router, root_dir=case.repo_path or ".")

    async def generate_plan():
        try:
            logger.debug(f"调用 PlanningAgent，案例: {case_id}")
            response = await agent.generate_plan(request)
            
            # 保存计划
            plan = manager.save_plan(
                case_id=case_id,
                plan_markdown=response["plan_markdown"],
                tasks=response["tasks"] if response["tasks"] else [],
            )

            # 记录 Agent 调用
            manager.record_agent_run(
                case_id=case_id,
                agent_type="planning",
                input_data=request,
                output_data={"plan_id": plan.id, "tasks_count": len(response["tasks"])},
                model=router.select_model("planning"),
            )

            logger.info(f"计划已生成: {plan.id}, 任务数量: {len(response['tasks'])}")
            click.echo(f"[OK] 计划已生成: {plan.id}")
            click.echo(f"   任务数量: {len(response['tasks'])}")
            click.echo(f"   计划文件: {plan.plan_md_path}")
            
            return response
        except Exception as e:
            logger.error(f"生成计划失败: {e}", exc_info=True)
            click.echo(f"[ERROR] 生成计划失败: {e}", err=True)
            manager.record_agent_run(
                case_id=case_id,
                agent_type="planning",
                input_data=request,
                status="failed",
                error_message=str(e),
            )
            raise

    asyncio.run(generate_plan())


@cli.command()
@click.argument('case_id')
def show_plan(case_id: str):
    """查看案例的实现计划"""
    manager = get_case_manager()
    plan_data = manager.get_plan(case_id)

    if not plan_data:
        click.echo(f"[ERROR] 案例 {case_id} 还没有生成计划", err=True)
        click.echo("   运行: openclaw plan <case_id> 生成计划")
        return

    plan = plan_data["plan"]
    tasks = plan_data["tasks"] or []

    click.echo(f"\n[PLAN] 实现计划: {plan.id}\n")
    
    if plan_data["markdown"]:
        click.echo("=" * 60)
        click.echo(plan_data["markdown"][:1000])  # 只显示前1000字符
        if len(plan_data["markdown"]) > 1000:
            click.echo("\n... (完整内容请查看文件)")
        click.echo("=" * 60)

    if tasks:
        click.echo(f"\n[TASKS] 子任务列表 ({len(tasks)} 个):\n")
        for i, task in enumerate(tasks, 1):
            risk_color = {
                'low': 'green',
                'medium': 'yellow',
                'high': 'red',
            }.get(task.get('risk_level', 'medium'), 'white')
            
            click.echo(f"  {i}. {task.get('title', 'N/A')}")
            click.echo(f"     风险: {click.style(task.get('risk_level', 'N/A'), fg=risk_color)}")
            if task.get('related_files'):
                click.echo(f"     相关文件: {', '.join(task['related_files'])}")


@cli.command()
@click.argument('case_id')
@click.argument('task_id')
def code(case_id: str, task_id: str):
    """为任务生成代码补丁"""
    logger.info(f"开始为任务 {task_id} (案例: {case_id}) 生成代码")
    
    manager = get_case_manager()
    case = manager.get_case(case_id)
    task = manager.get_task(task_id)

    if not case:
        logger.error(f"案例不存在: {case_id}")
        click.echo(f"❌ 案例不存在: {case_id}", err=True)
        return

    if not task:
        logger.error(f"任务不存在: {task_id}")
        click.echo(f"❌ 任务不存在: {task_id}", err=True)
        return

    click.echo(f"[CODE] 为任务 {task_id} 生成代码...")

    # 构建编码请求
    related_files = []
    if task.related_files:
        import json
        related_files = json.loads(task.related_files)

    request: CodingRequest = {
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description or "",
            "related_files": related_files,
        },
    }

    # 调用 CodingAgent
    router = get_llm_router()
    agent = CodingAgent(router, root_dir=case.repo_path or ".")

    async def generate_code():
        try:
            logger.debug(f"调用 CodingAgent，任务: {task_id}")
            response = await agent.generate_code(request)

            # 保存补丁
            for patch in response["patches"]:
                manager.save_patch(
                    case_id=case_id,
                    task_id=task_id,
                    patch_content=patch["diff"],
                    description=patch["description"],
                )

            # 更新任务状态
            manager.update_task_status(task_id, "completed")

            # 记录 Agent 调用
            manager.record_agent_run(
                case_id=case_id,
                agent_type="coding",
                task_id=task_id,
                input_data=request,
                output_data={"patches_count": len(response["patches"])},
                model=router.select_model("coding"),
            )

            logger.info(f"代码已生成，补丁数量: {len(response['patches'])}")
            click.echo(f"[OK] 代码已生成")
            click.echo(f"   补丁数量: {len(response['patches'])}")
            for i, patch in enumerate(response["patches"], 1):
                click.echo(f"   - {patch['file_path']}: {patch['description']}")

        except Exception as e:
            logger.error(f"生成代码失败: {e}", exc_info=True)
            click.echo(f"[ERROR] 生成代码失败: {e}", err=True)
            manager.record_agent_run(
                case_id=case_id,
                agent_type="coding",
                task_id=task_id,
                input_data=request,
                status="failed",
                error_message=str(e),
            )
            raise

    asyncio.run(generate_code())


@cli.command()
@click.argument('case_id')
def test(case_id: str):
    """为案例生成测试建议"""
    logger.info(f"开始为案例 {case_id} 生成测试建议")
    
    manager = get_case_manager()
    case = manager.get_case(case_id)

    if not case:
        logger.error(f"案例不存在: {case_id}")
        click.echo(f"❌ 案例不存在: {case_id}", err=True)
        return

    click.echo(f"[TEST] 为案例 {case_id} 生成测试建议...")

    # 获取所有补丁
    patches = manager.get_patches(case_id)

    if not patches:
        click.echo("[WARN] 没有找到代码补丁，请先运行: openclaw code <case_id> <task_id>")
        return

    # 构建测试请求
    changes = []
    for patch_info in patches:
        patch_content = manager.storage.load_patch(case_id, patch_info["task_id"])
        if patch_content:
            changes.append({
                "file_path": patch_info.get("file_path", "unknown"),
                "diff": patch_content,
            })

    request: TestAgentRequest = {
        "changes": changes,
    }

    # 调用 TestAgent
    router = get_llm_router()
    agent = TestAgent(router)

    async def generate_test():
        try:
            logger.debug(f"调用 TestAgent，案例: {case_id}")
            response = await agent.analyze_changes(request)

            # 保存测试结果
            suggestions_text = f"""# 测试建议

## 潜在问题
{chr(10).join([f"- [{issue['severity']}] {issue['description']}" for issue in response['potential_issues']])}

## 测试用例
{chr(10).join([f"### {tc['name']}\n{tc.get('description', '')}" for tc in response['test_cases']])}
"""

            checklist = response["manual_checklist"] or []

            manager.save_test_results(case_id, suggestions_text, checklist)

            # 更新案例状态
            manager.update_case_status(case_id, "testing")

            # 记录 Agent 调用
            manager.record_agent_run(
                case_id=case_id,
                agent_type="test",
                input_data=request,
                output_data={
                    "issues_count": len(response["potential_issues"]),
                    "test_cases_count": len(response["test_cases"]),
                },
                model=router.select_model("summary"),
            )

            logger.info(f"测试建议已生成，问题数: {len(response['potential_issues'])}, 测试用例数: {len(response['test_cases'])}")
            click.echo(f"[OK] 测试建议已生成")
            click.echo(f"   潜在问题: {len(response['potential_issues'])}")
            click.echo(f"   测试用例: {len(response['test_cases'])}")
            click.echo(f"   验收清单: {len(checklist)}")

        except Exception as e:
            logger.error(f"生成测试建议失败: {e}", exc_info=True)
            click.echo(f"[ERROR] 生成测试建议失败: {e}", err=True)
            manager.record_agent_run(
                case_id=case_id,
                agent_type="test",
                input_data=request,
                status="failed",
                error_message=str(e),
            )
            raise

    asyncio.run(generate_test())


@cli.command()
@click.argument('case_id')
def show_tasks(case_id: str):
    """查看案例的任务列表"""
    manager = get_case_manager()
    tasks = manager.get_tasks(case_id)

    if not tasks:
        click.echo(f"案例 {case_id} 还没有任务")
        return

        click.echo(f"\n[TASKS] 任务列表 ({len(tasks)} 个):\n")
    for task in tasks:
        status_color = {
            'pending': 'yellow',
            'in_progress': 'blue',
            'completed': 'green',
            'cancelled': 'red',
        }.get(task.status, 'white')

        click.echo(f"  [{click.style(task.status, fg=status_color)}] {task.id}: {task.title}")
        if task.description:
            desc = task.description[:50] + "..." if len(task.description) > 50 else task.description
            click.echo(f"      {desc}")


if __name__ == '__main__':
    cli()
