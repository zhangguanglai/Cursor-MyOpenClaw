"""启动后端 API 服务器"""

import uvicorn
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    print("=" * 60)
    print("启动 OpenClaw Studio API 服务器")
    print("=" * 60)
    print("\n服务器地址: http://localhost:8000")
    print("API 文档: http://localhost:8000/docs")
    print("\n按 Ctrl+C 停止服务器\n")
    
    uvicorn.run(
        "openclaw_studio.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
