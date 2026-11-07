"""
Google Gemini provider adapter.
Default model: gemini-3.8-flash
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from src.providers.base import BaseLLMProvider
from src.utils.logging import logger


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
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}
            ],
            "generationConfig": {
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        }

        logger.debug(f"Calling Gemini API with model: {self._model}")
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError(f"Gemini API returned no candidates: {data}")

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise RuntimeError(f"Gemini API returned empty parts: {data}")

        raw_text = parts[0].get("text", "{}")
        return json.loads(raw_text)
