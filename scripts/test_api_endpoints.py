"""
API 端点测试脚本

测试所有 API 端点是否正常工作
"""

import sys
import io
import requests
import json
from pathlib import Path

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


def test_health():
    """测试健康检查端点"""
    print("\n[测试] GET /health")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200, f"状态码: {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", f"状态: {data.get('status')}"
        print("✅ 健康检查通过")
        return True
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False


def test_create_case():
    """测试创建案例"""
    print("\n[测试] POST /cases")
    try:
        payload = {
            "title": "API 测试案例",
            "description": "这是一个 API 测试案例",
            "repo_path": ".",
            "branch": "main"
        }
        response = requests.post(f"{API_BASE}/cases", json=payload, timeout=10)
        assert response.status_code == 200, f"状态码: {response.status_code}"
        data = response.json()
        assert "id" in data, "响应中没有 id"
        print(f"✅ 案例创建成功: {data['id']}")
        return data["id"]
    except Exception as e:
        print(f"❌ 创建案例失败: {e}")
        return None


def test_get_case(case_id):
    """测试获取案例"""
    print(f"\n[测试] GET /cases/{case_id}")
    try:
        response = requests.get(f"{API_BASE}/cases/{case_id}", timeout=5)
        assert response.status_code == 200, f"状态码: {response.status_code}"
        data = response.json()
        assert data["id"] == case_id, "案例 ID 不匹配"
        print(f"✅ 获取案例成功: {data['title']}")
        return True
    except Exception as e:
        print(f"❌ 获取案例失败: {e}")
        return False


def test_list_cases():
    """测试列出案例"""
    print("\n[测试] GET /cases")
    try:
        response = requests.get(f"{API_BASE}/cases", timeout=5)
        assert response.status_code == 200, f"状态码: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "响应不是列表"
        print(f"✅ 列出案例成功: {len(data)} 个案例")
        return True
    except Exception as e:
        print(f"❌ 列出案例失败: {e}")
        return False


def test_generate_plan(case_id):
    """测试生成计划"""
    print(f"\n[测试] POST /cases/{case_id}/planning")
    try:
        payload = {
            "requirement_description": "测试需求描述",
            "related_files": []
        }
        response = requests.post(
            f"{API_BASE}/cases/{case_id}/planning",
            json=payload,
            timeout=60  # 计划生成可能需要较长时间
        )
        assert response.status_code == 200, f"状态码: {response.status_code}"
        data = response.json()
        assert "plan_id" in data, "响应中没有 plan_id"
        print(f"✅ 计划生成成功: {data['plan_id']}")
        return True
    except Exception as e:
        print(f"❌ 生成计划失败: {e}")
        return False


def test_get_plan(case_id):
    """测试获取计划"""
    print(f"\n[测试] GET /cases/{case_id}/plan")
    try:
        response = requests.get(f"{API_BASE}/cases/{case_id}/plan", timeout=5)
        if response.status_code == 404:
            print("⚠️  计划不存在（可能还未生成）")
            return True
        assert response.status_code == 200, f"状态码: {response.status_code}"
        data = response.json()
        assert "plan_markdown" in data, "响应中没有 plan_markdown"
        print(f"✅ 获取计划成功: {len(data.get('tasks', []))} 个任务")
        return True
    except Exception as e:
        print(f"❌ 获取计划失败: {e}")
        return False


def test_get_patches(case_id):
    """测试获取补丁列表"""
    print(f"\n[测试] GET /cases/{case_id}/patches")
    try:
        response = requests.get(f"{API_BASE}/cases/{case_id}/patches", timeout=5)
        assert response.status_code == 200, f"状态码: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "响应不是列表"
        print(f"✅ 获取补丁列表成功: {len(data)} 个补丁")
        return True
    except Exception as e:
        print(f"❌ 获取补丁列表失败: {e}")
        return False


def test_get_history(case_id):
    """测试获取历史记录"""
    print(f"\n[测试] GET /cases/{case_id}/history")
    try:
        response = requests.get(f"{API_BASE}/cases/{case_id}/history", timeout=5)
        assert response.status_code == 200, f"状态码: {response.status_code}"
        data = response.json()
        assert "history" in data, "响应中没有 history"
        print(f"✅ 获取历史记录成功: {len(data['history'])} 条记录")
        return True
    except Exception as e:
        print(f"❌ 获取历史记录失败: {e}")
        return False


def test_git_status(case_id):
    """测试获取 Git 状态"""
    print(f"\n[测试] GET /cases/{case_id}/git-status")
    try:
        response = requests.get(f"{API_BASE}/cases/{case_id}/git-status", timeout=5)
        if response.status_code == 404:
            print("⚠️  Git 状态不可用（可能案例未关联 Git 仓库）")
            return True
        assert response.status_code == 200, f"状态码: {response.status_code}"
        data = response.json()
        assert "current_branch" in data, "响应中没有 current_branch"
        print(f"✅ 获取 Git 状态成功: {data['current_branch']}")
        return True
    except Exception as e:
        print(f"❌ 获取 Git 状态失败: {e}")
        return False


def test_knowledge_search():
    """测试知识库搜索"""
    print("\n[测试] GET /knowledge/search")
    try:
        response = requests.get(
            f"{API_BASE}/knowledge/search",
            params={"q": "Python"},
            timeout=5
        )
        assert response.status_code == 200, f"状态码: {response.status_code}"
        data = response.json()
        assert "results" in data, "响应中没有 results"
        print(f"✅ 知识库搜索成功: {data['total']} 个结果")
        return True
    except Exception as e:
        print(f"❌ 知识库搜索失败: {e}")
        return False


def test_knowledge_templates():
    """测试获取模板列表"""
    print("\n[测试] GET /knowledge/templates")
    try:
        response = requests.get(f"{API_BASE}/knowledge/templates", timeout=5)
        assert response.status_code == 200, f"状态码: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "响应不是列表"
        print(f"✅ 获取模板列表成功: {len(data)} 个模板")
        return True
    except Exception as e:
        print(f"❌ 获取模板列表失败: {e}")
        return False


def main():
    """运行所有 API 测试"""
    print("=" * 60)
    print("API 端点测试")
    print("=" * 60)
    print(f"\n测试目标: {BASE_URL}")
    
    results = []
    
    # 基础测试
    results.append(("健康检查", test_health()))
    
    # 案例相关测试
    case_id = test_create_case()
    results.append(("创建案例", case_id is not None))
    
    if case_id:
        results.append(("获取案例", test_get_case(case_id)))
        results.append(("列出案例", test_list_cases()))
        results.append(("生成计划", test_generate_plan(case_id)))
        results.append(("获取计划", test_get_plan(case_id)))
        results.append(("获取补丁", test_get_patches(case_id)))
        results.append(("获取历史", test_get_history(case_id)))
        results.append(("Git 状态", test_git_status(case_id)))
    
    # 知识库测试
    results.append(("知识库搜索", test_knowledge_search()))
    results.append(("模板列表", test_knowledge_templates()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
