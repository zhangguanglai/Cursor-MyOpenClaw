"""测试前后端集成"""

import requests
import json
import sys

def test_backend():
    """测试后端 API"""
    print("=" * 60)
    print("测试后端 API")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 1. 健康检查
    print("\n1. 健康检查...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ 健康检查通过: {response.json()}")
        else:
            print(f"   ❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 无法连接到后端: {e}")
        print("   💡 请确保后端服务正在运行: python start_backend.py")
        return False
    
    # 2. 获取案例列表
    print("\n2. 获取案例列表...")
    try:
        response = requests.get(f"{base_url}/api/v1/cases", timeout=5)
        if response.status_code == 200:
            cases = response.json()
            print(f"   ✅ 获取成功，共 {len(cases)} 个案例")
            if cases:
                print(f"   📋 第一个案例: {cases[0].get('title', 'N/A')}")
        else:
            print(f"   ⚠️  获取失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 3. 创建测试案例
    print("\n3. 创建测试案例...")
    try:
        test_case = {
            "title": "集成测试案例",
            "description": "这是一个用于测试前后端集成的案例",
            "repo_path": ".",
            "branch": "main"
        }
        response = requests.post(
            f"{base_url}/api/v1/cases",
            json=test_case,
            timeout=10
        )
        if response.status_code == 200:
            case_data = response.json()
            print(f"   ✅ 案例创建成功")
            print(f"   📝 案例 ID: {case_data.get('id', 'N/A')}")
            print(f"   📝 标题: {case_data.get('title', 'N/A')}")
            return case_data.get('id')
        else:
            print(f"   ❌ 创建失败: {response.status_code}")
            print(f"   📄 响应: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    return None

def test_frontend():
    """测试前端服务"""
    print("\n" + "=" * 60)
    print("测试前端服务")
    print("=" * 60)
    
    frontend_url = "http://localhost:5173"
    
    print("\n1. 检查前端服务...")
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ 前端服务正常运行")
            print(f"   🌐 访问地址: {frontend_url}")
        else:
            print(f"   ⚠️  前端服务响应异常: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 无法连接到前端: {e}")
        print("   💡 请确保前端服务正在运行: cd openclaw-studio-frontend && npm run dev")

def main():
    print("\n🚀 开始前后端集成测试\n")
    
    # 测试后端
    case_id = test_backend()
    
    # 测试前端
    test_frontend()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n📋 下一步:")
    print("   1. 访问前端: http://localhost:5173")
    print("   2. 访问后端 API 文档: http://localhost:8000/docs")
    if case_id:
        print(f"   3. 测试案例 ID: {case_id}")
    print("\n💡 提示:")
    print("   - 后端服务: python start_backend.py")
    print("   - 前端服务: cd openclaw-studio-frontend && npm run dev")
    print("   - 详细测试指南: 查看 TESTING_GUIDE.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试已取消")
        sys.exit(0)
