"""
Anthropic Claude provider adapter.
Default model: claude-sonnet-5-5

Sampling parameters (temperature/top_p/top_k) are deliberately not sent: the Claude 5
models reject them with HTTP 400.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from src.providers.base import BaseLLMProvider
from src.providers.http import post_json, extract_json_object, ProviderError
from src.utils.logging import logger

load_dotenv()


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, model: Optional[str] = None):
        self._model = model or os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-5-5"
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def model(self) -> str:
        return self._model

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        if not self.api_key:
            raise ProviderError("ANTHROPIC_API_KEY is not configured.")

        payload = {
            "model": self._model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "max_tokens": 16000,
        }
        logger.debug(f"Calling Anthropic API with model: {self._model}")
        data, latency = post_json(
            "https://api.anthropic.com/v1/messages",
            {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            payload, timeout=300, secret=self.api_key,
        )
        usage = data.get("usage", {})
        self.record_usage(usage.get("input_tokens", 0), usage.get("output_tokens", 0), 0, latency)
        # With thinking enabled the first block may be a thinking block; join only text blocks.
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        if not text:
            raise ProviderError("Anthropic returned no text block", retryable=True)
        return extract_json_object(text)
