"""创建 Web API 模块开发案例"""

import sys
import io

# 设置 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from openclaw_studio.case_manager import CaseManager

def main():
    manager = CaseManager()
    
    case = manager.create_case(
        title="实现 Web 控制台后端 API",
        description="""使用 FastAPI 实现 OpenClaw Studio 后端 API，提供 RESTful 接口供前端调用。

功能目标：
- 提供案例管理 API（CRUD 操作）
- 提供规划 API（触发 PlanningAgent）
- 提供编码 API（触发 CodingAgent）
- 提供测试 API（触发 TestAgent）
- 提供历史记录 API（查看完整闭环）
- 集成 OpenClaw Core 的 Agent 调用
- 支持异步任务处理

用户场景：
- 前端通过 API 创建和管理案例
- 前端触发 Agent 生成计划、代码、测试建议
- 前端查看历史记录和 Agent 调用日志
- 前端查看补丁和 diff

验收标准：
- 所有 API 端点正常工作
- 集成测试通过
- API 文档自动生成（FastAPI 自动生成）
- 错误处理完善
- 日志记录完整

技术约束：
- 使用 FastAPI 框架
- 异步处理 Agent 调用
- 与现有 CaseManager 集成
- 使用 Pydantic 进行数据验证
- 遵循 RESTful 设计原则""",
        repo_path=".",
        branch="main"
    )
    
    print(f"✅ 案例已创建: {case.id}")
    print(f"   标题: {case.title}")
    print(f"   状态: {case.status}")
    print(f"   创建时间: {case.created_at}")
    print(f"\n下一步: 运行 'python -m openclaw_cli.cli plan {case.id}' 生成计划")

if __name__ == "__main__":
    main()
