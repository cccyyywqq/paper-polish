from typing import Any, Optional, Callable
import hashlib
import time
import asyncio
from functools import wraps


class LRUCache:
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = {}
        self.access_order = []

    def _generate_key(self, text: str, operation: str, **kwargs) -> str:
        content = f"{operation}:{text}:{sorted(kwargs.items())}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                self.access_order.remove(key)
                self.access_order.append(key)
                return entry["value"]
            else:
                del self.cache[key]
                self.access_order.remove(key)
        return None

    def set(self, key: str, value: Any):
        if len(self.cache) >= self.max_size:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]

        self.cache[key] = {"value": value, "timestamp": time.time()}
        self.access_order.append(key)

    def clear(self):
        self.cache.clear()
        self.access_order.clear()

    def stats(self) -> dict:
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
        }


cache = LRUCache(max_size=100, ttl=3600)


def cached(ttl: int = 3600, key_prefix: str = ""):
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
