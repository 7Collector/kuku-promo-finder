"""Hard constraints from the brief, in one place. Enforced in code, not in prompts."""

MIN_DURATION = 20.0      # seconds, total promo length
MAX_DURATION = 60.0
HOOK_WINDOW = 3.0        # the hook beat must start within this many seconds of the cut
EPS = 0.05               # float tolerance for the three limits above
SNAP_TOLERANCE = 0.5     # LLM timestamps within this distance of a real beat edge are snapped to it
# Scoring weights (editorial priors, not calibrated against ground truth)
WEIGHT_HOOK = 0.30
WEIGHT_CLIFFHANGER = 0.25
WEIGHT_PAYOFF_WITHHELD = 0.20
WEIGHT_INJUSTICE_TENSION = 0.15
WEIGHT_STANDALONE_CLARITY = 0.10
WEIGHT_CONVERSION_INTENT = 0.0

# Listwise reranking blend weights (when --rerank is active)
WEIGHT_WEIGHTED_SCORE = 0.50
WEIGHT_RERANK_SCORE = 0.50

SCORE_MIN, SCORE_MAX = 0.0, 10.0
SCRIPT_END_MARKER = r"-{3,}\s*SCRIPT END\s*-{3,}"
CLIFFHANGER_TAIL_SECONDS = 6.0
CLIFF_WINDOW = CLIFFHANGER_TAIL_SECONDS       # the cliffhanger beat must END within this many seconds of the final cut

# Legacy weights (kept for ablation comparison only)
LEGACY_WEIGHT_HOOK = 0.35
LEGACY_WEIGHT_CLIFFHANGER = 0.25
LEGACY_WEIGHT_PAYOFF_WITHHELD = 0.10
LEGACY_WEIGHT_INJUSTICE_TENSION = 0.20
LEGACY_WEIGHT_STANDALONE_CLARITY = 0.10
LEGACY_WEIGHT_CONVERSION_INTENT = 0.0
LEGACY_SCORING_WEIGHTS = {
    "hook": LEGACY_WEIGHT_HOOK,
    "cliffhanger": LEGACY_WEIGHT_CLIFFHANGER,
    "payoff_withheld": LEGACY_WEIGHT_PAYOFF_WITHHELD,
    "injustice_tension": LEGACY_WEIGHT_INJUSTICE_TENSION,
    "standalone_clarity": LEGACY_WEIGHT_STANDALONE_CLARITY,
    "conversion_intent": LEGACY_WEIGHT_CONVERSION_INTENT,
}


