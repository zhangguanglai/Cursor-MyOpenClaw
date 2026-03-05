"""
直接测试规划 API

测试规划 API 端点，查看详细错误信息
"""

import sys
import io
import requests
import json

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


def test_planning_api():
    """测试规划 API"""
    print("=" * 60)
    print("规划 API 直接测试")
    print("=" * 60)
    
    # 先创建一个测试案例
    print("\n[步骤 1] 创建测试案例...")
    try:
        payload = {
            "title": "规划 API 测试案例",
            "description": "测试规划 API 功能",
            "repo_path": ".",
            "branch": "main"
        }
        response = requests.post(f"{API_BASE}/cases", json=payload, timeout=10)
        if response.status_code != 200:
            print(f"❌ 创建案例失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return
        case_data = response.json()
        case_id = case_data["id"]
        print(f"✅ 案例创建成功: {case_id}")
    except Exception as e:
        print(f"❌ 创建案例失败: {e}")
        return
    
    # 测试生成计划
    print("\n[步骤 2] 测试生成计划...")
    try:
        payload = {
            "requirement_description": "添加一个简单的日志功能，记录用户操作",
            "related_files": []
        }
        print(f"   发送请求到: POST {API_BASE}/cases/{case_id}/planning")
        print(f"   请求内容: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            f"{API_BASE}/cases/{case_id}/planning",
            json=payload,
            timeout=120  # 计划生成可能需要较长时间
        )
        
        print(f"\n   响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 计划生成成功")
            print(f"   Plan ID: {data.get('plan_id', 'N/A')}")
            print(f"   任务数量: {len(data.get('tasks', []))}")
            print(f"   计划长度: {len(data.get('plan_markdown', ''))} 字符")
            
            if data.get('tasks'):
                print("\n   任务列表:")
                for i, task in enumerate(data['tasks'][:5], 1):
                    print(f"   {i}. {task.get('title', 'N/A')}")
        else:
            print(f"❌ 计划生成失败")
            print(f"   错误信息: {response.text}")
            
            # 尝试解析错误详情
            try:
                error_data = response.json()
                print(f"\n   错误详情:")
                print(f"   {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                pass
    except requests.exceptions.Timeout:
        print("❌ 请求超时（超过 120 秒）")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        test_planning_api()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
