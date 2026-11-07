"""
Show-agnostic adversarial quality auditor for promos.

Two methods, always labelled on the result:
  - "llm":   a model reads the actual clip screenplay (camera beats included) and judges it.
  - "rules": an offline lint for the keyword engine. It is NOT a quality judgement.
If a live audit call fails the result is method="error" (unaudited); it never falls back to rules.
"""

import re
from typing import List, Dict, Any, Optional
from src.models import PromoCandidate, QualityAudit, Episode
from src.providers.base import BaseLLMProvider
from src.providers.factory import get_llm_provider
from src.prompts import AUDIT_SYSTEM_PROMPT, AUDIT_USER_PROMPT_TEMPLATE
from src.parser import format_segment_slice
from src.taxonomy import Taxonomy
from src.utils.logging import logger

FLAW_TYPES = (
    "resolution_leak", "context_deficit", "visual_dependency",
    "slow_burn", "false_reading", "wrong_tag", "other",
)
_FLAW_KEYWORDS = (
    ("resolution_leak", ("resolution", "leak", "resolv", "spoil", "comeuppance")),
    ("context_deficit", ("context", "unexplained", "backstory", "cold viewer")),
    ("visual_dependency", ("visual",)),
    ("slow_burn", ("slow",)),
    ("false_reading", ("sarcas", "false", "ironic", "playful")),
    ("wrong_tag", ("tag", "mislabel", "misclass")),
)
_TRUE = {"true", "yes", "pass", "passed", "1"}
_FALSE = {"false", "no", "fail", "failed", "0"}


def parse_bool(value: Any) -> bool:
    """Strict boolean parse. 'false' must never become True."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in _TRUE:
            return True
        if v in _FALSE:
            return False
    raise ValueError(f"'pass' is not a boolean: {value!r}")


def normalize_flaw(value: Any) -> Optional[str]:
    """Maps the model's flaw label onto FLAW_TYPES so ranking penalties can rely on it."""
    if value is None or str(value).strip().lower() in ("", "none", "null"):
        return None
    text = str(value).strip().lower().replace(" ", "_")
    if text in FLAW_TYPES:
        return text
    for flaw, keys in _FLAW_KEYWORDS:
        if any(k in text for k in keys):
            return flaw
    return "other"


