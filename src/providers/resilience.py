"""
Retry/backoff and on-disk response cache, as wrappers around any BaseLLMProvider.
A re-run with identical prompts costs nothing; a crash mid-run loses nothing already paid for.
"""

import hashlib
import json
import os
import time
from typing import Any, Dict, Tuple

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

    @property
    def last_usage(self) -> Dict[str, Any]:
        return self.inner.last_usage

    def record_usage(self, *a, **k):
        return self.inner.record_usage(*a, **k)


class RetryingProvider(_Wrapper):
    def __init__(self, inner: BaseLLMProvider, attempts: int = 8, base_delay: float = 5.0):
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
                # Malformed JSON check: on malformed JSON retry once, then raise
                is_json_err = "JSON" in str(e) or "json" in str(e)
                if is_json_err and i >= 1:
                    raise
                if not e.retryable or i == self.attempts - 1:
                    raise
                retry_after = getattr(e, "retry_after", None)
                delay = max(retry_after or 0.0, self.base_delay * (2 ** i))
                logger.warning(f"{self.name} call failed ({e}); retry {i + 1}/{self.attempts - 1} in {delay:.1f}s")
                time.sleep(delay)
        raise last


class CachedProvider(_Wrapper):
    def __init__(self, inner: BaseLLMProvider, cache_dir: str = ".cache/kuku"):
        super().__init__(inner)
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _keys(self, system_prompt: str, user_prompt: str) -> Tuple[str, str, str]:
        prompt_full = f"{system_prompt}\n---\n{user_prompt}"
        prompt_hash = hashlib.sha256(prompt_full.encode("utf-8")).hexdigest()
        new_key = f"{self.name}_{self.model}_{prompt_hash}"
        legacy_key = hashlib.sha256(
            json.dumps([self.name, self.model, system_prompt, user_prompt]).encode("utf-8")
        ).hexdigest()
        return new_key, legacy_key, prompt_hash

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        new_key, legacy_key, prompt_hash = self._keys(system_prompt, user_prompt)
        new_path = os.path.join(self.cache_dir, f"{new_key}.json")
        legacy_path = os.path.join(self.cache_dir, f"{legacy_key}.json")

        for path in (new_path, legacy_path):
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        entry = json.load(f)
                    if isinstance(entry, dict) and "response" in entry and "usage" in entry:
                        val = entry["response"]
                        u = entry.get("usage", {})
                        self.inner.record_usage(
                            prompt_tokens=u.get("prompt_tokens", 0),
                            completion_tokens=u.get("completion_tokens", 0),
                            reasoning_tokens=u.get("reasoning_tokens", 0),
                            latency=u.get("latency_s", 0.0),
                            cached=True,
                        )
                    else:
                        val = entry
                        self.inner.record_usage(cached=True)
                    return val
                except ValueError:
                    pass

        value = self.inner.generate_json(system_prompt, user_prompt)
        usage = getattr(self.inner, "last_usage", {})
        cache_entry = {
            "provider": self.name,
            "model": self.model,
            "prompt_hash": prompt_hash,
            "response": value,
            "usage": usage,
        }
        tmp = new_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cache_entry, f)
        os.replace(tmp, new_path)
        return value
