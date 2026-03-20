from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers import polish_router, anti_ai_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="论文润色工具",
    description="AI驱动的论文润色与去AI化处理工具",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(polish_router, prefix="/api/polish", tags=["润色"])
app.include_router(anti_ai_router, prefix="/api/anti-ai", tags=["去AI化"])


@app.get("/")
async def root():
    return {"message": "论文润色工具API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
