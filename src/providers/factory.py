"""
Provider factory with an explicit registry. Add a provider with `register_provider`.
"""

import os
from typing import Callable, Dict, Optional
from dotenv import load_dotenv
from src.providers.base import BaseLLMProvider
from src.providers.gemini import GeminiProvider
from src.providers.openai import OpenAIProvider
from src.providers.anthropic import AnthropicProvider
from src.providers.heuristic import HeuristicProvider
from src.providers.resilience import CachedProvider, RetryingProvider
from src.utils.logging import logger

load_dotenv()

# name -> (constructor, env vars of which at least one must be set; () = none needed)
PROVIDERS: Dict[str, tuple] = {
    "gemini": (GeminiProvider, ("GEMINI_API_KEY", "GOOGLE_API_KEY")),
    "openai": (OpenAIProvider, ("OPENAI_API_KEY",)),
    "anthropic": (AnthropicProvider, ("ANTHROPIC_API_KEY",)),
    "heuristic": (HeuristicProvider, ()),
}


class ProviderConfigError(Exception):
    """The requested provider cannot be used (unknown name or missing credentials)."""


def register_provider(name: str, constructor: Callable[..., BaseLLMProvider], env_keys: tuple = ()) -> None:
    PROVIDERS[name.lower()] = (constructor, env_keys)


def _has_key(env_keys: tuple) -> bool:
    return not env_keys or any(os.getenv(k) for k in env_keys)


def get_llm_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
    cache: bool = False,
    retries: int = 8,
) -> BaseLLMProvider:
    """
    Instantiates a provider. An explicitly requested provider that is unknown or lacks
    credentials raises ProviderConfigError; it never silently becomes the keyword engine.
    With no name, the first provider with credentials is used, else the offline heuristic engine.
    """
    target = (provider_name or "").lower().strip()

    if not target:
        target = next((n for n in ("gemini", "openai", "anthropic") if _has_key(PROVIDERS[n][1])), "heuristic")
    elif target not in PROVIDERS:
        raise ProviderConfigError(f"Unknown provider '{target}'. Available: {', '.join(sorted(PROVIDERS))}.")
    else:
        constructor, env_keys = PROVIDERS[target]
        if not _has_key(env_keys):
            raise ProviderConfigError(f"Provider '{target}' needs one of: {', '.join(env_keys)} (set it in .env).")

    constructor, _ = PROVIDERS[target]
    logger.info(f"Initializing LLM provider: '{target}' (requested model: {model_name or 'default'})")
    provider = constructor() if target == "heuristic" else constructor(model=model_name)
    if not provider.is_live:
        return provider
    provider = RetryingProvider(provider, attempts=retries)
    return CachedProvider(provider) if cache else provider
