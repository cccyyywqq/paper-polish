from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    path = request.url.path

    if path.startswith("/api"):
        if not limiter.is_allowed(client_ip):
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "请求过于频繁，请稍后再试",
                    "retry_after": limiter.get_reset_time(client_ip),
                },
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
    return {"message": "论文润色工具API", "version": "1.1.0"}


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
