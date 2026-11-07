"""
Base abstract interface for LLM providers (Strategy Pattern).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier."""
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        """Model identifier."""
        pass

    @abstractmethod
    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Executes generation and returns parsed JSON dictionary.
        Must raise an exception if generation or parsing fails.
        """
        pass
