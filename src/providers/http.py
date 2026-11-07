"""
Shared HTTP transport for provider adapters: key-safe errors, JSON extraction.
Secrets are only ever sent in headers, and are scrubbed from every raised message.
"""

import json
import re
import time
from typing import Any, Dict, Optional

import requests


class ProviderError(Exception):
    """A provider call failed. `status` is the HTTP status when known; `retryable` drives backoff."""

    def __init__(self, message: str, status: Optional[int] = None, retryable: bool = False):
        super().__init__(message)
        self.status = status
        self.retryable = retryable


def scrub(text: str, secret: Optional[str]) -> str:
    return text.replace(secret, "***") if secret else text


def post_json(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: float,
              secret: Optional[str]) -> tuple:
    """POSTs JSON. Returns (parsed_response, latency_seconds). Raises ProviderError without leaking URL or key."""
    t0 = time.time()
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    except (requests.Timeout, requests.ConnectionError) as e:
        raise ProviderError(f"network error: {type(e).__name__}", retryable=True)
    latency = time.time() - t0
    if resp.status_code >= 400:
        body = scrub(resp.text[:300].replace("\n", " "), secret)
        raise ProviderError(
            f"HTTP {resp.status_code}: {body}",
            status=resp.status_code,
            retryable=resp.status_code in (408, 409, 429) or resp.status_code >= 500,
        )
    try:
        return resp.json(), latency
    except ValueError:
        raise ProviderError("response body was not JSON", status=resp.status_code, retryable=True)


def extract_json_object(raw_text: str) -> Dict[str, Any]:
    """Parses a JSON object from model text, tolerating markdown fences. Raises retryable ProviderError."""
    text = (raw_text or "").strip()
    try:
        value = json.loads(text)
    except ValueError:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        try:
            value = json.loads(m.group(0)) if m else None
        except ValueError:
            value = None
    if not isinstance(value, dict):
        raise ProviderError("model did not return a JSON object", retryable=True)
    return value
