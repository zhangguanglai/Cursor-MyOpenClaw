"""
性能测试脚本

测试 API 响应时间和并发请求性能
"""

import sys
import io
import time
import requests
import asyncio
import aiohttp
from typing import List, Dict
from statistics import mean, median, stdev

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


def test_single_request(endpoint: str, method: str = "GET", data: dict = None) -> Dict:
    """测试单个请求的响应时间"""
    start_time = time.time()
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        elif method == "POST":
            response = requests.post(f"{API_BASE}{endpoint}", json=data, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        elapsed = time.time() - start_time
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "elapsed_time": elapsed,
            "error": None
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "success": False,
            "status_code": None,
            "elapsed_time": elapsed,
            "error": str(e)
        }


def test_response_time(endpoint: str, method: str = "GET", data: dict = None, iterations: int = 10) -> Dict:
    """测试响应时间（多次请求）"""
    print(f"\n[测试] {method} {endpoint} ({iterations} 次)")
    
    results = []
    for i in range(iterations):
        result = test_single_request(endpoint, method, data)
        results.append(result)
        if not result["success"]:
            print(f"  请求 {i+1} 失败: {result.get('error', result.get('status_code'))}")
    
    successful_results = [r for r in results if r["success"]]
    
    if not successful_results:
        print(f"  ❌ 所有请求都失败")
        return {
            "endpoint": endpoint,
            "method": method,
            "total_requests": iterations,
            "successful_requests": 0,
            "failed_requests": iterations,
            "avg_time": None,
            "min_time": None,
            "max_time": None,
            "median_time": None,
            "std_dev": None
        }
    
    elapsed_times = [r["elapsed_time"] for r in successful_results]
    
    stats = {
        "endpoint": endpoint,
        "method": method,
        "total_requests": iterations,
        "successful_requests": len(successful_results),
        "failed_requests": iterations - len(successful_results),
        "avg_time": mean(elapsed_times),
        "min_time": min(elapsed_times),
        "max_time": max(elapsed_times),
        "median_time": median(elapsed_times),
        "std_dev": stdev(elapsed_times) if len(elapsed_times) > 1 else 0
    }
    
    print(f"  ✅ 成功: {stats['successful_requests']}/{stats['total_requests']}")
    print(f"  平均响应时间: {stats['avg_time']:.3f}s")
    print(f"  最小响应时间: {stats['min_time']:.3f}s")
    print(f"  最大响应时间: {stats['max_time']:.3f}s")
    print(f"  中位数响应时间: {stats['median_time']:.3f}s")
    if stats['std_dev'] > 0:
        print(f"  标准差: {stats['std_dev']:.3f}s")
    
    return stats


async def test_concurrent_requests(endpoint: str, method: str = "GET", data: dict = None, concurrency: int = 10) -> Dict:
    """测试并发请求性能"""
    print(f"\n[测试] 并发请求 {method} {endpoint} (并发数: {concurrency})")
    
    async def make_request(session, index):
        start_time = time.time()
        try:
            if method == "GET":
                async with session.get(f"{API_BASE}{endpoint}", timeout=aiohttp.ClientTimeout(total=30)) as response:
                    status = response.status
                    await response.read()
            elif method == "POST":
                async with session.post(f"{API_BASE}{endpoint}", json=data, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    status = response.status
                    await response.read()
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            elapsed = time.time() - start_time
            return {
                "success": status == 200,
                "status_code": status,
                "elapsed_time": elapsed,
                "error": None
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "status_code": None,
                "elapsed_time": elapsed,
                "error": str(e)
            }
    
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [make_request(session, i) for i in range(concurrency)]
        results = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    successful_results = [r for r in results if r["success"]]
    elapsed_times = [r["elapsed_time"] for r in successful_results]
    
    stats = {
        "endpoint": endpoint,
        "method": method,
        "concurrency": concurrency,
        "total_requests": concurrency,
        "successful_requests": len(successful_results),
        "failed_requests": concurrency - len(successful_results),
        "total_time": total_time,
        "avg_time": mean(elapsed_times) if elapsed_times else None,
        "min_time": min(elapsed_times) if elapsed_times else None,
        "max_time": max(elapsed_times) if elapsed_times else None,
        "requests_per_second": concurrency / total_time if total_time > 0 else 0
    }
    
    print(f"  ✅ 成功: {stats['successful_requests']}/{stats['total_requests']}")
    print(f"  总耗时: {stats['total_time']:.3f}s")
    if stats['avg_time']:
        print(f"  平均响应时间: {stats['avg_time']:.3f}s")
        print(f"  最小响应时间: {stats['min_time']:.3f}s")
        print(f"  最大响应时间: {stats['max_time']:.3f}s")
    print(f"  吞吐量: {stats['requests_per_second']:.2f} 请求/秒")
    
    return stats


def test_health_endpoint():
    """测试健康检查端点"""
    print("\n" + "=" * 60)
    print("健康检查端点性能测试")
    print("=" * 60)
    return test_response_time("/health", "GET", iterations=20)


def test_cases_endpoint():
    """测试案例列表端点"""
    print("\n" + "=" * 60)
    print("案例列表端点性能测试")
    print("=" * 60)
    return test_response_time("/cases", "GET", iterations=10)


def test_create_case():
    """测试创建案例端点"""
    print("\n" + "=" * 60)
    print("创建案例端点性能测试")
    print("=" * 60)
    data = {
        "title": "性能测试案例",
        "description": "这是一个性能测试案例",
        "repo_path": ".",
        "branch": "main"
    }
    return test_response_time("/cases", "POST", data=data, iterations=5)


async def test_concurrent_health():
    """测试并发健康检查"""
    print("\n" + "=" * 60)
    print("并发健康检查测试")
    print("=" * 60)
    return await test_concurrent_requests("/health", "GET", concurrency=20)


async def test_concurrent_cases():
    """测试并发案例列表"""
    print("\n" + "=" * 60)
    print("并发案例列表测试")
    print("=" * 60)
    return await test_concurrent_requests("/cases", "GET", concurrency=10)


async def main():
    """主函数"""
    print("=" * 60)
    print("API 性能测试")
    print("=" * 60)
    print(f"\n测试目标: {BASE_URL}")
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 后端服务未正常运行")
            return
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        print("   请确保后端服务正在运行: python start_backend.py")
        return
    
    print("✅ 后端服务运行正常")
    
    results = []
    
    # 1. 健康检查端点
    results.append(test_health_endpoint())
    
    # 2. 案例列表端点
    results.append(test_cases_endpoint())
    
    # 3. 创建案例端点
    results.append(test_create_case())
    
    # 4. 并发测试
    results.append(await test_concurrent_health())
    results.append(await test_concurrent_cases())
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("性能测试结果汇总")
    print("=" * 60)
    
    for result in results:
        if result.get("avg_time"):
            print(f"\n{result['method']} {result['endpoint']}:")
            print(f"  成功率: {result['successful_requests']}/{result['total_requests']}")
            print(f"  平均响应时间: {result['avg_time']:.3f}s")
            if result.get("requests_per_second"):
                print(f"  吞吐量: {result['requests_per_second']:.2f} 请求/秒")
    
    print("\n" + "=" * 60)
    print("性能测试完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
