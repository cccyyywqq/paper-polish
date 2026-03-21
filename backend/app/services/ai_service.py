from abc import ABC, abstractmethod
from typing import List
import asyncio
import os
import httpx
from zhipuai import ZhipuAI
from ..config import get_settings
from ..utils import logger, retry, split_text, merge_results

settings = get_settings()


class AIService(ABC):
    @abstractmethod
    async def polish_text(self, text: str, style: str = "academic") -> str:
        pass

    @abstractmethod
    async def anti_ai_detection(self, text: str) -> str:
        pass

    @abstractmethod
    async def get_suggestions(self, text: str) -> List[str]:
        pass


def create_zhipuai_client():
    api_key = settings.zhipuai_api_key
    if not api_key:
        raise ValueError("ZHIPUAI_API_KEY is not configured")

    http_client = httpx.Client(transport=httpx.HTTPTransport())
    return ZhipuAI(api_key=api_key, http_client=http_client)


class ZhipuAIService(AIService):
    def __init__(self):
        self.client = create_zhipuai_client()
        self.model = settings.zhipuai_model

    def _select_model(self, text: str) -> str:
        if len(text) > 5000:
            return "glm-4"
        return self.model

    def _polish_chunk(self, text: str, style: str = "academic") -> str:
        prompts = {
            "academic": "你是一位专业的学术论文编辑。请将以下文本润色为严谨的学术论文风格，保持原意但提升表达质量和专业性：",
            "natural": "你是一位优秀的写作助手。请将以下文本润色得更自然流畅，增加可读性，同时保持学术性：",
            "formal": "你是一位学术写作专家。请将以下文本润色为正式的学术风格，使用专业术语和规范表达：",
        }

        model = self._select_model(text)

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompts.get(style, prompts["academic"])},
                {"role": "user", "content": text},
            ],
            temperature=0.7,
            max_tokens=4000,
        )

        return response.choices[0].message.content

    def _anti_ai_chunk(self, text: str) -> str:
        model = self._select_model(text)

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """请将以下文本改写，使其不被AI检测工具识别，同时保持学术性和准确性：""",
                },
                {"role": "user", "content": text},
            ],
            temperature=0.8,
            max_tokens=4000,
        )

        return response.choices[0].message.content

    async def polish_text(self, text: str, style: str = "academic") -> str:
        chunks = split_text(text, max_chunk_length=1500)
        logger.info(f"Split text into {len(chunks)} chunks for polishing")

        if len(chunks) == 1:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._polish_chunk, text, style)
            return result

        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(None, self._polish_chunk, chunk, style)
            for chunk in chunks
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Chunk {i} failed: {result}")
                final_results.append(chunks[i])
            else:
                final_results.append(result)

        return merge_results(final_results, chunks)

    async def anti_ai_detection(self, text: str) -> str:
        chunks = split_text(text, max_chunk_length=1500)
        logger.info(f"Split text into {len(chunks)} chunks for anti-AI processing")

        if len(chunks) == 1:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._anti_ai_chunk, text)
            return result

        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(None, self._anti_ai_chunk, chunk)
            for chunk in chunks
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Chunk {i} failed: {result}")
                final_results.append(chunks[i])
            else:
                final_results.append(result)

        return merge_results(final_results, chunks)

    async def get_suggestions(self, text: str) -> List[str]:
        loop = asyncio.get_event_loop()

        def _get_suggestions():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """请分析以下学术文本，提供3-5条具体的改进建议，每条建议不超过50字：""",
                    },
                    {"role": "user", "content": text[:2000]},
                ],
                temperature=0.5,
                max_tokens=1000,
            )
            content = response.choices[0].message.content
            return [s.strip() for s in content.split("\n") if s.strip()][:5]

        return await loop.run_in_executor(None, _get_suggestions)


class LocalModelService(AIService):
    def __init__(self):
        self.available = False

    async def polish_text(self, text: str, style: str = "academic") -> str:
        logger.warning("Local model not available")
        return text

    async def anti_ai_detection(self, text: str) -> str:
        logger.warning("Local model not available")
        return text

    async def get_suggestions(self, text: str) -> List[str]:
        return ["本地模型暂未配置"]


class AIServiceFactory:
    @staticmethod
    def create_service(provider: str = "zhipuai") -> AIService:
        logger.info(f"Creating AI service: {provider}")
        if provider == "zhipuai":
            return ZhipuAIService()
        elif provider == "local":
            return LocalModelService()
        else:
            raise ValueError(f"不支持的AI服务: {provider}")
