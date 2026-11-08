"""
Deterministic validation of promo candidates against the real screenplay.

The model proposes; this module decides. Every cut point must be an authentic beat
edge, every quote must exist in the screenplay at the claimed place, durations and the
hook window are enforced here regardless of which provider produced the candidate.
"""

import re
from typing import Dict, List, Optional, Tuple

from src.constants import (
    CLIFF_WINDOW, CLIFFHANGER_TAIL_SECONDS, EPS, HOOK_WINDOW, MAX_DURATION, MIN_DURATION, SNAP_TOLERANCE,
)
from src.models import Beat, BeatType, Episode, PromoCandidate, Segment
from src.utils.timestamps import try_parse_timestamp

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


def verify_payoff_location(payoff_loc: object, episodes_by_num: Dict[int, Episode]) -> Optional[str]:
    """
    Verifies that payoff_location points to a real beat in the show.
    Accepts:
      - string e.g. "Ep 15 01:23.40", "Episode 15, 00:45.00", "Ep 15: 01:23.40", "15: 01:23.40"
      - dict e.g. {"episode": 15, "timestamp": "01:23.40"}
    Returns canonical string "Ep {episode} {timestamp}" if verified on a real beat, else None.
    """
    if not payoff_loc:
        return None
    if isinstance(payoff_loc, str) and payoff_loc.strip().lower() in ("unknown", "none", "null", ""):
        return None

    ep_num: Optional[int] = None
    ts_str: Optional[str] = None

    if isinstance(payoff_loc, dict):
        try:
            ep_val = payoff_loc.get("episode")
            ep_num = int(ep_val) if ep_val is not None else None
            ts_str = str(payoff_loc.get("timestamp", ""))
        except (ValueError, TypeError):
            return None
    elif isinstance(payoff_loc, str):
        m = re.search(r"(?:ep(?:isode)?\s*(\d+)|(?:^|\s)(\d+)\s*[:,\-])", payoff_loc, re.IGNORECASE)
        if m:
            ep_num = int(m.group(1) or m.group(2))
            ts_m = re.search(r"(?:(\d+:)?\d{1,2}:\d{1,2}(?:\.\d+)?)", payoff_loc)
            if ts_m:
                ts_str = ts_m.group(0)

    if ep_num is None or not ts_str:
        return None

    ep = episodes_by_num.get(ep_num)
    if ep is None:
        return None

    t_sec = try_parse_timestamp(ts_str)
    if t_sec is None:
        return None

    beats = spoken_beats(ep)
    # Prefer snapping to a beat start if within tolerance
    for b in beats:
        if abs(b.start_seconds - t_sec) <= SNAP_TOLERANCE + EPS:
            return f"Ep {ep_num} {b.start_str}"
    # Otherwise check if inside beat or near beat end
    for b in beats:
        if (
            abs(b.end_seconds - t_sec) <= SNAP_TOLERANCE + EPS
            or (b.start_seconds - EPS <= t_sec <= b.end_seconds + EPS)
        ):
            return f"Ep {ep_num} {b.start_str}"

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

    if cand.payoff_location is not None and str(cand.payoff_location).strip().lower() not in ("unknown", "none", ""):
        if not verify_payoff_location(cand.payoff_location, episodes_by_num):
            errors.append(f"payoff_location '{cand.payoff_location}' does not point to a real beat")

    return errors


def trim_to_cliffhanger(
    cand: PromoCandidate,
    episodes_by_num: Dict[int, Episode],
) -> Tuple[Optional[PromoCandidate], Optional[str]]:
    """
    If the tagged cliffhanger beat ends before the tail window (last 6s),
    trims the clip end to that beat's real end edge (for multi-segment clips,
    trims the segment containing the beat and drops later segments).
    Re-runs every hard check. If it falls under 20s, drops with reason
    'too short after cliffhanger trim'.
    Records trimmed_from_end and seconds_removed.
    Returns (candidate_or_none, drop_reason_if_any).
    """
    if not cand.segments:
        return None, "no segments"

    last_seg = cand.segments[-1]
    last_ep = episodes_by_num.get(
        last_seg.episode if last_seg.episode is not None else cand.episodes[-1]
    )
    cliff_quote = cand.cliffhanger.quote

    # Check if cliffhanger is already within the last CLIFFHANGER_TAIL_SECONDS of the clip
    if last_ep is not None:
        tail = [
            b for b in spoken_beats(last_ep)
            if last_seg.start_seconds - EPS <= b.start_seconds and b.end_seconds <= last_seg.end_seconds + EPS
        ]
        tail = [b for b in tail if b.end_seconds >= last_seg.end_seconds - CLIFFHANGER_TAIL_SECONDS - EPS]
        if find_quote_beat(tail, cliff_quote):
            cand.trimmed_from_end = False
            cand.seconds_removed = 0.0
            errs = check_candidate(cand, episodes_by_num)
            if errs:
                return None, errs[0]
            return cand, None

    # Search for tagged cliffhanger quote beat across all segments
    matched_seg_idx = -1
    matched_beat: Optional[Beat] = None

    for idx, seg in enumerate(cand.segments):
        ep_num = seg.episode if seg.episode is not None else (
            cand.episodes[idx] if idx < len(cand.episodes) else cand.episodes[0]
        )
        ep = episodes_by_num.get(ep_num)
        if ep is None:
            continue
        seg_beats = [
            b for b in spoken_beats(ep)
            if seg.start_seconds - EPS <= b.start_seconds and b.end_seconds <= seg.end_seconds + EPS
        ]
        b = find_quote_beat(seg_beats, cliff_quote)
        if b is not None:
            matched_seg_idx = idx
            matched_beat = b

    if matched_beat is None or matched_seg_idx < 0:
        return None, f"cliffhanger quote not found in the last {CLIFFHANGER_TAIL_SECONDS:.0f}s of the clip"

    orig_total = sum(s.duration for s in cand.segments)
    kept_segments = cand.segments[:matched_seg_idx + 1]
    target_seg = kept_segments[-1]

    if matched_beat.end_seconds <= target_seg.start_seconds:
        return None, "too short after cliffhanger trim"

    new_target_seg = Segment(
        episode=target_seg.episode,
        start=target_seg.start,
        end=matched_beat.end_str,
        start_seconds=target_seg.start_seconds,
        end_seconds=matched_beat.end_seconds,
    )
    kept_segments[-1] = new_target_seg

    new_total = round(sum(s.duration for s in kept_segments), 2)
    secs_removed = round(orig_total - new_total, 2)

    if new_total < MIN_DURATION - EPS:
        return None, "too short after cliffhanger trim"

    cand.segments = kept_segments
    cand.total_duration = new_total
    cand.trimmed_from_end = True
    cand.seconds_removed = secs_removed
    cand.cliffhanger.timestamp = matched_beat.start_str
    cand.cliffhanger.timestamp_seconds = matched_beat.start_seconds

    errs = check_candidate(cand, episodes_by_num)
    if errs:
        return None, errs[0]

    return cand, None

