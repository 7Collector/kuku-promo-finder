"""
Anthropic Claude provider adapter.
Default model: claude-sonnet-5-5
"""

import os
import json
import re
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from src.providers.base import BaseLLMProvider
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
            raise ValueError("ANTHROPIC_API_KEY is not configured.")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self._model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "max_tokens": 4096,
            "temperature": 0.2
        }

        logger.debug(f"Calling Anthropic API with model: {self._model}")
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()

        data = resp.json()
        content = data.get("content", [])
        if not content:
            raise RuntimeError(f"Anthropic returned no content: {data}")

        raw_text = content[0].get("text", "{}")
        # Extract JSON block if surrounded by markdown code blocks
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(raw_text)
