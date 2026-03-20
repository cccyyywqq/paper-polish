from fastapi import APIRouter, HTTPException
from ..schemas.paper import PolishRequest, PolishResponse
from ..services.polish_service import PolishService
from ..services.ai_service import AIServiceFactory

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


@router.post("/batch")
async def batch_polish(texts: list[str], style: str = "academic", ai_provider: str = "zhipuai"):
    try:
        ai_service = AIServiceFactory.create_service(ai_provider)
        polish_service = PolishService(ai_service)

        results = await polish_service.batch_polish(texts, style)
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
