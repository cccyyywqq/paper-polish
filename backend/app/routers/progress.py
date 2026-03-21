import asyncio
import json
import uuid
from typing import Dict
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from ..utils import logger

router = APIRouter()

progress_store: Dict[str, Dict] = {}


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
    async def event_generator():
        last_progress = -1
        while True:
            if await request.is_disconnected():
                break

            if task_id not in progress_store:
                yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                break

            data = progress_store[task_id]
            if data["progress"] != last_progress:
                yield f"data: {json.dumps(data)}\n\n"
                last_progress = data["progress"]

            if data["status"] in ["completed", "failed"]:
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in progress_store:
        return {"error": "Task not found"}
    return progress_store[task_id]


@router.delete("/cleanup/{task_id}")
async def cleanup_task(task_id: str):
    if task_id in progress_store:
        del progress_store[task_id]
    return {"success": True}
