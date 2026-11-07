"""
Retry/backoff and on-disk response cache, as wrappers around any BaseLLMProvider.
A re-run with identical prompts costs nothing; a crash mid-run loses nothing already paid for.
"""

import hashlib
import json
import os
import time
from typing import Any, Dict

from src.providers.base import BaseLLMProvider
from src.providers.http import ProviderError
from src.utils.logging import logger


class _Wrapper(BaseLLMProvider):
    def __init__(self, inner: BaseLLMProvider):
        self.inner = inner

    @property
    def name(self) -> str:
        return self.inner.name

    @property
    def model(self) -> str:
        return self.inner.model

    @property
    def usage(self) -> Dict[str, Any]:
        return self.inner.usage

    def record_usage(self, *a, **k):
        return self.inner.record_usage(*a, **k)


class RetryingProvider(_Wrapper):
    def __init__(self, inner: BaseLLMProvider, attempts: int = 4, base_delay: float = 2.0):
        super().__init__(inner)
        self.attempts = attempts
        self.base_delay = base_delay

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        last: Exception = RuntimeError("no attempts made")
        for i in range(self.attempts):
            try:
                return self.inner.generate_json(system_prompt, user_prompt)
            except ProviderError as e:
                last = e
                if not e.retryable or i == self.attempts - 1:
                    raise
                delay = self.base_delay * (2 ** i)
                logger.warning(f"{self.name} call failed ({e}); retry {i + 1}/{self.attempts - 1} in {delay:.0f}s")
                time.sleep(delay)
        raise last


class CachedProvider(_Wrapper):
    def __init__(self, inner: BaseLLMProvider, cache_dir: str = ".cache/kuku"):
        super().__init__(inner)
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _path(self, system_prompt: str, user_prompt: str) -> str:
        key = hashlib.sha256(
            json.dumps([self.name, self.model, system_prompt, user_prompt]).encode("utf-8")
        ).hexdigest()
        return os.path.join(self.cache_dir, f"{key}.json")

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        path = self._path(system_prompt, user_prompt)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    value = json.load(f)
                self.inner.record_usage(cached=True)
                return value
            except ValueError:
                pass
        value = self.inner.generate_json(system_prompt, user_prompt)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(value, f)
        os.replace(tmp, path)
        return value
