import asyncio
from fastapi import APIRouter, HTTPException
from ..schemas.paper import PolishRequest, PolishResponse, BatchPolishRequest, BatchPolishResponse
from ..services.polish_service import PolishService
from ..services.ai_service import AIServiceFactory
from ..utils import logger, split_text
from .progress import create_task, update_progress

router = APIRouter()


@router.post("/text", response_model=PolishResponse)
async def polish_text(request: PolishRequest):
    try:
        ai_service = AIServiceFactory.create_service(request.ai_provider)
        polish_service = PolishService(ai_service)

        result = await polish_service.comprehensive_polish(request.text, request.style)
        return PolishResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text-with-progress")
async def polish_text_with_progress(request: PolishRequest):
    task_id = create_task()

    asyncio.create_task(_process_polish(task_id, request))

    return {"task_id": task_id}


async def _process_polish(task_id: str, request: PolishRequest):
    try:
        chunks = split_text(request.text, max_chunk_length=1500)
        update_progress(task_id, 0, len(chunks), "processing")

        ai_service = AIServiceFactory.create_service(request.ai_provider)
        polish_service = PolishService(ai_service)

        results = []
        for i, chunk in enumerate(chunks):
            result = await ai_service.polish_text(chunk, request.style)
            results.append(result)
            update_progress(task_id, i + 1, len(chunks), "processing", result)

        final_result = "\n\n".join(results)
        update_progress(task_id, len(chunks), len(chunks), "completed")

        from .progress import progress_store
        progress_store[task_id]["result"] = {
            "original": request.text,
            "polished": final_result,
            "grammar_corrected": final_result,
            "suggestions": [],
            "success": True,
            "message": "润色完成",
        }
    except Exception as e:
        logger.error(f"Polish task failed: {e}")
        update_progress(task_id, 0, 0, "failed")


@router.post("/batch", response_model=BatchPolishResponse)
async def batch_polish(request: BatchPolishRequest):
    try:
        ai_service = AIServiceFactory.create_service(request.ai_provider)
        polish_service = PolishService(ai_service)

        results = await polish_service.batch_polish(request.texts, request.style)
        return BatchPolishResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
