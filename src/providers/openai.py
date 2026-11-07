"""
OpenAI provider adapter.
Default model: gpt-6-luna
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from src.providers.base import BaseLLMProvider
from src.utils.logging import logger


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
            raise ValueError("OPENAI_API_KEY is not configured.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        logger.debug(f"Calling OpenAI API with model: {self._model}")
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()

        data = resp.json()
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError(f"OpenAI API returned no choices: {data}")

        raw_text = choices[0]["message"]["content"]
        return json.loads(raw_text)
