"""
Taxonomy loader and matching utilities for Promos.
"""

import os
import yaml
from typing import Dict, List, Any, Optional


class Taxonomy:
    def __init__(self, config_path: str = "config/taxonomy.yaml"):
        self.config_path = config_path
        self.hooks: List[Dict[str, Any]] = []
        self.cliffhangers: List[Dict[str, Any]] = []
        self.hook_by_id: Dict[str, Dict[str, Any]] = {}
        self.cliffhanger_by_id: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Taxonomy config not found at: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self.hooks = data.get("hooks", [])
        self.cliffhangers = data.get("cliffhangers", [])
        self.hook_by_id = {h["id"]: h for h in self.hooks}
        self.cliffhanger_by_id = {c["id"]: c for c in self.cliffhangers}

    def get_hook_weight(self, hook_id: str) -> float:
        return self.hook_by_id.get(hook_id, {}).get("weight", 0.8)

    def get_cliffhanger_weight(self, cliff_id: str) -> float:
        return self.cliffhanger_by_id.get(cliff_id, {}).get("weight", 0.8)

    def match_hook_cues(self, text: str) -> Optional[Dict[str, Any]]:
        """Matches text against hook taxonomy example cues."""
        text_lower = text.lower()
        best_match = None
        max_matches = 0
        for hook in self.hooks:
            cues = hook.get("example_cues", [])
            matches = sum(1 for cue in cues if cue.lower() in text_lower)
            if matches > max_matches:
                max_matches = matches
                best_match = hook
        return best_match

    def match_cliffhanger_cues(self, text: str) -> Optional[Dict[str, Any]]:
        """Matches text against cliffhanger taxonomy example cues."""
        text_lower = text.lower()
        best_match = None
        max_matches = 0
        for cliff in self.cliffhangers:
            cues = cliff.get("example_cues", [])
            matches = sum(1 for cue in cues if cue.lower() in text_lower)
            if matches > max_matches:
                max_matches = matches
                best_match = cliff
        return best_match

    def to_yaml_string(self) -> str:
        with open(self.config_path, "r", encoding="utf-8") as f:
            return f.read()
