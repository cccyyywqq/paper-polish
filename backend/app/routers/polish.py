import asyncio
from fastapi import APIRouter, HTTPException
from ..schemas.paper import PolishRequest, PolishResponse, BatchPolishRequest, BatchPolishResponse
from ..services.polish_service import PolishService
from ..services.ai_service import AIServiceFactory
from ..utils import logger, split_text
from .progress import create_task, update_progress, set_task_error, set_task_result

router = APIRouter()

MAX_CONCURRENT = 3


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
    asyncio.create_task(_process_polish_concurrent(task_id, request))
    return {"task_id": task_id}


async def _process_polish_concurrent(task_id: str, request: PolishRequest):
    try:
        chunks = split_text(request.text, max_chunk_length=1500)
        total = len(chunks)
        update_progress(task_id, 0, total, "processing")

        ai_service = AIServiceFactory.create_service(request.ai_provider)

        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        completed = [0]

        async def process_chunk(chunk: str, index: int) -> tuple[int, str]:
            async with semaphore:
                try:
                    result = await ai_service.polish_text(chunk, request.style, task_id)
                    completed[0] += 1
                    update_progress(task_id, completed[0], total, "processing", result)
                    return index, result
                except Exception as e:
                    logger.error(f"[{task_id}] Chunk {index} failed: {e}")
                    completed[0] += 1
                    update_progress(task_id, completed[0], total, "processing", chunk)
                    return index, chunk

        tasks = [process_chunk(chunk, i) for i, chunk in enumerate(chunks)]
        results = await asyncio.gather(*tasks)

        results.sort(key=lambda x: x[0])
        final_results = [r[1] for r in results]
        final_result = "\n\n".join(final_results)

        set_task_result(task_id, {
            "original": request.text,
            "polished": final_result,
            "grammar_corrected": final_result,
            "suggestions": [],
            "success": True,
            "message": "润色完成",
        })

    except Exception as e:
        logger.error(f"Polish task {task_id} failed: {e}")
        set_task_error(task_id, str(e))


@router.post("/batch", response_model=BatchPolishResponse)
async def batch_polish(request: BatchPolishRequest):
    try:
        ai_service = AIServiceFactory.create_service(request.ai_provider)
        polish_service = PolishService(ai_service)

        results = await polish_service.batch_polish(request.texts, request.style)
        return BatchPolishResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
