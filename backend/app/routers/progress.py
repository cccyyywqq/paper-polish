import asyncio
import json
import uuid
from typing import Dict, Optional, Any, List
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ..utils import logger

router = APIRouter()

progress_store: Dict[str, Dict] = {}


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
    progress_store[task_id] = {"progress": 0, "total": 0, "status": "pending", "results": []}
    return task_id


def update_progress(task_id: str, progress: int, total: int, status: str = "processing", result: str = None):
    if task_id in progress_store:
        progress_store[task_id]["progress"] = progress
        progress_store[task_id]["total"] = total
        progress_store[task_id]["status"] = status
        if result:
            progress_store[task_id]["results"].append(result)


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
                yield f"data: {json.dumps({'error': '任务不存在'})}\n\n"
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
        raise HTTPException(status_code=404, detail="任务不存在")
    return ProgressStatus(**progress_store[task_id])


@router.delete("/cleanup/{task_id}", response_model=CleanupResponse)
async def cleanup_task(task_id: str):
    if task_id in progress_store:
        del progress_store[task_id]
    return CleanupResponse()
