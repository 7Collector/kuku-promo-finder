"""
Timestamp and temporal geometry utilities for microdrama screenplays.
"""

import re
from typing import Optional, Tuple

_TS_RE = re.compile(r"^(?:(\d+):)?(\d{1,2}):(\d{1,2}(?:\.\d+)?)$|^(\d+(?:\.\d+)?)$")


def try_parse_timestamp(ts: object) -> Optional[float]:
    """
    Strict timestamp parser. Returns seconds or None when the value is not a valid timestamp.
    Accepts '(00:11.30)', '00:11.30', '1:05.50', '01:02:15.00', '45.0'.
    Rejects minutes/seconds fields >= 60 (e.g. '09:99.00') and anything non-numeric.
    """
    if not isinstance(ts, (str, int, float)):
        return None
    s = str(ts).strip("() \t")
    m = _TS_RE.match(s)
    if not m:
        return None
    if m.group(4) is not None:
        return float(m.group(4))
    hours = int(m.group(1) or 0)
    minutes = int(m.group(2))
    seconds = float(m.group(3))
    if minutes >= 60 or seconds >= 60.0:
        return None
    return hours * 3600.0 + minutes * 60.0 + seconds


def parse_timestamp_to_seconds(ts: str) -> float:
    """
    Lenient wrapper kept for screenplay parsing. Invalid or empty input returns 0.0;
    use try_parse_timestamp() wherever invalid input must be detected.
    """
    value = try_parse_timestamp(ts)
    return 0.0 if value is None else value


def seconds_to_timestamp(sec: float) -> str:
    """Converts seconds (float) to mm:ss.ss formatted string."""
    sec = max(0.0, sec)
    minutes = int(sec // 60)
    remaining_sec = sec % 60
    return f"{minutes:02d}:{remaining_sec:05.2f}"


def calculate_temporal_overlap(
    start_a: float, end_a: float, start_b: float, end_b: float
) -> Tuple[float, float]:
    """
    Calculates overlap duration (seconds) and the overlap ratio relative
    to the shorter interval.
    Returns: (overlap_duration_seconds, overlap_ratio)
    """
    start_max = max(start_a, start_b)
    end_min = min(end_a, end_b)

    if end_min <= start_max:
        return 0.0, 0.0

    overlap_dur = end_min - start_max
    min_dur = min(max(0.001, end_a - start_a), max(0.001, end_b - start_b))
    ratio = overlap_dur / min_dur
    return overlap_dur, ratio
