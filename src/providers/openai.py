"""
OpenAI provider adapter.
Default model: gpt-6-luna
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from src.providers.base import BaseLLMProvider
from src.providers.http import post_json, extract_json_object, ProviderError
from src.utils.logging import logger

load_dotenv()


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model: Optional[str] = None):
        self._model = model or os.getenv("OPENAI_MODEL") or "gpt-6-luna"
        self.api_key = os.getenv("OPENAI_API_KEY")

    @property
    def name(self) -> str:
        return "openai"

    @property
    def model(self) -> str:
        return self._model

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        if not self.api_key:
            raise ProviderError("OPENAI_API_KEY is not configured.")

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        # Reasoning models only accept the default temperature.
        is_reasoning_model = any(k in self._model.lower() for k in ["gpt-6", "luna", "o1", "o3", "o4", "sol", "astra"])
        if not is_reasoning_model:
            payload["temperature"] = 0.2

        logger.debug(f"Calling OpenAI API with model: {self._model}")
        data, latency = post_json(
            "https://api.openai.com/v1/chat/completions",
            {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
            payload, timeout=180, secret=self.api_key,
        )
        usage = data.get("usage", {})
        self.record_usage(
            usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0),
            (usage.get("completion_tokens_details") or {}).get("reasoning_tokens", 0), latency,
        )
        choices = data.get("choices", [])
        if not choices:
            raise ProviderError("OpenAI returned no choices", retryable=True)
        return extract_json_object(choices[0]["message"]["content"])
