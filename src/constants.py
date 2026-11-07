"""Hard constraints from the brief, in one place. Enforced in code, not in prompts."""

MIN_DURATION = 20.0      # seconds, total promo length
MAX_DURATION = 60.0
HOOK_WINDOW = 3.0        # the hook beat must start within this many seconds of the cut
EPS = 0.05               # float tolerance for the three limits above
SNAP_TOLERANCE = 0.5     # LLM timestamps within this distance of a real beat edge are snapped to it
SCORE_MIN, SCORE_MAX = 0.0, 10.0
SCRIPT_END_MARKER = r"-{3,}\s*SCRIPT END\s*-{3,}"
CLIFF_WINDOW = 6.0       # the cliffhanger beat must END within this many seconds of the final cut
