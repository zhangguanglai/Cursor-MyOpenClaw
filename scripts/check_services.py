"""
检查服务状态脚本

检查前后端服务是否正在运行
"""

import sys
import io
import socket
import requests
from pathlib import Path

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def check_port(host, port):
    """检查端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_backend():
    """检查后端服务"""
    print("\n[检查] 后端服务 (http://localhost:8000)")
    
    # 检查端口
    if not check_port("localhost", 8000):
        print("❌ 端口 8000 未开放")
        print("   请运行: python start_backend.py")
        return False
    
    # 检查健康端点
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            return True
        else:
            print(f"⚠️  后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到后端服务: {e}")
        print("   请运行: python start_backend.py")
        return False


def check_frontend():
    """检查前端服务"""
    print("\n[检查] 前端服务 (http://localhost:5173)")
    
    # 检查端口
    if not check_port("localhost", 5173):
        print("❌ 端口 5173 未开放")
        print("   请运行: cd openclaw-studio-frontend && npm run dev")
        return False
    
    # 尝试访问前端
    try:
        response = requests.get("http://localhost:5173", timeout=2)
        if response.status_code == 200:
            print("✅ 前端服务运行正常")
            return True
        else:
            print(f"⚠️  前端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到前端服务: {e}")
        print("   请运行: cd openclaw-studio-frontend && npm run dev")
        return False


def main():
    """检查所有服务"""
    print("=" * 60)
    print("服务状态检查")
    print("=" * 60)
    
    backend_ok = check_backend()
    frontend_ok = check_frontend()
    
    print("\n" + "=" * 60)
    print("检查结果")
    print("=" * 60)
    print(f"后端服务: {'✅ 正常' if backend_ok else '❌ 未运行'}")
    print(f"前端服务: {'✅ 正常' if frontend_ok else '❌ 未运行'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 所有服务运行正常，可以开始测试！")
        return 0
    else:
        print("\n⚠️  请先启动未运行的服务")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n检查被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
