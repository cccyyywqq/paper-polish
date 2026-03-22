from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time
import asyncio

from .config import get_settings
from .database import init_db, engine
from .routers import polish_router, anti_ai_router, upload_router, auth_router, progress_router
from .routers.progress import progress_store
from .utils import logger, limiter, cache

settings = get_settings()

app_start_time = time.time()
request_count = 0
error_count = 0
last_errors = []
MAX_ERROR_HISTORY = 10


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting application (env={settings.environment}, debug={settings.is_debug})...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down application...")
    cache.clear()


app = FastAPI(
    title="论文润色工具",
    description="AI驱动的论文润色与去AI化处理工具",
    version="2.1.0",
    docs_url="/docs" if settings.is_debug else None,
    redoc_url="/redoc" if settings.is_debug else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def error_response(status_code: int, message: str, error_code: str = None, details=None):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "error_code": error_code,
            "details": details if settings.is_debug else None,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(
        status_code=exc.status_code,
        message=exc.detail,
        error_code=f"HTTP_{exc.status_code}",
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    details = []
    for error in errors:
        details.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    return error_response(
        status_code=422,
        message="请求参数验证失败",
        error_code="VALIDATION_ERROR",
        details=details,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    global error_count, last_errors
    error_count += 1
    last_errors.append({
        "time": datetime.utcnow().isoformat(),
        "error": str(exc),
        "type": type(exc).__name__,
    })
    if len(last_errors) > MAX_ERROR_HISTORY:
        last_errors = last_errors[-MAX_ERROR_HISTORY:]
    logger.error(f"Unhandled exception: {exc}")
    return error_response(
        status_code=500,
        message="服务器内部错误",
        error_code="INTERNAL_ERROR",
    )


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    global request_count
    request_count += 1

    client_ip = request.client.host
    path = request.url.path

    if path.startswith("/api"):
        if not limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return error_response(
                status_code=429,
                message="请求过于频繁，请稍后再试",
                error_code="RATE_LIMITED",
            )

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    response.headers["X-Process-Time"] = str(process_time)
    if settings.is_debug:
        logger.info(f"{request.method} {path} - {response.status_code} - {process_time:.3f}s")

    return response


app.include_router(polish_router, prefix="/api/polish", tags=["润色"])
app.include_router(anti_ai_router, prefix="/api/anti-ai", tags=["去AI化"])
app.include_router(upload_router, prefix="/api/upload", tags=["文件上传"])
app.include_router(auth_router, prefix="/api/auth", tags=["用户认证"])
app.include_router(progress_router, prefix="/api/progress", tags=["进度"])


async def check_database() -> dict:
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "type": settings.database_url.split(":")[0]}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_llm() -> dict:
    try:
        from .services.llm_client import llm_client
        if llm_client._client is not None:
            return {"status": "initialized", "model": settings.zhipuai_model}
        return {"status": "not_initialized"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_progress_store() -> dict:
    try:
        pending = sum(1 for t in progress_store.values() if t.get("status") == "processing")
        total = len(progress_store)
        return {"status": "ok", "total_tasks": total, "pending_tasks": pending}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.get("/")
async def root():
    return {
        "name": "论文润色工具",
        "version": "2.1.0",
        "environment": settings.environment,
        "docs": "/docs" if settings.is_debug else None,
    }


@app.get("/health")
async def health_check():
    db_check = await check_database()
    llm_check = check_llm()
    progress_check = check_progress_store()

    checks = {
        "api": {"status": "ok"},
        "database": db_check,
        "llm": llm_check,
        "progress_store": progress_check,
    }

    all_ok = all(
        c.get("status") in ["ok", "initialized"]
        for c in checks.values()
    )

    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/stats")
async def get_stats():
    uptime = time.time() - app_start_time
    llm_check = check_llm()

    return {
        "uptime_seconds": round(uptime, 2),
        "uptime_human": _format_uptime(uptime),
        "requests": {
            "total": request_count,
            "errors": error_count,
            "error_rate": round(error_count / max(request_count, 1) * 100, 2),
        },
        "cache": cache.stats(),
        "rate_limiter": {
            "max_requests": limiter.max_requests,
            "window": limiter.window,
        },
        "progress_store": {
            "total_tasks": len(progress_store),
            "pending": sum(1 for t in progress_store.values() if t.get("status") == "processing"),
            "completed": sum(1 for t in progress_store.values() if t.get("status") == "completed"),
            "failed": sum(1 for t in progress_store.values() if t.get("status") == "failed"),
        },
        "llm": llm_check,
        "config": settings.safe_config,
        "recent_errors": last_errors if settings.is_debug else len(last_errors),
    }


def _format_uptime(seconds: float) -> str:
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    return " ".join(parts) or "< 1m"
