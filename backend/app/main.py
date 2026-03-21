from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time

from .database import init_db
from .routers import polish_router, anti_ai_router, upload_router, auth_router, progress_router
from .utils import logger, limiter, cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down application...")
    cache.clear()


app = FastAPI(
    title="论文润色工具",
    description="AI驱动的论文润色与去AI化处理工具",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def error_response(status_code: int, message: str, error_code: str = None, details: any = None):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "error_code": error_code,
            "details": details,
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
    logger.error(f"Unhandled exception: {exc}")
    return error_response(
        status_code=500,
        message="服务器内部错误",
        error_code="INTERNAL_ERROR",
    )


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
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
    logger.info(f"{request.method} {path} - {response.status_code} - {process_time:.3f}s")

    return response


app.include_router(polish_router, prefix="/api/polish", tags=["润色"])
app.include_router(anti_ai_router, prefix="/api/anti-ai", tags=["去AI化"])
app.include_router(upload_router, prefix="/api/upload", tags=["文件上传"])
app.include_router(auth_router, prefix="/api/auth", tags=["用户认证"])
app.include_router(progress_router, prefix="/api/progress", tags=["进度"])


@app.get("/")
async def root():
    return {"message": "论文润色工具API", "version": "2.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/stats")
async def get_stats():
    return {
        "cache": cache.stats(),
        "rate_limiter": {
            "max_requests": limiter.max_requests,
            "window": limiter.window,
        },
    }
