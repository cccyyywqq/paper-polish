from abc import ABC, abstractmethod
from typing import List
import asyncio
import uuid
from .llm_client import invoke_llm, LLMResponse
from ..config import get_settings
from ..utils import logger, split_text, merge_results

settings = get_settings()


class AIService(ABC):
    @abstractmethod
    async def polish_text(
        self, text: str, style: str = "academic", task_id: str = ""
    ) -> str:
        pass

    @abstractmethod
    async def anti_ai_detection(self, text: str, task_id: str = "") -> str:
        pass

    @abstractmethod
    async def get_suggestions(self, text: str) -> List[str]:
        pass


PROMPTS = {
    "academic": "你是一位专业的学术论文编辑。请将以下文本润色为严谨的学术论文风格，保持原意但提升表达质量和专业性：",
    "natural": "你是一位优秀的写作助手。请将以下文本润色得更自然流畅，增加可读性，同时保持学术性：",
    "formal": "你是一位学术写作专家。请将以下文本润色为正式的学术风格，使用专业术语和规范表达：",
}

ANTI_AI_PROMPT = """请将以下文本改写，使其：
1. 不被AI检测工具识别为AI生成
2. 保持学术性和准确性
3. 增加个人表达和独特视角
4. 调整句式结构，避免AI常见模式
5. 使用多样化的句式开头
6. 保持逻辑连贯性和专业性"""


class ZhipuAIService(AIService):
    def __init__(self):
        self.max_concurrent = settings.llm_max_concurrent

    async def _call_llm(
        self,
        text: str,
        system_prompt: str,
        temperature: float = 0.7,
        request_id: str = "",
        task_id: str = "",
    ) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ]
        response = await invoke_llm(
            messages=messages,
            temperature=temperature,
            request_id=request_id,
            task_id=task_id,
        )
        return response.content

    async def polish_text(
        self, text: str, style: str = "academic", task_id: str = ""
    ) -> str:
        chunks = split_text(text, max_chunk_length=1500)
        logger.info(f"[{task_id}] Split into {len(chunks)} chunks for polishing")

        if len(chunks) == 1:
            request_id = str(uuid.uuid4())[:8]
            return await self._call_llm(
                text,
                PROMPTS.get(style, PROMPTS["academic"]),
                temperature=0.7,
                request_id=request_id,
                task_id=task_id,
            )

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def process_chunk(chunk: str, index: int) -> tuple[int, str]:
            async with semaphore:
                request_id = f"{task_id}-{index}"
                try:
                    result = await self._call_llm(
                        chunk,
                        PROMPTS.get(style, PROMPTS["academic"]),
                        temperature=0.7,
                        request_id=request_id,
                        task_id=task_id,
                    )
                    return index, result
                except Exception as e:
                    logger.error(f"[{task_id}] Chunk {index} failed: {e}")
                    return index, chunk

        tasks = [process_chunk(chunk, i) for i, chunk in enumerate(chunks)]
        results = await asyncio.gather(*tasks)

        results.sort(key=lambda x: x[0])
        final_results = [r[1] for r in results]

        return merge_results(final_results, chunks)

    async def anti_ai_detection(self, text: str, task_id: str = "") -> str:
        chunks = split_text(text, max_chunk_length=1500)
        logger.info(f"[{task_id}] Split into {len(chunks)} chunks for anti-AI")

        if len(chunks) == 1:
            request_id = str(uuid.uuid4())[:8]
            return await self._call_llm(
                text,
                ANTI_AI_PROMPT,
                temperature=0.8,
                request_id=request_id,
                task_id=task_id,
            )

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def process_chunk(chunk: str, index: int) -> tuple[int, str]:
            async with semaphore:
                request_id = f"{task_id}-{index}"
                try:
                    result = await self._call_llm(
                        chunk,
                        ANTI_AI_PROMPT,
                        temperature=0.8,
                        request_id=request_id,
                        task_id=task_id,
                    )
                    return index, result
                except Exception as e:
                    logger.error(f"[{task_id}] Chunk {index} failed: {e}")
                    return index, chunk

        tasks = [process_chunk(chunk, i) for i, chunk in enumerate(chunks)]
        results = await asyncio.gather(*tasks)

        results.sort(key=lambda x: x[0])
        final_results = [r[1] for r in results]

        return merge_results(final_results, chunks)

    async def get_suggestions(self, text: str) -> List[str]:
        request_id = str(uuid.uuid4())[:8]
        response = await self._call_llm(
            text[:2000],
            "请分析以下学术文本，提供3-5条具体的改进建议，每条建议不超过50字，以列表形式返回：",
            temperature=0.5,
            request_id=request_id,
        )
        return [s.strip() for s in response.split("\n") if s.strip()][:5]


class LocalModelService(AIService):
    available = False

    async def polish_text(
        self, text: str, style: str = "academic", task_id: str = ""
    ) -> str:
        raise NotImplementedError("本地模型暂未配置，请使用智谱GLM-4")

    async def anti_ai_detection(self, text: str, task_id: str = "") -> str:
        raise NotImplementedError("本地模型暂未配置，请使用智谱GLM-4")

    async def get_suggestions(self, text: str) -> List[str]:
        raise NotImplementedError("本地模型暂未配置，请使用智谱GLM-4")


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
