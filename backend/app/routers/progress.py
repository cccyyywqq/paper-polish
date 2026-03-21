import asyncio
import json
import uuid
import time
from typing import Dict, Optional, Any, List
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..utils import logger

router = APIRouter()

progress_store: Dict[str, Dict] = {}
TASK_TTL = 600  # 10 minutes
cleanup_started = False


class ProgressStatus(BaseModel):
    progress: int = 0
    total: int = 0
    status: str = "pending"
    results: List[str] = []
    result: Optional[Any] = None
    error: Optional[str] = None


class TaskResponse(BaseModel):
    task_id: str
    message: str = "任务已创建"


class CleanupResponse(BaseModel):
    success: bool = True
    message: str = "任务已清理"


def create_task() -> str:
    task_id = str(uuid.uuid4())
    progress_store[task_id] = {
        "progress": 0,
        "total": 0,
        "status": "pending",
        "results": [],
        "created_at": time.time(),
    }
    _ensure_cleanup_task()
    return task_id


def update_progress(
    task_id: str,
    progress: int,
    total: int,
    status: str = "processing",
    result: str = None,
):
    if task_id in progress_store:
        progress_store[task_id]["progress"] = progress
        progress_store[task_id]["total"] = total
        progress_store[task_id]["status"] = status
        progress_store[task_id]["updated_at"] = time.time()
        if result:
            progress_store[task_id]["results"].append(result)


def cleanup_expired_tasks():
    now = time.time()
    expired = [
        task_id
        for task_id, data in progress_store.items()
        if now - data.get("created_at", now) > TASK_TTL
    ]
    for task_id in expired:
        del progress_store[task_id]
        logger.info(f"Cleaned up expired task: {task_id}")
    return len(expired)


async def _periodic_cleanup():
    while True:
        await asyncio.sleep(60)
        cleaned = cleanup_expired_tasks()
        if cleaned > 0:
            logger.info(f"Periodic cleanup removed {cleaned} expired tasks")


def _ensure_cleanup_task():
    global cleanup_started
    if not cleanup_started:
        cleanup_started = True
        try:
            asyncio.get_event_loop().create_task(_periodic_cleanup())
        except RuntimeError:
            pass


@router.get("/stream/{task_id}")
async def stream_progress(task_id: str, request: Request):
    if task_id not in progress_store:
        raise HTTPException(status_code=404, detail="任务不存在")

    async def event_generator():
        last_progress = -1
        while True:
            if await request.is_disconnected():
                break

            if task_id not in progress_store:
                yield f"data: {json.dumps({'error': '任务不存在或已过期'})}\n\n"
                break

            data = progress_store[task_id]
            if data["progress"] != last_progress:
                yield f"data: {json.dumps(data)}\n\n"
                last_progress = data["progress"]

            if data["status"] in ["completed", "failed"]:
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/status/{task_id}", response_model=ProgressStatus)
async def get_status(task_id: str):
    if task_id not in progress_store:
        raise HTTPException(status_code=404, detail="任务不存在或已过期")
    return ProgressStatus(**progress_store[task_id])


@router.delete("/cleanup/{task_id}", response_model=CleanupResponse)
async def cleanup_task(task_id: str):
    if task_id in progress_store:
        del progress_store[task_id]
        logger.info(f"Task cleaned up: {task_id}")
    return CleanupResponse(message="任务已清理")


@router.post("/cleanup-all", response_model=CleanupResponse)
async def cleanup_all_tasks():
    count = len(progress_store)
    progress_store.clear()
    logger.info(f"All {count} tasks cleaned up")
    return CleanupResponse(message=f"已清理 {count} 个任务")
