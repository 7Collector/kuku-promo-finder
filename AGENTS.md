# Agents & AI Collaboration Log

## Tools Used

- **Antigravity (Claude Opus 4.6 Thinking)** — Primary AI coding assistant for architecture design, deterministic parser implementation, two-layer taxonomy design, and CLI engine.
- **Claude** — Used for prompt drafting, adversarial failure mode categorization, and iterative refinement of hook/cliffhanger schemas.

## Where AI Got It Wrong

1. **Timestamp Hallucination & Interval Math Drift**:
   When prompt-tested zero-shot on raw screenplay text, LLMs frequently hallucinated clean, rounded timestamps (e.g. inventing `00:45.00` or `01:00.00` when the actual dialogue was at `00:47.80`) that did not exist in the screenplay, and routinely miscalculated time intervals (claiming `00:18.00` to `00:52.00` was 40 seconds).
   *How we fixed it:* Kept timestamp arithmetic, duration bounds (20–60s), and boundary matching 100% deterministic in Python code (`src/parser.py` and `src/ranker.py`), requiring every cut point to match an authentic beat start/end.

2. **Conflating Atmospheric Cinematography with Viral Hooks**:
   Without explicit negative constraints, LLMs repeatedly proposed opening promos on establishing shots (e.g., `00:00.00` camera pans across the cathedral doors). On vertical short-form platforms (TikTok/Reels), 3 seconds of a camera panning an empty doorway leads to an immediate swipe.
   *How we fixed it:* Enforced a hard code constraint that the hook must trigger within ≤ 3.0 seconds of the opening cut, backed by our "Blood Boils" taxonomy requiring immediate interpersonal injustice or dialogue confrontation.

3. **Auditor Blindness to Mid-Segment Dialogue**:
   In early prompt iterations, the adversarial auditor template evaluated candidates using only the hook quote, cliffhanger quote, and the extractor's own "why it works" explanation. Because it never received the screenplay text occurring between the cuts, the model hallucinated whether a "resolution leak" occurred in the middle, grading its own summary rather than ground-truth beats.
   *How we fixed it:* Updated `src/parser.py` and `src/auditor.py` to slice and inject the authentic dialogue and action beat sequence (`<clip_screenplay>`) into every audit call, giving the auditor ground-truth visibility into the entire clip.
