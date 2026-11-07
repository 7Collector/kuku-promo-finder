"""
Backwards-compatible facade for LLM clients.
Delegates to the modular provider subsystem in src.providers.
"""

from typing import Optional, Dict, Any
from src.providers.base import BaseLLMProvider
from src.providers.factory import get_llm_provider
from src.prompts import PROMO_SYSTEM_PROMPT as SYSTEM_PROMPT


class LLMClient:
    """
    Facade wrapper around BaseLLMProvider.
    Maintains clean backward compatibility with previous interface.
    """
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        self._provider_instance: BaseLLMProvider = get_llm_provider(
            provider_name=provider, model_name=model
        )

    @property
    def provider(self) -> str:
        return self._provider_instance.name

    @property
    def model(self) -> str:
        return self._provider_instance.model

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        return self._provider_instance.generate_json(system_prompt, user_prompt)
