"""
Taxonomy loader and matching utilities for Promos.
Features regex word boundaries, inanimate object collision filters, and memory-cached YAML.
"""

import os
import re
import yaml
from typing import Dict, List, Any, Optional

INANIMATE_OBJECT_TOKENS = [
    "flint", "steel", "kindling", "spark", "sparks", "gavel", "sound block",
    "clock", "bell", "chime", "door", "doors", "table", "chair", "candle", "lamp"
]


class Taxonomy:
    def __init__(self, config_path: str = "config/taxonomy.yaml"):
        self.config_path = config_path
        self.hooks: List[Dict[str, Any]] = []
        self.cliffhangers: List[Dict[str, Any]] = []
        self.hook_by_id: Dict[str, Dict[str, Any]] = {}
        self.cliffhanger_by_id: Dict[str, Dict[str, Any]] = {}
        self._raw_yaml: str = ""
        self.load()

    def load(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Taxonomy config not found at: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            self._raw_yaml = f.read()

        data = yaml.safe_load(self._raw_yaml) or {}
        self.hooks = data.get("hooks", [])
        self.cliffhangers = data.get("cliffhangers", [])
        self.hook_by_id = {h["id"]: h for h in self.hooks}
        self.cliffhanger_by_id = {c["id"]: c for c in self.cliffhangers}

    def get_hook_weight(self, hook_id: str) -> float:
        return self.hook_by_id.get(hook_id, {}).get("weight", 0.80)

    def get_cliffhanger_weight(self, cliff_id: str) -> float:
        return self.cliffhanger_by_id.get(cliff_id, {}).get("weight", 0.80)

    def match_hook_cues(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Matches text against hook taxonomy cues with strict regex word boundaries.
        Filters out false positive collisions (e.g. physical aggression on inanimate flint/gavel).
        """
        text_lower = text.lower()
        is_inanimate = any(re.search(r"\b" + re.escape(tok) + r"\b", text_lower) for tok in INANIMATE_OBJECT_TOKENS)

        best_match = None
        max_matches = 0

        for hook in self.hooks:
            # If physical aggression, ignore actions against inanimate objects (e.g. lighting fire or judge gavel)
            if hook["id"] == "physical_aggression" and is_inanimate:
                continue

            cues = hook.get("example_cues", [])
            matches = sum(
                1 for cue in cues
                if re.search(r"\b" + re.escape(cue.lower()) + r"\b", text_lower)
            )

            if matches > max_matches:
                max_matches = matches
                best_match = hook

        return best_match

    def match_cliffhanger_cues(self, text: str) -> Optional[Dict[str, Any]]:
        """Matches text against cliffhanger taxonomy cues with regex word boundaries."""
        text_lower = text.lower()
        best_match = None
        max_matches = 0

        for cliff in self.cliffhangers:
            cues = cliff.get("example_cues", [])
            matches = sum(
                1 for cue in cues
                if re.search(r"\b" + re.escape(cue.lower()) + r"\b", text_lower)
            )

            if matches > max_matches:
                max_matches = matches
                best_match = cliff

        return best_match

    def to_yaml_string(self) -> str:
        """Returns in-memory cached YAML string."""
        return self._raw_yaml

    def hooks_to_yaml_string(self) -> str:
        """Returns in-memory YAML of only hooks."""
        return yaml.dump({"hooks": self.hooks}, sort_keys=False)

    def cliffhangers_to_yaml_string(self) -> str:
        """Returns in-memory YAML of only cliffhangers."""
        return yaml.dump({"cliffhangers": self.cliffhangers}, sort_keys=False)
