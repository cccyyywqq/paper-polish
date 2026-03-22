import asyncio
import hashlib
import time
import uuid
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from zhipuai import ZhipuAI
from ..config import get_settings
from ..utils import logger

settings = get_settings()


@dataclass
class LLMRequest:
    messages: List[Dict[str, str]]
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 4000
    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    task_id: str = ""


@dataclass
class LLMResponse:
    content: str
    request_id: str
    task_id: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    latency_ms: int = 0
    cached: bool = False


class LLMCache:
    def __init__(self, max_size: int = 200, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, Dict] = {}
        self._access_order: List[str] = []

    def _make_key(self, messages: List[Dict], model: str, temperature: float) -> str:
        content = f"{model}:{temperature}:{str(messages)}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, messages: List[Dict], model: str, temperature: float) -> Optional[str]:
        key = self._make_key(messages, model, temperature)
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                self._access_order.remove(key)
                self._access_order.append(key)
                return entry["content"]
            else:
                del self._cache[key]
                self._access_order.remove(key)
        return None

    def set(self, messages: List[Dict], model: str, temperature: float, content: str):
        key = self._make_key(messages, model, temperature)
        if len(self._cache) >= self.max_size:
            oldest = self._access_order.pop(0)
            del self._cache[oldest]
        self._cache[key] = {"content": content, "timestamp": time.time()}
        self._access_order.append(key)

    def stats(self) -> Dict:
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
        }


class LLMClient:
    def __init__(self):
        self._client: Optional[ZhipuAI] = None
        self._cache = LLMCache(max_size=200, ttl=3600)
        self._max_retries = settings.llm_max_retries
        self._timeout = settings.llm_timeout

    @property
    def client(self) -> ZhipuAI:
        if self._client is None:
            self._client = ZhipuAI(api_key=settings.zhipuai_api_key)
        return self._client

    def _select_model(self, text_length: int) -> str:
        if text_length > 5000:
            return "glm-4"
        return settings.zhipuai_model

    async def invoke(
        self,
        messages: List[Dict[str, str]],
        model: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        request_id: str = "",
        task_id: str = "",
        use_cache: bool = True,
    ) -> LLMResponse:
        if not model:
            text_len = len(str(messages))
            model = self._select_model(text_len)

        request_id = request_id or str(uuid.uuid4())[:8]
        log_prefix = f"[LLM][{request_id}][{task_id}]" if task_id else f"[LLM][{request_id}]"

        logger.info(f"{log_prefix} Request start: model={model}, msgs={len(messages)}")

        if use_cache:
            cached = self._cache.get(messages, model, temperature)
            if cached:
                logger.info(f"{log_prefix} Cache hit")
                return LLMResponse(
                    content=cached,
                    request_id=request_id,
                    task_id=task_id,
                    model=model,
                    cached=True,
                )

        last_error = None
        for attempt in range(self._max_retries):
            try:
                start_time = time.time()
                loop = asyncio.get_event_loop()

                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: self.client.chat.completions.create(
                            model=model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        ),
                    ),
                    timeout=self._timeout,
                )

                latency_ms = int((time.time() - start_time) * 1000)
                content = response.choices[0].message.content

                if use_cache:
                    self._cache.set(messages, model, temperature, content)

                usage = {}
                if hasattr(response, "usage") and response.usage:
                    usage = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }

                logger.info(
                    f"{log_prefix} Success: latency={latency_ms}ms, "
                    f"tokens={usage.get('total_tokens', '?')}, attempt={attempt + 1}"
                )

                return LLMResponse(
                    content=content,
                    request_id=request_id,
                    task_id=task_id,
                    model=model,
                    usage=usage,
                    latency_ms=latency_ms,
                )

            except asyncio.TimeoutError:
                last_error = Exception(f"请求超时 ({self._timeout}s)")
                wait_time = 2 ** attempt
                logger.warning(
                    f"{log_prefix} Timeout after {self._timeout}s, attempt {attempt + 1}/{self._max_retries}"
                )
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(wait_time)

            except Exception as e:
                last_error = e
                wait_time = 2 ** attempt
                logger.warning(
                    f"{log_prefix} Attempt {attempt + 1}/{self._max_retries} failed: {e}. "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(wait_time)

        logger.error(f"{log_prefix} All {self._max_retries} attempts failed: {last_error}")
        raise last_error


llm_client = LLMClient()


async def invoke_llm(
    messages: List[Dict[str, str]],
    model: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4000,
    request_id: str = "",
    task_id: str = "",
    use_cache: bool = True,
) -> LLMResponse:
    return await llm_client.invoke(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        request_id=request_id,
        task_id=task_id,
        use_cache=use_cache,
    )
