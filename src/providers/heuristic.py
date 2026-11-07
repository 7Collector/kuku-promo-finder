"""
Deterministic, offline heuristic provider.
Allows instantaneous zero-dependency benchmarking and offline testing.
"""

import re
from typing import Dict, Any
from src.providers.base import BaseLLMProvider


class HeuristicProvider(BaseLLMProvider):
    @property
    def name(self) -> str:
        return "heuristic"

    @property
    def model(self) -> str:
        return "heuristic-offline-engine"

    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Returns structured fallback format; domain heuristics are executed
        directly by PromoExtractor.
        """
        ep_match = re.search(r"Episode:\s*(?:Episode\s*)?(\d+)", user_prompt, re.IGNORECASE)
        ep_id = str(int(ep_match.group(1))) if ep_match else "1"

        return {
            "episode_id": ep_id,
            "candidates": [],
            "rejected_near_misses": []
        }
