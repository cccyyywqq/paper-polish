from fastapi import APIRouter, HTTPException
from ..schemas.paper import AntiAIRequest, AntiAIResponse
from ..services.anti_ai_service import AntiAIService
from ..services.ai_service import AIServiceFactory

router = APIRouter()


@router.post("/process", response_model=AntiAIResponse)
async def anti_ai_process(request: AntiAIRequest):
    try:
        ai_service = AIServiceFactory.create_service(request.ai_provider)
        anti_ai_service = AntiAIService(ai_service)

        result = await anti_ai_service.process_text(request.text)
        return AntiAIResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_ai_risk(text: str):
    try:
        anti_ai_service = AntiAIService(AIServiceFactory.create_service("zhipuai"))
        risk = anti_ai_service._estimate_ai_risk(text)
        naturalness = anti_ai_service._calculate_naturalness(text)

        return {
            "ai_detection_risk": risk,
            "naturalness_score": naturalness,
            "risk_level": "high" if risk > 60 else "medium" if risk > 30 else "low",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
