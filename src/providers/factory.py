"""
Provider Factory for LLM clients.
"""

import os
from typing import Optional
from src.providers.base import BaseLLMProvider
from src.providers.gemini import GeminiProvider
from src.providers.openai import OpenAIProvider
from src.providers.anthropic import AnthropicProvider
from src.providers.heuristic import HeuristicProvider
from src.utils.logging import logger


def get_llm_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None
) -> BaseLLMProvider:
    """
    Instantiates an LLM provider using requested provider or auto-detection from environment.
    Supported providers:
      - 'gemini' (Default model: 'gemini-3.8-flash')
      - 'openai' (Default model: 'gpt-6-luna')
      - 'anthropic' (Default model: 'claude-sonnet-5-5')
      - 'heuristic' (Offline fallback)
    """
    target = (provider_name or "").lower().strip()

    if not target:
        if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
            target = "gemini"
        elif os.getenv("OPENAI_API_KEY"):
            target = "openai"
        elif os.getenv("ANTHROPIC_API_KEY"):
            target = "anthropic"
        else:
            target = "heuristic"

    logger.info(f"Initializing LLM provider: '{target}' (requested model: {model_name or 'default'})")

    if target == "gemini":
        return GeminiProvider(model=model_name)
    elif target == "openai":
        return OpenAIProvider(model=model_name)
    elif target == "anthropic":
        return AnthropicProvider(model=model_name)
    elif target == "heuristic":
        return HeuristicProvider()
    else:
        logger.warning(f"Unknown provider '{target}'. Falling back to HeuristicProvider.")
        return HeuristicProvider()
