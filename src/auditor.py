"""
Show-agnostic adversarial quality auditor for Promos.
Audits candidate clips for failure modes: resolution leaks, context deficits, visual dependencies.
"""

from typing import List, Dict, Any, Optional
from src.models import PromoCandidate, QualityAudit, Episode
from src.providers.base import BaseLLMProvider
from src.providers.factory import get_llm_provider
from src.prompts import AUDIT_SYSTEM_PROMPT, AUDIT_USER_PROMPT_TEMPLATE
from src.parser import format_segment_slice
from src.utils.logging import logger


class PromoAuditor:
    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        show_context: Optional[Dict[str, Any]] = None,
        episodes: Optional[List[Episode]] = None,
    ):
        self.llm_provider = llm_provider or get_llm_provider()
        self.show_context = show_context or {}
        self.episodes_by_num: Dict[int, Episode] = (
            {ep.episode_number: ep for ep in episodes} if episodes else {}
        )
        self._lore_tokens = self._extract_lore_tokens(self.show_context)

    def set_episodes(self, episodes: List[Episode]):
        """Caches parsed episodes for screenplay text slicing."""
        self.episodes_by_num = {ep.episode_number: ep for ep in episodes}

    def _extract_lore_tokens(self, context: Dict[str, Any]) -> List[str]:
        """Extracts dynamic character names and entities from show context config."""
        tokens: List[str] = []
        for ant in context.get("antagonists", []):
            name = ant.get("name", "")
            if name:
                tokens.append(name.lower())
        ml = context.get("male_lead", {}).get("name", "")
        if ml:
            tokens.append(ml.lower())
        return tokens

    def _get_screenplay_text(self, candidate: PromoCandidate) -> str:
        """Extracts the authentic screenplay dialogue and action beats for candidate segments."""
        if not self.episodes_by_num or not candidate.segments:
            return f"(Dialogue quotes: Hook='{candidate.hook.quote}', Cliffhanger='{candidate.cliffhanger.quote}')"

        slices = []
        for idx, seg in enumerate(candidate.segments):
            ep_num = candidate.episodes[idx] if idx < len(candidate.episodes) else candidate.episodes[0]
            ep = self.episodes_by_num.get(ep_num)
            if ep:
                slice_text = format_segment_slice(ep, seg.start_seconds, seg.end_seconds, include_camera=False)
                slices.append(f"--- Segment {idx + 1} (Episode {ep_num} [{seg.start} -> {seg.end}]) ---\n{slice_text}")
        return "\n\n".join(slices) if slices else f"(Dialogue quotes: Hook='{candidate.hook.quote}', Cliffhanger='{candidate.cliffhanger.quote}')"

    def audit_candidate(self, candidate: PromoCandidate) -> QualityAudit:
        """Audits a promo candidate, returning QualityAudit with critique and risks."""
        if self.llm_provider.name != "heuristic":
            try:
                return self._audit_via_llm(candidate)
            except Exception as e:
                logger.warning(f"LLM audit failed for {candidate.promo_id}: {e}. Using rule-based auditor.")

        return self._audit_via_rules(candidate)

    def _audit_via_llm(self, candidate: PromoCandidate) -> QualityAudit:
        segs_str = ", ".join(f"{s.start} -> {s.end}" for s in candidate.segments)
        screenplay_text = self._get_screenplay_text(candidate)

        user_prompt = AUDIT_USER_PROMPT_TEMPLATE.format(
            episodes=candidate.episodes,
            segments_str=segs_str,
            total_duration=candidate.total_duration,
            hook_type=candidate.hook.type,
            hook_quote=candidate.hook.quote,
            cliffhanger_type=candidate.cliffhanger.type,
            cliff_quote=candidate.cliffhanger.quote,
            why_it_works=candidate.why_it_works,
            screenplay_text=screenplay_text,
        )

        resp = self.llm_provider.generate_json(AUDIT_SYSTEM_PROMPT, user_prompt)

        passed = bool(resp.get("pass", True))
        flaw = resp.get("lethal_flaw")
        critique = resp.get("critique", "Solid emotional hook with high cold-viewer clarity.")
        confidence = float(resp.get("confidence_score", 8.0))
        risks = resp.get("risks", [])

        return QualityAudit(
            passed=passed,
            flaw_type=flaw,
            critique=critique,
            confidence_score=confidence,
            risks=risks,
        )

    def _audit_via_rules(self, candidate: PromoCandidate) -> QualityAudit:
        """Deterministic adversarial audit for offline / rapid benchmarking."""
        risks: List[str] = []
        flaw_type: Optional[str] = None
        passed = True

        screenplay_text = self._get_screenplay_text(candidate)
        text_full = (candidate.hook.quote + " " + candidate.cliffhanger.quote + " " + screenplay_text).lower()

        # Check visual dependency
        visual_keywords = ["gazing down", "framing", "symmetrical", "close-up", "turns away", "steps into"]
        if any(w in text_full for w in visual_keywords):
            risks.append("Relies moderately on visual acting/cinematography described in stage directions.")

        # Context deficit check based on show context (unintroduced character lore in short clips)
        if self._lore_tokens and candidate.promo_type != "cross_episode":
            matched_lore = [tok for tok in self._lore_tokens if tok in text_full]
            if len(matched_lore) >= 2 and candidate.scores.standalone_clarity < 8.0:
                risks.append(f"Multiple specific character references ({', '.join(matched_lore)}) without setup may confuse cold viewers.")
                if candidate.scores.standalone_clarity < 7.0:
                    flaw_type = "context_deficit"
                    passed = False

        # Check resolution leak
        if candidate.scores.payoff_withheld < 7.0:
            flaw_type = "resolution_leak"
            risks.append("Clip resolves part of its own tension, reducing urgency to click.")
            passed = False

        # Check interrupted retaliation validity (cannot be purely a passive beat or clenched hand)
        if candidate.cliffhanger.type == "interrupted_retaliation":
            cliff_text = candidate.cliffhanger.quote.lower()
            passive_beats = ["clenched hand", "clenches fist", "eyes narrow", "looks down", "silent"]
            if any(p in cliff_text for p in passive_beats) and not any(a in cliff_text for a in ["will regret", "warn", "touch", "not finished", "swing", "strike", "stop", "dare"]):
                risks.append("Cliffhanger is only a subtle facial/hand gesture without a concrete initiated counter-action.")

        return QualityAudit(
            passed=passed,
            flaw_type=flaw_type,
            critique=risks[0] if risks else "Solid emotional hook with high cold-viewer clarity and withheld payoff.",
            confidence_score=8.5 if passed else 6.5,
            risks=risks,
        )

        critique = (
            "Strong injustice tension that hooks scrollers immediately; payoff is firmly withheld."
            + (" " + "; ".join(risks) if risks else "")
        )

        return QualityAudit(
            passed=passed,
            flaw_type=flaw_type,
            critique=critique.strip(),
            confidence_score=8.5 if passed else 6.0,
            risks=risks,
        )
