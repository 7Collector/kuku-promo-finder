"""
Adversarial Quality Auditor for Promos.
Audits candidate clips for failure modes: resolution leaks, context deficit, visual dependencies.
"""

from typing import List, Dict, Any, Optional
from src.models import PromoCandidate, QualityAudit
from src.llm_client import LLMClient


AUDIT_PROMPT_TEMPLATE = """You are an adversarial video producer auditing promo candidate clips for TikTok/Reels.
Your job is to identify FALSE POSITIVES and explain why a proposed promo will fail in the wild.

Proposed Promo:
- Episode(s): {episodes}
- Timestamps: {segments_str} (Duration: {total_duration:.1f}s)
- Hook Tagged: {hook_type} ("{hook_quote}")
- Cliffhanger Tagged: {cliffhanger_type} ("{cliff_quote}")
- Why it works: {why_it_works}

Audit against these 5 Failure Modes:
1. Resolution Leak: Does the clip accidentally resolve the conflict (e.g. protagonist already gets revenge or explains the misunderstanding)?
2. Context Deficit: Does the dialogue use pronouns or references that make no sense to someone who hasn't seen the show?
3. Visual Dependency: Does the dramatic weight depend on visual acting/effects that the text describes but might look clumsy or muted on screen?
4. Slow Burn: Does the true hook happen at second 5-8 instead of within the first 3 seconds?
5. Sarcasm / False Reading: Is the emotional keyword being used playfully or ironically rather than with genuine high stakes?

Output JSON:
{{
  "pass": true,
  "lethal_flaw": null,
  "critique": "One to two sentences honestly identifying risks, cold-viewer comprehension limits, or visual dependencies.",
  "confidence_score": 8.5,
  "risks": ["Slight visual reliance on cathedral atmosphere"]
}}
"""


class PromoAuditor:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()

    def audit_candidate(self, candidate: PromoCandidate) -> QualityAudit:
        """Audits a promo candidate, returning QualityAudit with critique and risks."""
        if self.llm_client.provider != "heuristic":
            try:
                return self._audit_via_llm(candidate)
            except Exception as e:
                print(f"[Warning] LLM audit failed for {candidate.promo_id}: {e}. Using rule-based auditor.")

        return self._audit_via_rules(candidate)

    def _audit_via_llm(self, candidate: PromoCandidate) -> QualityAudit:
        segs_str = ", ".join(f"{s.start} -> {s.end}" for s in candidate.segments)
        user_prompt = AUDIT_PROMPT_TEMPLATE.format(
            episodes=candidate.episodes,
            segments_str=segs_str,
            total_duration=candidate.total_duration,
            hook_type=candidate.hook.type,
            hook_quote=candidate.hook.quote,
            cliffhanger_type=candidate.cliffhanger.type,
            cliff_quote=candidate.cliffhanger.quote,
            why_it_works=candidate.why_it_works,
        )

        resp = self.llm_client.generate_json(
            "You are an adversarial video marketing auditor. Respond in strict JSON.",
            user_prompt,
        )

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

        # Check visual dependency
        text_full = (candidate.hook.quote + " " + candidate.cliffhanger.quote).lower()
        if any(w in text_full for w in ["gazing down", "framing", "symmetrical", "close-up", "turns away"]):
            risks.append("Relies moderately on visual acting/cinematography described in stage directions.")

        # Check context deficit
        if any(w in text_full for w in ["house sterling", "alliance", "father thomas", "informant"]):
            risks.append("Mention of noble house or external lore may require minor viewer inference.")

        # Check resolution leak
        if candidate.scores.payoff_withheld < 7.0:
            flaw_type = "resolution_leak"
            risks.append("Clip may resolve part of its own tension, reducing urgency to click.")
            passed = False

        critique = (
            "Strong injustice tension that hooks scrollers immediately; payoff is firmly withheld. "
            + (" " + "; ".join(risks) if risks else "")
        )

        return QualityAudit(
            passed=passed,
            flaw_type=flaw_type,
            critique=critique.strip(),
            confidence_score=8.5 if passed else 6.0,
            risks=risks,
        )
