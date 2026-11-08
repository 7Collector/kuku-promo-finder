"""
Cost calculation utilities for LLM provider pricing.
"""

from typing import Tuple


def calculate_cost_usd(provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """
    Computes exact estimated cost in USD based on published token pricing.
    """
    p = (provider or "").lower().strip()
    m = (model or "").lower().strip()

    if "openai" in p or "gpt" in m or "luna" in m:
        # gpt-6-luna: $0.10 / 1M prompt tokens, $0.50 / 1M completion tokens
        return round((prompt_tokens * 0.10 + completion_tokens * 0.50) / 1_000_000, 6)
    elif "gemini" in p or "gemini" in m:
        # gemini flash: $0.075 / 1M prompt tokens, $0.30 / 1M completion tokens
        return round((prompt_tokens * 0.075 + completion_tokens * 0.30) / 1_000_000, 6)
    elif "anthropic" in p or "claude" in m:
        # claude-sonnet-5-5 / 3-5: $3.00 / 1M prompt tokens, $15.00 / 1M completion tokens
        return round((prompt_tokens * 3.00 + completion_tokens * 15.00) / 1_000_000, 6)
    return 0.0


def format_stage_cost(live_cost: float, cached_cost: float, live_calls: int, cache_hits: int) -> str:
    """
    Formats cost string according to Section 1 specification:
    'cached (original cost $X)' for hits, or '$X' for live calls.
    """
    if live_calls > 0 and cache_hits > 0:
        return f"${live_cost:.4f} (+ cached original cost ${cached_cost:.4f})"
    elif live_calls > 0:
        return f"${live_cost:.4f}"
    elif cache_hits > 0:
        return f"cached (original cost ${cached_cost:.4f})"
    return "$0.0000"
