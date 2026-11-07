"""
Taxonomy loader and matching utilities for Promos.
Features regex word boundaries, inanimate object collision filters, and memory-cached YAML.
"""

import os
import re
import yaml
from typing import Dict, List, Any, Optional

# Objects that make a "physical aggression" cue a false positive. Extend per show if needed.
INANIMATE_OBJECT_TOKENS = [
    "flint", "steel", "kindling", "spark", "sparks", "gavel", "sound block",
    "clock", "bell", "chime", "door", "doors", "table", "chair", "candle", "lamp"
]


class Taxonomy:
    def __init__(
        self,
        config_path: str = "config/taxonomy.yaml",
        show_context_path: Optional[str] = None,
        overlay: Optional[Dict[str, List[str]]] = None,
    ):
        self.config_path = config_path
        self.show_context_path = show_context_path
        self.overlay: Dict[str, List[str]] = overlay or {}
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

        # Load show overlay if available
        if self.show_context_path and os.path.exists(self.show_context_path):
            with open(self.show_context_path, "r", encoding="utf-8") as f:
                show_data = yaml.safe_load(f) or {}
                self.overlay.update(show_data.get("show_cues_overlay", {}))

        # Merge show cues into each hook / cliffhanger
        for h in self.hooks:
            cues = list(h.get("generic_cues", [])) + list(h.get("example_cues", []))
            if h["id"] in self.overlay:
                cues.extend(self.overlay[h["id"]])
            h["example_cues"] = list(dict.fromkeys(cues))

        for c in self.cliffhangers:
            cues = list(c.get("generic_cues", [])) + list(c.get("example_cues", []))
            if c["id"] in self.overlay:
                cues.extend(self.overlay[c["id"]])
            c["example_cues"] = list(dict.fromkeys(cues))

        self.hook_by_id = {h["id"]: h for h in self.hooks}
        self.cliffhanger_by_id = {c["id"]: c for c in self.cliffhangers}

    # Weight for a model-proposed "new:<name>" type: neutral, so it is neither rewarded nor
    # punished for not being in the registry.
    NEW_TYPE_WEIGHT = 0.90

    def get_hook_weight(self, hook_id: str) -> float:
        return self.hook_by_id.get(hook_id, {}).get("weight", self.NEW_TYPE_WEIGHT)

    def get_cliffhanger_weight(self, cliff_id: str) -> float:
        return self.cliffhanger_by_id.get(cliff_id, {}).get("weight", self.NEW_TYPE_WEIGHT)

    def normalize_type(self, raw: str, kind: str, default: str) -> str:
        """Maps a model-supplied type to a registered id, or to 'new:<slug>' when unregistered."""
        registry = self.hook_by_id if kind == "hook" else self.cliffhanger_by_id
        value = (raw or "").strip()
        if value in registry:
            return value
        slug = re.sub(r"[^a-z0-9]+", "_", value.lower().removeprefix("new:")).strip("_")
        if slug in registry:
            return slug
        return f"new:{slug}" if slug else default

    def describe_type(self, type_id: str, kind: str) -> str:
        """Definition, requirements and exclusions of a tagged type, for the auditor prompt."""
        t = (self.hook_by_id if kind == "hook" else self.cliffhanger_by_id).get(type_id)
        if not t:
            return f"{type_id}: (model-proposed type, no registry definition)"
        lines = [f"{t['id']} - {t.get('name', '')}: {t.get('definition', '')}"]
        if t.get("requires"):
            lines.append("  requires: " + "; ".join(t["requires"]))
        if t.get("do_not_tag_if"):
            lines.append("  do NOT tag if: " + "; ".join(t["do_not_tag_if"]))
        return "\n".join(lines)

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
