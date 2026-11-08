"""
Google Gemini provider adapter.
Default model: gemini-3.8-flash
"""

import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from src.providers.base import BaseLLMProvider
from src.providers.http import post_json, extract_json_object, ProviderError
from src.utils.logging import logger

load_dotenv()

_DISCOVERED_GEMINI_MODEL: Optional[str] = None


def discover_gemini_flash_model(api_key: Optional[str] = None) -> str:
    """
    Calls the Gemini list-models endpoint with the configured key,
    filtering to generateContent models, and picking an available flash-class model.
    On 404, reports; does not guess another ID.
    """
    global _DISCOVERED_GEMINI_MODEL
    if _DISCOVERED_GEMINI_MODEL:
        return _DISCOVERED_GEMINI_MODEL

    key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ProviderError("GEMINI_API_KEY or GOOGLE_API_KEY is not configured.")

    url = "https://generativelanguage.googleapis.com/v1beta/models"
    try:
        resp = requests.get(url, headers={"x-goog-api-key": key}, timeout=15)
    except Exception as e:
        raise ProviderError(f"Failed to query Gemini list-models: {type(e).__name__}: {e}", retryable=True)

    if resp.status_code == 404:
        raise ProviderError(f"Gemini list-models endpoint returned HTTP 404: {resp.text[:200]}", status=404)
    if resp.status_code >= 400:
        raise ProviderError(f"Gemini list-models failed with HTTP {resp.status_code}: {resp.text[:200]}", status=resp.status_code)

    models_data = resp.json().get("models", [])
    content_models = [
        m.get("name", "") for m in models_data
        if "generateContent" in (m.get("supportedGenerationMethods") or [])
    ]
    flash_models = [
        m for m in content_models
        if "flash" in m.lower() and not any(x in m.lower() for x in ("tts", "image", "audio"))
    ]
    if not flash_models:
        raise ProviderError("No flash-class generateContent model available on configured Gemini key")

    chosen = None
    for pref in ("models/gemini-2.5-flash-lite", "models/gemini-3.5-flash-lite", "models/gemini-flash-lite-latest", "models/gemini-3.5-flash", "models/gemini-2.5-flash"):
        if pref in flash_models:
            m_id = pref.replace("models/", "")
            try:
                probe_url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_id}:generateContent"
                p_resp = requests.post(probe_url, headers={"x-goog-api-key": key}, json={"contents": [{"parts": [{"text": "ping"}]}]}, timeout=5)
                if p_resp.status_code == 200:
                    chosen = pref
                    break
            except Exception:
                continue
    if not chosen:
        chosen = flash_models[0]

    _DISCOVERED_GEMINI_MODEL = chosen.replace("models/", "")
    logger.info(f"Discovered Gemini flash-class model: {_DISCOVERED_GEMINI_MODEL}")
    return _DISCOVERED_GEMINI_MODEL


class GeminiProvider(BaseLLMProvider):
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if model:
            self._model = model.replace("models/", "")
        elif os.getenv("GEMINI_MODEL"):
            self._model = os.getenv("GEMINI_MODEL").replace("models/", "")
        else:
            self._model = discover_gemini_flash_model(self.api_key)

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
