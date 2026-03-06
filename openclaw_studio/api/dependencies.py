"""
依赖注入模块

提供 CaseManager 和 Agent 的单例注入。
"""

from typing import Generator
from fastapi import Depends

from openclaw_studio.case_manager import CaseManager
from openclaw_core.llm_router import LLMRouter
from openclaw_core.agents import PlanningAgent, CodingAgent, TestAgent

# 单例管理器（线程安全，适合开发；生产可换为 DI 容器）
_case_manager: CaseManager | None = None
_llm_router: LLMRouter | None = None


def get_case_manager() -> Generator[CaseManager, None, None]:
    """获取 CaseManager 实例（单例）"""
    global _case_manager
    if _case_manager is None:
        _case_manager = CaseManager()
    yield _case_manager


def get_llm_router() -> LLMRouter:
    """获取 LLMRouter 实例（单例）"""
    global _llm_router
    if _llm_router is None:
        from openclaw_core.logger import get_logger
        logger = get_logger("openclaw.api.dependencies")
        logger.info("初始化 LLMRouter...")
        try:
            _llm_router = LLMRouter()
            logger.info(f"LLMRouter 初始化成功，可用 Provider: {list(_llm_router.providers.keys())}")
        except Exception as e:
            logger.error(f"LLMRouter 初始化失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    return _llm_router


def get_planning_agent(
    llm_router: LLMRouter = Depends(get_llm_router),
) -> PlanningAgent:
    """获取 PlanningAgent 实例"""
    return PlanningAgent(llm_router=llm_router, root_dir=".")


def get_coding_agent(
    llm_router: LLMRouter = Depends(get_llm_router),
) -> CodingAgent:
    """获取 CodingAgent 实例"""
    return CodingAgent(llm_router=llm_router, root_dir=".")


def get_test_agent(
    llm_router: LLMRouter = Depends(get_llm_router),
) -> TestAgent:
    """获取 TestAgent 实例"""
    return TestAgent(llm_router=llm_router)
