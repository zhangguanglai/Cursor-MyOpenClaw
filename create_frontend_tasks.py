"""基于计划文档创建详细的前端开发任务列表"""

import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager
from openclaw_studio.database import Task

def main():
    case_id = "case-8b994138"
    
    print("=" * 60)
    print("创建前端开发任务列表")
    print("=" * 60)
    print(f"\n案例 ID: {case_id}")
    
    manager = CaseManager()
    
    # 基于计划文档创建详细任务列表
    tasks = [
        {
            "id": "task-001",
            "title": "搭建 React + TypeScript 项目结构",
            "description": "使用 Vite 创建项目，配置 TypeScript、ESLint、Prettier。创建基础目录结构（components, features, services, store, utils）。",
            "related_files": [],
            "risk_level": "low"
        },
        {
            "id": "task-002",
            "title": "安装和配置核心依赖",
            "description": "安装 Ant Design、TanStack Query、Zustand、react-markdown、diff2html-react 等核心依赖库。配置开发依赖（ESLint、Prettier）。",
            "related_files": [],
            "risk_level": "low"
        },
        {
            "id": "task-003",
            "title": "实现 API 客户端封装",
            "description": "创建 axios 实例（apiClient.ts），配置 baseURL、timeout、拦截器。创建 TanStack Query hooks（cases.ts, planning.ts, coding.ts, testing.ts, history.ts）。",
            "related_files": ["openclaw_studio/api/main.py", "openclaw_studio/api/v1/cases.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-004",
            "title": "实现需求中心视图（CaseList + CaseForm）",
            "description": "创建案例列表页面，支持创建/查看/编辑案例。使用 Ant Design Table 和 Drawer 组件。集成 useCasesQuery 和 useCreateCaseMutation。",
            "related_files": ["openclaw_studio/api/v1/cases.py", "openclaw_studio/models.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-005",
            "title": "实现规划视图（PlanEditor + TaskTable）",
            "description": "创建计划展示页面，支持 Markdown 渲染和编辑。创建任务列表表格。支持触发 PlanningAgent。集成 useTriggerPlanningMutation 和 useCasePlanQuery。",
            "related_files": ["openclaw_studio/api/v1/planning.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-006",
            "title": "实现执行视图（PatchList + DiffPreview）",
            "description": "创建补丁列表页面，支持查看所有补丁。实现 Diff 预览组件（使用 diff2html-react）。支持为任务生成代码补丁。集成 useGenerateCodeMutation 和 useCasePatchesQuery。",
            "related_files": ["openclaw_studio/api/v1/coding.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-007",
            "title": "实现测试视图（Checklist + SuggestionsView）",
            "description": "创建测试建议页面，支持查看潜在问题、测试用例和验收清单。实现 Markdown 渲染（使用 react-markdown）。支持触发 TestAgent。集成 useGenerateTestMutation。",
            "related_files": ["openclaw_studio/api/v1/testing.py"],
            "risk_level": "medium"
        },
        {
            "id": "task-008",
            "title": "实现历史视图（TimelineView）",
            "description": "创建历史记录时间线页面，按时间倒序展示完整闭环记录（Case 创建、Plan 生成、Coding runs、Test runs）。使用 Ant Design Timeline 组件。集成 useCaseHistoryQuery。",
            "related_files": ["openclaw_studio/api/v1/history.py"],
            "risk_level": "low"
        },
        {
            "id": "task-009",
            "title": "实现路由和导航（React Router + Layout）",
            "description": "配置 React Router，实现路由导航。创建主布局组件（使用 Ant Design Layout）。实现顶部导航菜单和侧边栏。支持路由跳转和参数传递。",
            "related_files": [],
            "risk_level": "low"
        },
        {
            "id": "task-010",
            "title": "实现响应式设计",
            "description": "使用 Ant Design 的 useBreakpoint Hook 实现响应式布局。适配移动端（xs）、平板（sm/md）、桌面（lg/xl）。优化各视图在不同屏幕尺寸下的显示效果。",
            "related_files": [],
            "risk_level": "medium"
        },
        {
            "id": "task-011",
            "title": "前后端联调和测试",
            "description": "验证所有 API 端点正常工作。测试完整流程（创建案例 → 生成计划 → 生成代码 → 生成测试 → 查看历史）。编写基础单元测试和 E2E 测试。修复发现的 bug。",
            "related_files": ["openclaw_studio/api"],
            "risk_level": "high"
        },
    ]
    
    print(f"\n📋 创建 {len(tasks)} 个任务...")
    
    # 获取计划
    plan_data = manager.get_plan(case_id)
    if not plan_data:
        print("❌ 计划不存在")
        return
    
    plan = plan_data.get("plan")
    if not plan:
        print("❌ 计划对象不存在")
        return
    
    plan_id = plan.id
    
    # 更新计划 JSON
    plan_json_path = Path(f"cases/{case_id}/plan.json")
    plan_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(plan_json_path, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 计划 JSON 已更新: {plan_json_path}")
    
    # 保存任务到数据库
    created_count = 0
    skipped_count = 0
    
    for task_data in tasks:
        task_id = task_data["id"]
        related_files = json.dumps(task_data.get("related_files", [])) if task_data.get("related_files") else None
        
        # 检查任务是否已存在
        existing_task = manager.get_task(task_id)
        if existing_task:
            # 更新现有任务
            manager.db.update_task(
                task_id,
                title=task_data["title"],
                description=task_data.get("description", ""),
                related_files=related_files,
                risk_level=task_data.get("risk_level", "medium"),
            )
            skipped_count += 1
            print(f"   ↻ 任务 {task_id} 已更新")
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
            created_count += 1
            print(f"   ✅ 任务 {task_id} 已创建")
        except Exception as e:
            print(f"   ⚠️  任务 {task_id} 创建失败: {e}")
    
    manager.close()
    
    print(f"\n✅ 任务创建完成")
    print(f"   新建: {created_count}")
    print(f"   更新: {skipped_count}")
    print(f"   总计: {len(tasks)}")
    
    print(f"\n📋 任务列表:")
    for task in tasks:
        print(f"   {task['id']}: {task['title']}")
    
    print(f"\n下一步: 开始为任务生成代码")
    print(f"   运行: python generate_frontend_code.py {case_id}")

if __name__ == "__main__":
    main()
