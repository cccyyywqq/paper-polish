from typing import Dict, List
import re
from .ai_service import AIService


class AntiAIService:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    async def process_text(self, text: str, task_id: str = "") -> Dict:
        processed = await self.ai_service.anti_ai_detection(text, task_id)
        suggestions = await self.ai_service.get_suggestions(text)
        naturalness = self._calculate_naturalness(processed)
        ai_risk = self._estimate_ai_risk(processed)

        return {
            "original": text,
            "processed": processed,
            "naturalness_score": naturalness,
            "ai_detection_risk": ai_risk,
            "suggestions": suggestions,
        }

    def _calculate_naturalness(self, text: str) -> float:
        score = 70.0

        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s for s in sentences if s.strip()]
        if not sentences:
            return score

        avg_length = sum(len(s) for s in sentences) / len(sentences)
        if 20 <= avg_length <= 100:
            score += 10

        unique_words = set(text.split())
        total_words = text.split()
        if total_words:
            diversity = len(unique_words) / len(total_words)
            score += diversity * 20

        return min(100.0, max(0.0, score))

    def _estimate_ai_risk(self, text: str) -> float:
        risk = 30.0

        ai_patterns = [
            r'首先，.*其次，.*最后',
            r'总之',
            r'综上所述',
            r'值得注意的是',
            r'需要指出的是',
            r'此外，',
            r'另外，',
        ]

        pattern_count = sum(
            len(re.findall(p, text, re.IGNORECASE)) for p in ai_patterns
        )
        risk += pattern_count * 10

        sentences = re.split(r'[。！？.!?]', text)
        sentences = [s for s in sentences if s.strip()]
        if len(sentences) > 3:
            lengths = [len(s) for s in sentences]
            length_variance = max(lengths) - min(lengths)
            if length_variance < 20:
                risk += 15

        return min(100.0, max(0.0, risk))