class PromoAuditor:
    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        show_context: Optional[Dict[str, Any]] = None,
        episodes: Optional[List[Episode]] = None,
        taxonomy: Optional[Taxonomy] = None,
    ):
        self.llm_provider = llm_provider or get_llm_provider()
        self.show_context = show_context or {}
        self.taxonomy = taxonomy
        self.episodes_by_num: Dict[int, Episode] = (
            {ep.episode_number: ep for ep in episodes} if episodes else {}
        )
        self._lore_tokens = self._extract_lore_tokens(self.show_context)

    def set_episodes(self, episodes: List[Episode]):
        self.episodes_by_num = {ep.episode_number: ep for ep in episodes}

    @staticmethod
    def _extract_lore_tokens(context: Dict[str, Any]) -> List[str]:
        """Character names from the show context, without parenthetical aliases."""
        tokens: List[str] = []
        for ant in context.get("antagonists", []) or []:
            if ant.get("name"):
                tokens.append(ant["name"].lower())
        ml = (context.get("male_lead") or {}).get("name", "")
        if ml:
            tokens.append(re.sub(r"\s*\(.*?\)", "", ml).strip().lower())
        return [t for t in tokens if t]

    def _get_screenplay_text(self, candidate: PromoCandidate) -> str:
        """The authentic beats of every segment, camera directions included."""
        fallback = f"(Dialogue quotes: Hook='{candidate.hook.quote}', Cliffhanger='{candidate.cliffhanger.quote}')"
        if not self.episodes_by_num or not candidate.segments:
            return fallback
        slices = []
        for idx, seg in enumerate(candidate.segments):
            ep_num = seg.episode if seg.episode is not None else (
                candidate.episodes[idx] if idx < len(candidate.episodes) else candidate.episodes[0]
            )
            ep = self.episodes_by_num.get(ep_num)
            if ep:
                text = format_segment_slice(ep, seg.start_seconds, seg.end_seconds, include_camera=True)
                slices.append(f"--- Segment {idx + 1} (Episode {ep_num} [{seg.start} -> {seg.end}]) ---\n{text}")
        return "\n\n".join(slices) if slices else fallback

    def audit_candidate(self, candidate: PromoCandidate) -> QualityAudit:
        if not self.llm_provider.is_live:
            return self._audit_via_rules(candidate)
        try:
            return self._audit_via_llm(candidate)
        except Exception as e:
            logger.error(f"LLM audit failed for {candidate.promo_id}: {e}")
            return QualityAudit(
                passed=False, method="error", audit_model=self.llm_provider.model,
                flaw_type="audit_error", confidence_score=0.0,
                critique=f"Audit unavailable ({e}); candidate is unaudited.",
            )

    def _tag_definitions(self, candidate: PromoCandidate) -> str:
        if not self.taxonomy:
            return "(taxonomy not provided)"
        return "\n".join([
            self.taxonomy.describe_type(candidate.hook.type, "hook"),
            self.taxonomy.describe_type(candidate.cliffhanger.type, "cliffhanger"),
        ])

    def _audit_via_llm(self, candidate: PromoCandidate) -> QualityAudit:
        user_prompt = AUDIT_USER_PROMPT_TEMPLATE.format(
            show_title=self.show_context.get("show_title", "Microdrama"),
            show_premise=str(self.show_context.get("premise", "")).strip(),
            episodes=candidate.episodes,
            segments_str=", ".join(f"{s.start} -> {s.end}" for s in candidate.segments),
            total_duration=candidate.total_duration,
            hook_type=candidate.hook.type,
            hook_quote=candidate.hook.quote,
            cliffhanger_type=candidate.cliffhanger.type,
            cliff_quote=candidate.cliffhanger.quote,
            tag_definitions=self._tag_definitions(candidate),
            screenplay_text=self._get_screenplay_text(candidate),
        )
        resp = self.llm_provider.generate_json(AUDIT_SYSTEM_PROMPT, user_prompt)

        passed = parse_bool(resp.get("pass"))
        flaw = normalize_flaw(resp.get("lethal_flaw"))
        if not passed and flaw is None:
            flaw = "other"
        critique = str(resp.get("critique", "")).strip()
        if not critique:
            raise ValueError("audit response has no critique")
        risks = resp.get("risks") or []
        return QualityAudit(
            passed=passed,
            method="llm",
            audit_model=self.llm_provider.model,
            flaw_type=None if passed else flaw,
            critique=critique,
            confidence_score=max(0.0, min(10.0, float(resp.get("confidence_score", 5.0)))),
            risks=[str(r) for r in risks] if isinstance(risks, list) else [str(risks)],
        )

    def _audit_via_rules(self, candidate: PromoCandidate) -> QualityAudit:
        """Offline lint for the keyword engine. Flags obvious problems; it does not judge quality."""
        risks: List[str] = []
        flaw_type: Optional[str] = None
        passed = True

        text_full = (candidate.hook.quote + " " + candidate.cliffhanger.quote + " "
                     + self._get_screenplay_text(candidate)).lower()

        if any(w in text_full for w in ["gazing down", "framing", "symmetrical", "close-up", "turns away", "steps into"]):
            risks.append("Relies moderately on visual acting/cinematography described in stage directions.")

        if self._lore_tokens and candidate.promo_type != "cross_episode":
            matched = [t for t in self._lore_tokens if t in text_full]
            if len(matched) >= 2 and candidate.scores.standalone_clarity < 8.0:
                risks.append(f"Multiple character references ({', '.join(matched)}) without setup may confuse cold viewers.")
                if candidate.scores.standalone_clarity < 7.0:
                    flaw_type, passed = "context_deficit", False

        if candidate.scores.payoff_withheld < 7.0:
            flaw_type, passed = "resolution_leak", False
            risks.append("Clip resolves part of its own tension, reducing urgency to click.")

        if candidate.cliffhanger.type == "interrupted_retaliation":
            cliff_text = candidate.cliffhanger.quote.lower()
            if any(p in cliff_text for p in ["clenched hand", "clenches fist", "eyes narrow", "looks down", "silent"]) and \
                    not any(a in cliff_text for a in ["will regret", "warn", "touch", "not finished", "swing", "strike", "stop", "dare"]):
                risks.append("Cliffhanger is only a subtle gesture without a concrete initiated counter-action.")

        return QualityAudit(
            passed=passed,
            method="rules",
            audit_model="rule-lint",
            flaw_type=flaw_type,
            critique="[rule lint, not a quality judgement] " + (risks[0] if risks else "No lint flags."),
            confidence_score=0.0,
            risks=risks,
        )
