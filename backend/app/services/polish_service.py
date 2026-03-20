from typing import Dict, List
from .ai_service import AIService


class PolishService:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    async def comprehensive_polish(self, text: str, style: str = "academic") -> Dict:
        polished = await self.ai_service.polish_text(text, style)
        suggestions = await self.ai_service.get_suggestions(text)

        return {
            "original": text,
            "polished": polished,
            "grammar_corrected": polished,
            "suggestions": suggestions,
        }

    async def batch_polish(self, texts: List[str], style: str = "academic") -> List[Dict]:
        results = []
        for text in texts:
            result = await self.comprehensive_polish(text, style)
            results.append(result)
        return results
