import time
import asyncio
from typing import Dict, Optional
from collections import defaultdict


class RateLimiter:
    def __init__(self, max_requests: int = 10, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests: Dict[str, list] = defaultdict(list)

    def _cleanup(self, key: str):
        current_time = time.time()
        self.requests[key] = [
            t for t in self.requests[key] if current_time - t < self.window
        ]

    def is_allowed(self, key: str = "default") -> bool:
        self._cleanup(key)
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(time.time())
            return True
        return False

    def get_remaining(self, key: str = "default") -> int:
        self._cleanup(key)
        return max(0, self.max_requests - len(self.requests[key]))

    def get_reset_time(self, key: str = "default") -> float:
        if not self.requests[key]:
            return 0
        oldest = min(self.requests[key])
        return max(0, self.window - (time.time() - oldest))


limiter = RateLimiter(max_requests=10, window=60)


async def rate_limit_middleware(request, call_next):
    client_ip = request.client.host
    if not limiter.is_allowed(client_ip):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "retry_after": limiter.get_reset_time(client_ip)},
        )
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(limiter.get_remaining(client_ip))
    return response
