"""
Base abstract interface for LLM providers (Strategy Pattern).
"""

import threading
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier."""

    @property
    @abstractmethod
    def model(self) -> str:
        """Model identifier."""

    @abstractmethod
    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Executes generation and returns parsed JSON dictionary.
        Must raise an exception if generation or parsing fails.
        """

    @property
    def is_live(self) -> bool:
        """True for providers that call a model; False for the offline keyword engine."""
        return self.name != "heuristic"

    # Token / latency accounting (shared by all adapters; thread-safe).
    def record_usage(self, prompt_tokens: int = 0, completion_tokens: int = 0,
                     reasoning_tokens: int = 0, latency: float = 0.0, cached: bool = False) -> None:
        if not hasattr(self, "_usage_lock"):
            self._usage_lock = threading.Lock()
            self._usage = {"calls": 0, "cache_hits": 0, "prompt_tokens": 0,
                           "completion_tokens": 0, "reasoning_tokens": 0, "latency_s": 0.0,
                           "cached_prompt_tokens": 0, "cached_completion_tokens": 0, "cached_reasoning_tokens": 0}
            self._last_usage = {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0, "latency_s": 0.0}
        with self._usage_lock:
            self._last_usage = {
                "prompt_tokens": int(prompt_tokens or 0),
                "completion_tokens": int(completion_tokens or 0),
                "reasoning_tokens": int(reasoning_tokens or 0),
                "latency_s": float(latency or 0.0),
            }
            if cached:
                self._usage["cache_hits"] += 1
                self._usage["cached_prompt_tokens"] = self._usage.get("cached_prompt_tokens", 0) + int(prompt_tokens or 0)
                self._usage["cached_completion_tokens"] = self._usage.get("cached_completion_tokens", 0) + int(completion_tokens or 0)
                self._usage["cached_reasoning_tokens"] = self._usage.get("cached_reasoning_tokens", 0) + int(reasoning_tokens or 0)
                return
            self._usage["calls"] += 1
            self._usage["prompt_tokens"] += int(prompt_tokens or 0)
            self._usage["completion_tokens"] += int(completion_tokens or 0)
            self._usage["reasoning_tokens"] += int(reasoning_tokens or 0)
            self._usage["latency_s"] += float(latency or 0.0)

    @property
    def last_usage(self) -> Dict[str, Any]:
        return dict(getattr(self, "_last_usage", {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0, "latency_s": 0.0}))

    @property
    def usage(self) -> Dict[str, Any]:
        return dict(getattr(self, "_usage", {"calls": 0, "cache_hits": 0, "prompt_tokens": 0,
                                              "completion_tokens": 0, "reasoning_tokens": 0, "latency_s": 0.0,
                                              "cached_prompt_tokens": 0, "cached_completion_tokens": 0, "cached_reasoning_tokens": 0}))
