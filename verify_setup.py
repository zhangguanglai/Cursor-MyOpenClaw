"""
验证设置脚本

用于验证 LLMRouter 和相关模块是否正确安装和配置。
"""

import os
import sys

# 设置输出编码为 UTF-8（Windows 兼容）
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    try:
        from openclaw_core.llm_router import LLMRouter, LLMMessage, OpenAICompatibleProvider
        from openclaw_core.config import load_llm_config
        print("✓ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_config_loading():
    """测试配置文件加载"""
    print("\n测试配置文件加载...")
    try:
        from openclaw_core.config import load_llm_config
        config = load_llm_config()
        providers = list(config["providers"].keys())
        task_types = list(config["models"].keys())
        print(f"✓ 配置文件加载成功")
        print(f"  Providers: {providers}")
        print(f"  Task types: {task_types}")
        return True
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False


def test_router_initialization():
    """测试 LLMRouter 初始化"""
    print("\n测试 LLMRouter 初始化...")
    try:
        # 设置测试环境变量
        os.environ.setdefault("QWEN_API_KEY", "test_key")
        os.environ.setdefault("MINIMAX_API_KEY", "test_key")
        
        from openclaw_core.llm_router import LLMRouter
        router = LLMRouter()
        
        providers = list(router.providers.keys())
        planning_model = router.select_model("planning")
        coding_model = router.select_model("coding")
        summary_model = router.select_model("summary")
        
        print(f"✓ LLMRouter 初始化成功")
        print(f"  可用 Providers: {providers}")
        print(f"  Planning 模型: {planning_model}")
        print(f"  Coding 模型: {coding_model}")
        print(f"  Summary 模型: {summary_model}")
        return True
    except Exception as e:
        print(f"✗ LLMRouter 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("OpenClaw Core - 设置验证")
    print("=" * 50)
    
    results = []
    results.append(test_imports())
    results.append(test_config_loading())
    results.append(test_router_initialization())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✓ 所有验证通过！")
        sys.exit(0)
    else:
        print("✗ 部分验证失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
