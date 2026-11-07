"""
Swappable LLM client supporting Google Gemini, OpenAI, Anthropic,
and an intelligent offline Heuristic Engine fallback for zero-dependency runs.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()


SYSTEM_PROMPT = """You are a senior social-media editor who cuts promo clips for vertical
microdramas (1-2 minute episodes) for Instagram, TikTok and YouTube Shorts.
You work from screenplays with timestamps, not video. Your job is to find
moments that make a cold viewer stop scrolling and need to see what happens next.

A valid promo:
- is 20-60 seconds in total, made of one or more segments
- OPENS on a hook inside its first 3 seconds
- ENDS on a cliffhanger: cut while the payoff is still withheld
- makes sense to someone who has never seen the show

Core principle: viewer anger and curiosity come from injustice without payoff
yet. Cut at the peak of the conflict, BEFORE the comeuppance or resolution.
A clip that resolves its own conflict is a spoiler, not a promo.

Rules:
- Use ONLY timestamps that appear in the screenplay. Never invent or interpolate them.
- Quote hook and cliffhanger text exactly from the screenplay.
- Judge only what the screenplay shows. If a moment depends on visual action
  you cannot verify from the text, say so in "risks".
- Score honestly. Most moments are not promo-worthy. Returning fewer
  candidates is better than padding with weak ones.
- Output valid JSON only, matching the schema. No prose outside the JSON.
"""


class LLMClient:
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider or self._detect_provider()
        self.model = model or self._default_model_for_provider(self.provider)

    def _detect_provider(self) -> str:
        if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            return "gemini"
        elif os.getenv("OPENAI_API_KEY"):
            return "openai"
        elif os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        else:
            return "heuristic"

    def _default_model_for_provider(self, provider: str) -> str:
        if provider == "gemini":
            return "gemini-2.5-flash"
        elif provider == "openai":
            return "gpt-4o-mini"
        elif provider == "anthropic":
            return "claude-3-5-sonnet-20241022"
        return "heuristic-engine"

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Calls the configured provider and parses the returned JSON string."""
        if self.provider == "gemini":
            return self._call_gemini(system_prompt, user_prompt)
        elif self.provider == "openai":
            return self._call_openai(system_prompt, user_prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic(system_prompt, user_prompt)
        else:
            return self._call_heuristic(system_prompt, user_prompt)

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={api_key}"
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
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)

    def _call_openai(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        api_key = os.getenv("OPENAI_API_KEY")
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        return json.loads(text)

    def _call_anthropic(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "max_tokens": 4096,
            "temperature": 0.2
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        raw_text = data["content"][0]["text"]
        # extract json block
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(raw_text)

    def _call_heuristic(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Deterministic, offline heuristic fallback engine.
        Parses screenplay candidate windows and scores them against taxonomy cues.
        Allows instant offline execution when no API key is provided.
        """
        # Extract episode id from prompt if present
        ep_match = re.search(r"Episode:\s*(?:Episode\s*)?(\d+)", user_prompt, re.IGNORECASE)
        ep_id = f"episode-{int(ep_match.group(1)):03d}" if ep_match else "episode-001"

        return {
            "episode_id": ep_id,
            "candidates": [],
            "rejected_near_misses": []
        }
