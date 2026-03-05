"""测试所有视图功能的脚本"""

import sys
import io
import requests
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    print("=" * 60)
    print("测试健康检查端点")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        print(f"✅ 健康检查通过: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_cases_api():
    """测试案例 API"""
    print("\n" + "=" * 60)
    print("测试案例 API")
    print("=" * 60)
    try:
        # 获取案例列表
        response = requests.get(f"{BASE_URL}/api/v1/cases")
        response.raise_for_status()
        cases = response.json()
        print(f"✅ 获取案例列表成功: {len(cases)} 个案例")
        
        if len(cases) > 0:
            case_id = cases[0]["id"]
            print(f"   使用案例: {case_id}")
            
            # 获取案例详情
            response = requests.get(f"{BASE_URL}/api/v1/cases/{case_id}")
            response.raise_for_status()
            case = response.json()
            print(f"✅ 获取案例详情成功: {case['title']}")
            
            return case_id
        else:
            print("⚠️  没有案例，跳过后续测试")
            return None
    except Exception as e:
        print(f"❌ 案例 API 测试失败: {e}")
        return None

def test_planning_api(case_id):
    """测试规划 API"""
    if not case_id:
        return
    print("\n" + "=" * 60)
    print("测试规划 API")
    print("=" * 60)
    try:
        # 获取计划
        response = requests.get(f"{BASE_URL}/api/v1/cases/{case_id}/plan")
        if response.status_code == 200:
            plan = response.json()
            print(f"✅ 获取计划成功: {len(plan.get('tasks', []))} 个任务")
        elif response.status_code == 404:
            print("⚠️  计划不存在（这是正常的，如果案例还没有生成计划）")
        else:
            response.raise_for_status()
    except Exception as e:
        print(f"❌ 规划 API 测试失败: {e}")

def test_coding_api(case_id):
    """测试编码 API"""
    if not case_id:
        return
    print("\n" + "=" * 60)
    print("测试编码 API")
    print("=" * 60)
    try:
        # 获取补丁列表
        response = requests.get(f"{BASE_URL}/api/v1/cases/{case_id}/patches")
        if response.status_code == 200:
            patches = response.json()
            print(f"✅ 获取补丁列表成功: {len(patches)} 个补丁")
        elif response.status_code == 404:
            print("⚠️  补丁列表为空（这是正常的，如果案例还没有生成补丁）")
        else:
            response.raise_for_status()
    except Exception as e:
        print(f"❌ 编码 API 测试失败: {e}")

def test_testing_api(case_id):
    """测试测试 API"""
    if not case_id:
        return
    print("\n" + "=" * 60)
    print("测试测试 API")
    print("=" * 60)
    try:
        # 获取测试结果
        response = requests.get(f"{BASE_URL}/api/v1/cases/{case_id}/test")
        if response.status_code == 200:
            test_result = response.json()
            print(f"✅ 获取测试结果成功")
            print(f"   潜在问题: {len(test_result.get('potential_issues', []))} 个")
            print(f"   测试用例: {len(test_result.get('test_cases', []))} 个")
        elif response.status_code == 404:
            print("⚠️  测试结果不存在（这是正常的，如果案例还没有执行测试）")
        else:
            response.raise_for_status()
    except Exception as e:
        print(f"❌ 测试 API 测试失败: {e}")

def test_history_api(case_id):
    """测试历史 API"""
    if not case_id:
        return
    print("\n" + "=" * 60)
    print("测试历史 API")
    print("=" * 60)
    try:
        # 获取历史记录
        response = requests.get(f"{BASE_URL}/api/v1/cases/{case_id}/history")
        response.raise_for_status()
        history = response.json()
        print(f"✅ 获取历史记录成功")
        print(f"   案例: {history['case']['title']}")
        print(f"   历史事件数: {len(history.get('history', []))} 个")
        
        # 测试筛选功能
        response = requests.get(f"{BASE_URL}/api/v1/cases/{case_id}/history?types=plan,patch")
        response.raise_for_status()
        filtered_history = response.json()
        print(f"✅ 筛选功能测试成功: {len(filtered_history.get('history', []))} 个事件")
    except Exception as e:
        print(f"❌ 历史 API 测试失败: {e}")

def main():
    print("🧪 OpenClaw Studio API 功能测试")
    print("=" * 60)
    
    # 测试健康检查
    if not test_health():
        print("\n❌ 后端服务未运行，请先启动后端服务")
        print("   运行: python start_backend.py")
        return
    
    # 测试各个 API
    case_id = test_cases_api()
    test_planning_api(case_id)
    test_coding_api(case_id)
    test_testing_api(case_id)
    test_history_api(case_id)
    
    print("\n" + "=" * 60)
    print("✅ 所有 API 测试完成")
    print("=" * 60)
    print("\n下一步:")
    print("1. 启动前端服务: cd openclaw-studio-frontend && npm run dev")
    print("2. 访问 http://localhost:5173 测试前端功能")
    print("3. 测试各个视图的交互功能")

if __name__ == "__main__":
    main()
