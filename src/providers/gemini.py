"""
Google Gemini provider adapter.
Default model: gemini-3.8-flash
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from src.providers.base import BaseLLMProvider
from src.providers.http import post_json, extract_json_object, ProviderError
from src.utils.logging import logger

load_dotenv()


class GeminiProvider(BaseLLMProvider):
    def __init__(self, model: Optional[str] = None):
        self._model = model or os.getenv("GEMINI_MODEL") or "gemini-3.8-flash"
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def model(self) -> str:
        return self._model

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        if not self.api_key:
            raise ProviderError("GEMINI_API_KEY or GOOGLE_API_KEY is not configured.")

        # The key travels in a header, never in the URL, so it cannot appear in logs or tracebacks.
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent"
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
        }
        logger.debug(f"Calling Gemini API with model: {self._model}")
        data, latency = post_json(
            url, {"Content-Type": "application/json", "x-goog-api-key": self.api_key},
            payload, timeout=180, secret=self.api_key,
        )
        meta = data.get("usageMetadata", {})
        self.record_usage(
            meta.get("promptTokenCount", 0),
            meta.get("candidatesTokenCount", 0) + meta.get("thoughtsTokenCount", 0),
            meta.get("thoughtsTokenCount", 0), latency,
        )
        candidates = data.get("candidates", [])
        parts = (candidates[0].get("content", {}).get("parts", []) if candidates else [])
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        if not text:
            raise ProviderError("Gemini returned no text", retryable=True)
        return extract_json_object(text)
