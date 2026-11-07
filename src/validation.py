"""
Deterministic validation of promo candidates against the real screenplay.

The model proposes; this module decides. Every cut point must be an authentic beat
edge, every quote must exist in the screenplay at the claimed place, durations and the
hook window are enforced here regardless of which provider produced the candidate.
"""

import re
from typing import Dict, List, Optional, Tuple

from src.constants import (
    CLIFF_WINDOW, EPS, HOOK_WINDOW, MAX_DURATION, MIN_DURATION, SNAP_TOLERANCE,
)
from src.models import Beat, BeatType, Episode, PromoCandidate

_PREFIX_RE = re.compile(r"^\s*(?:ACTION|SFX|SOUND FX|SOUND|CAMERA)\s*:\s*", re.IGNORECASE)
_PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
_SPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    text = _PREFIX_RE.sub("", text or "")
    text = _PUNCT_RE.sub("", text.lower().replace("’", "'").replace("’", "'"))
    return _SPACE_RE.sub(" ", text).strip()


def spoken_beats(episode: Episode) -> List[Beat]:
    """Beats usable as hook/cliffhanger evidence (everything a viewer hears or sees acted)."""
    return [b for b in episode.all_beats if b.beat_type != BeatType.CAMERA]


def snap_to_beat_edge(episode: Episode, t: float, edge: str) -> Optional[Beat]:
    """Returns the beat whose start (edge='start') or end (edge='end') is nearest to t, within tolerance."""
    best, best_d = None, SNAP_TOLERANCE + EPS
    for b in spoken_beats(episode):
        d = abs((b.start_seconds if edge == "start" else b.end_seconds) - t)
        if d < best_d:
            best, best_d = b, d
    return best


def find_quote_beat(beats: List[Beat], quote: str) -> Optional[Beat]:
    """First beat whose normalized text contains the normalized quote."""
    q = normalize_text(quote)
    if len(q) < 3:
        return None
    for b in beats:
        if q in normalize_text(b.text):
            return b
    return None


def check_candidate(cand: PromoCandidate, episodes_by_num: Dict[int, Episode]) -> List[str]:
    """
    Returns the list of violated hard rules (empty = valid). Provider-independent: runs on
    LLM output, heuristic output and composites alike.
    """
    errors: List[str] = []
    if not cand.segments:
        return ["no segments"]

    total = sum(s.duration for s in cand.segments)
    if not (MIN_DURATION - EPS <= total <= MAX_DURATION + EPS):
        errors.append(f"duration {total:.2f}s outside {MIN_DURATION:.0f}-{MAX_DURATION:.0f}s")

    for i, seg in enumerate(cand.segments):
        if seg.duration <= 0:
            errors.append(f"segment {i + 1} has non-positive duration")
            continue
        ep_num = seg.episode if seg.episode is not None else (
            cand.episodes[i] if i < len(cand.episodes) else cand.episodes[0]
        )
        ep = episodes_by_num.get(ep_num)
        if ep is None:
            errors.append(f"segment {i + 1}: episode {ep_num} not in input")
            continue
        starts = {round(b.start_seconds, 2) for b in spoken_beats(ep)}
        ends = {round(b.end_seconds, 2) for b in spoken_beats(ep)}
        if round(seg.start_seconds, 2) not in starts:
            errors.append(f"segment {i + 1} start {seg.start} is not a beat start in Ep {ep_num}")
        if round(seg.end_seconds, 2) not in ends:
            errors.append(f"segment {i + 1} end {seg.end} is not a beat end in Ep {ep_num}")

    first, last = cand.segments[0], cand.segments[-1]
    if cand.hook.timestamp_seconds < first.start_seconds - EPS or \
            cand.hook.timestamp_seconds - first.start_seconds > HOOK_WINDOW + EPS:
        errors.append(f"hook at {cand.hook.timestamp} is not within {HOOK_WINDOW:.0f}s of the opening cut")

    first_ep = episodes_by_num.get(first.episode if first.episode is not None else cand.episodes[0])
    last_ep = episodes_by_num.get(last.episode if last.episode is not None else cand.episodes[-1])
    if first_ep is not None:
        window = [b for b in spoken_beats(first_ep)
                  if first.start_seconds - EPS <= b.start_seconds <= first.start_seconds + HOOK_WINDOW + EPS]
        if not find_quote_beat(window, cand.hook.quote):
            errors.append("hook quote not found in a beat starting within the first 3s")
    if last_ep is not None:
        tail = [b for b in spoken_beats(last_ep)
                if last.start_seconds - EPS <= b.start_seconds and b.end_seconds <= last.end_seconds + EPS]
        tail = [b for b in tail if b.end_seconds >= last.end_seconds - CLIFF_WINDOW]
        if not find_quote_beat(tail, cand.cliffhanger.quote):
            errors.append(f"cliffhanger quote not found in the last {CLIFF_WINDOW:.0f}s of the clip")
    return errors
