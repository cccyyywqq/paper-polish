import asyncio
from typing import Dict, List
from .ai_service import AIService


class PolishService:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.max_concurrent = 3

    async def comprehensive_polish(
        self, text: str, style: str = "academic", task_id: str = ""
    ) -> Dict:
        polished = await self.ai_service.polish_text(text, style, task_id)
        suggestions = await self.ai_service.get_suggestions(text)

        return {
            "original": text,
            "polished": polished,
            "grammar_corrected": polished,
            "suggestions": suggestions,
        }

    async def batch_polish(
        self, texts: List[str], style: str = "academic", task_id: str = ""
    ) -> List[Dict]:
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def process_one(idx: int, text: str) -> tuple[int, Dict]:
            async with semaphore:
                sub_task_id = f"{task_id}-batch-{idx}" if task_id else ""
                try:
                    result = await self.comprehensive_polish(text, style, sub_task_id)
                    return idx, result
                except Exception as e:
                    return idx, {
                        "original": text,
                        "polished": text,
                        "grammar_corrected": text,
                        "suggestions": [f"处理失败: {str(e)}"],
                    }

        tasks = [process_one(i, text) for i, text in enumerate(texts)]
        results = await asyncio.gather(*tasks)

        results.sort(key=lambda x: x[0])
        return [r[1] for r in results]
