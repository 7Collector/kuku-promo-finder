"""
Timestamp and temporal geometry utilities for microdrama screenplays.
"""

from typing import Tuple


def parse_timestamp_to_seconds(ts: str) -> float:
    """
    Converts timestamp string to seconds (float).
    Supports: '(00:11.30)', '00:11.30', '1:05.50', '01:02:15.00', '45.0'.
    """
    ts_clean = ts.strip("() ").strip()
    if not ts_clean:
        return 0.0

    parts = ts_clean.split(":")
    try:
        if len(parts) == 1:
            return float(parts[0])
        elif len(parts) == 2:
            return float(parts[0]) * 60.0 + float(parts[1])
        elif len(parts) == 3:
            return float(parts[0]) * 3600.0 + float(parts[1]) * 60.0 + float(parts[2])
    except ValueError:
        return 0.0
    return 0.0


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
