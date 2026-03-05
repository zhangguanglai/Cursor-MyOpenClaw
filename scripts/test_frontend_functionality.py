"""
前端功能测试脚本

测试前端页面的基本功能
"""

import sys
import io
import requests
from typing import Dict, List

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

FRONTEND_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:8000"


def test_frontend_accessible():
    """测试前端是否可访问"""
    print("\n[测试] 前端服务可访问性")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"✅ 前端服务可访问: {FRONTEND_URL}")
            return True
        else:
            print(f"⚠️  前端服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法访问前端服务: {e}")
        print("   请确保前端服务正在运行: cd openclaw-studio-frontend && npm run dev")
        return False


def test_frontend_api_connection():
    """测试前端到后端的 API 连接"""
    print("\n[测试] 前端到后端 API 连接")
    try:
        # 测试后端健康检查
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ 后端 API 可访问: {BACKEND_URL}")
            return True
        else:
            print(f"⚠️  后端 API 响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法访问后端 API: {e}")
        print("   请确保后端服务正在运行: python start_backend.py")
        return False


def test_api_endpoints():
    """测试关键 API 端点"""
    print("\n[测试] 关键 API 端点")
    
    endpoints = [
        ("GET", "/api/v1/cases", "案例列表"),
        ("GET", "/health", "健康检查"),
        ("GET", "/api/v1/knowledge/templates", "知识库模板"),
    ]
    
    results = []
    for method, endpoint, name in endpoints:
        try:
            url = f"{BACKEND_URL}{endpoint}"
            response = requests.get(url, timeout=10)
            success = response.status_code == 200
            results.append({
                "name": name,
                "endpoint": endpoint,
                "success": success,
                "status_code": response.status_code
            })
            
            status = "✅" if success else "❌"
            print(f"  {status} {name}: {endpoint} ({response.status_code})")
        except Exception as e:
            results.append({
                "name": name,
                "endpoint": endpoint,
                "success": False,
                "error": str(e)
            })
            print(f"  ❌ {name}: {endpoint} (错误: {e})")
    
    return results


def test_create_and_view_case():
    """测试创建和查看案例"""
    print("\n[测试] 创建和查看案例")
    
    # 创建案例
    try:
        data = {
            "title": "前端功能测试案例",
            "description": "这是一个前端功能测试案例",
            "repo_path": ".",
            "branch": "main"
        }
        response = requests.post(f"{BACKEND_URL}/api/v1/cases", json=data, timeout=10)
        if response.status_code == 200:
            case = response.json()
            case_id = case["id"]
            print(f"✅ 案例创建成功: {case_id}")
            
            # 获取案例详情
            response = requests.get(f"{BACKEND_URL}/api/v1/cases/{case_id}", timeout=5)
            if response.status_code == 200:
                print(f"✅ 案例详情获取成功")
                return True
            else:
                print(f"⚠️  案例详情获取失败: {response.status_code}")
                return False
        else:
            print(f"❌ 案例创建失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("前端功能测试")
    print("=" * 60)
    
    results = {
        "frontend_accessible": False,
        "api_connection": False,
        "api_endpoints": [],
        "create_case": False
    }
    
    # 1. 测试前端可访问性
    results["frontend_accessible"] = test_frontend_accessible()
    
    # 2. 测试 API 连接
    results["api_connection"] = test_frontend_api_connection()
    
    # 3. 测试 API 端点
    results["api_endpoints"] = test_api_endpoints()
    
    # 4. 测试创建案例
    if results["api_connection"]:
        results["create_case"] = test_create_and_view_case()
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    print(f"\n前端可访问: {'✅' if results['frontend_accessible'] else '❌'}")
    print(f"API 连接: {'✅' if results['api_connection'] else '❌'}")
    
    if results["api_endpoints"]:
        successful = sum(1 for r in results["api_endpoints"] if r["success"])
        total = len(results["api_endpoints"])
        print(f"API 端点: {successful}/{total} 通过")
    
    print(f"创建案例: {'✅' if results['create_case'] else '❌'}")
    
    # 建议
    print("\n" + "=" * 60)
    print("建议")
    print("=" * 60)
    
    if not results["frontend_accessible"]:
        print("\n⚠️  前端服务未运行")
        print("   启动命令: cd openclaw-studio-frontend && npm run dev")
    
    if not results["api_connection"]:
        print("\n⚠️  后端服务未运行")
        print("   启动命令: python start_backend.py")
    
    if results["frontend_accessible"] and results["api_connection"]:
        print("\n✅ 前后端服务都正常运行")
        print("   可以访问前端页面进行手动测试:")
        print(f"   - 需求中心: {FRONTEND_URL}/cases")
        print(f"   - API 文档: {BACKEND_URL}/docs")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
