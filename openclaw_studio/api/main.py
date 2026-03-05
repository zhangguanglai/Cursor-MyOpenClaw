"""
OpenClaw Studio API 主应用

FastAPI 应用入口，配置路由、中间件和异常处理。
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from openclaw_core.logger import get_logger
from openclaw_studio.api.v1 import cases, history, planning, coding, testing, git

logger = get_logger("openclaw.api")

app = FastAPI(
    title="OpenClaw Studio API",
    version="0.1.0",
    description="Backend for OpenClaw Studio — AI-native development studio",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 配置（开发时开放，生产建议限制 origin）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(cases.router, prefix="/api/v1", tags=["Cases"])
app.include_router(planning.router, prefix="/api/v1", tags=["Planning"])
app.include_router(coding.router, prefix="/api/v1", tags=["Coding"])
app.include_router(testing.router, prefix="/api/v1", tags=["Testing"])
app.include_router(history.router, prefix="/api/v1", tags=["History"])
app.include_router(git.router, prefix="/api/v1", tags=["Git"])

# 全局异常处理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request data", "errors": exc.errors()},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error {exc.status_code} on {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# 启动和关闭事件
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 OpenClaw Studio API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 OpenClaw Studio API shutting down...")

@app.get("/")
async def root():
    """API 根路径"""
    return {
        "message": "OpenClaw Studio API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health():
    """健康检查端点"""
    from datetime import datetime, timezone
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "OpenClaw Studio API",
        "version": "0.1.0"
    }
