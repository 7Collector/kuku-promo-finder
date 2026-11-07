"""
Deterministic parser for Kuku microdrama screenplays.
Extracts structured metadata, scenes, dialogue lines, action beats, and camera directions.
Supports timestamps both with and without parentheses.
"""

import os
import re
import glob
from typing import List, Optional, Tuple
from src.models import (
    Beat,
    BeatType,
    Scene,
    Episode,
)
from src.utils.timestamps import (
    parse_timestamp_to_seconds,
    seconds_to_timestamp,
)
from src.utils.logging import logger


BEAT_PATTERN = re.compile(
    r"\*\*([^*]+)\*\*\s*\n"
    r"Start:\s*\(?([0-9:\.]+)\)?\s*\|\s*End:\s*\(?([0-9:\.]+)\)?\s*\n"
    r"(.*?)(?=\n\*\*[^*]+\*\*\s*\nStart:|\nSCENE\s+\d+|\n-{3,}\s*SCRIPT END|\Z)",
    re.DOTALL,
)
START_LINE_PATTERN = re.compile(r"^\s*Start:", re.MULTILINE)

EPISODE_NUM_PATTERN = re.compile(
    r"EPISODE NUMBER:\s*(?:Episode\s*)?(\d+)", re.IGNORECASE
)
LOGLINE_PATTERN = re.compile(
    r"EPISODE LOGLINE:\s*(.*?)(?=\nCONTINUITY NOTES:|\n---|\nSCENE|\Z)", re.DOTALL | re.IGNORECASE
)
CONTINUITY_PATTERN = re.compile(
    r"CONTINUITY NOTES:\s*(.*?)(?=\n---|\nSCENE|\Z)", re.DOTALL | re.IGNORECASE
)
SCENE_SPLIT_PATTERN = re.compile(r"\n(?=SCENE\s+\d+)")
SCENE_HEADER_PATTERN = re.compile(r"SCENE\s+(\d+)", re.IGNORECASE)
SCENE_HEADING_PATTERN = re.compile(r"Scene heading:\s*(.*?)(?=\nScene start:|\nActions|\Z)", re.IGNORECASE)
SCENE_START_PATTERN = re.compile(r"Scene start:\s*([0-9:\.]+)", re.IGNORECASE)
SCENE_END_PATTERN = re.compile(r"Scene end:\s*([0-9:\.]+)", re.IGNORECASE)


def parse_header_type(raw_header: str) -> Tuple[BeatType, Optional[str], Optional[str]]:
    """
    Parses beat header into BeatType, Speaker, and Emotion.
    Examples:
      - 'CAMERA:' -> CAMERA, None, None
      - 'ACTION:' -> ACTION, None, None
      - 'SOUND FX:' -> SOUND, None, None
      - 'MATRIARCH (Cold, Commanding):' -> DIALOGUE, 'MATRIARCH', 'Cold, Commanding'
    """
    cleaned = raw_header.strip().rstrip(":")
    upper = cleaned.upper()

    if upper in ["CAMERA"]:
        return BeatType.CAMERA, None, None
    elif upper in ["ACTION"]:
        return BeatType.ACTION, None, None
    elif upper in ["SOUND FX", "SOUND", "SFX"]:
        return BeatType.SOUND, None, None
    else:
        speaker = cleaned
        emotion = None
        if "(" in cleaned and ")" in cleaned:
            open_idx = cleaned.index("(")
            close_idx = cleaned.rindex(")")
            speaker = cleaned[:open_idx].strip()
            emotion = cleaned[open_idx + 1:close_idx].strip()
        return BeatType.DIALOGUE, speaker, emotion


def _number_from_filename(filename: str) -> Optional[int]:
    m = re.search(r"episode[-_ ]?0*(\d+)", os.path.basename(filename), re.IGNORECASE)
    return int(m.group(1)) if m else None


def parse_screenplay_text(content: str, filename: str = "", default_number: Optional[int] = None) -> Episode:
    """Parses raw screenplay text into a structured Episode model."""
    ep_match = EPISODE_NUM_PATTERN.search(content)
    if ep_match:
        ep_number = int(ep_match.group(1))
    else:
        ep_number = _number_from_filename(filename) or default_number or 1
        logger.warning(
            f"{filename or 'screenplay'}: no 'EPISODE NUMBER:' line; using episode number {ep_number}."
        )

    if filename:
        ep_id = os.path.splitext(os.path.basename(filename))[0]
    else:
        ep_id = f"episode-{ep_number:03d}"

    logline_match = LOGLINE_PATTERN.search(content)
    logline = logline_match.group(1).strip() if logline_match else ""

    continuity_match = CONTINUITY_PATTERN.search(content)
    continuity = continuity_match.group(1).strip() if continuity_match else ""

    scene_blocks = SCENE_SPLIT_PATTERN.split(content)
    parsed_scenes: List[Scene] = []
    max_end_time = 0.0

    for block in scene_blocks:
        sc_num_match = SCENE_HEADER_PATTERN.search(block)
        if not sc_num_match:
            continue
        sc_num = int(sc_num_match.group(1))

        heading_m = SCENE_HEADING_PATTERN.search(block)
        heading = heading_m.group(1).strip() if heading_m else f"Scene {sc_num}"

        start_m = SCENE_START_PATTERN.search(block)
        sc_start_str = start_m.group(1).strip() if start_m else "00:00.00"
        sc_start_sec = parse_timestamp_to_seconds(sc_start_str)

        end_m = SCENE_END_PATTERN.search(block)
        sc_end_str = end_m.group(1).strip() if end_m else "00:00.00"
        sc_end_sec = parse_timestamp_to_seconds(sc_end_str)

        beats: List[Beat] = []
        for b_match in BEAT_PATTERN.finditer(block):
            raw_header = b_match.group(1)
            b_start_str = b_match.group(2).strip()
            b_end_str = b_match.group(3).strip()
            b_text = b_match.group(4).strip()

            b_start_sec = parse_timestamp_to_seconds(b_start_str)
            b_end_sec = parse_timestamp_to_seconds(b_end_str)
            if b_end_sec < b_start_sec:
                logger.warning(f"{ep_id}: dropped beat with end before start ({b_start_str} -> {b_end_str}).")
                continue
            max_end_time = max(max_end_time, b_end_sec)

            b_type, speaker, emotion = parse_header_type(raw_header)

            beats.append(
                Beat(
                    beat_type=b_type,
                    speaker=speaker,
                    emotion=emotion,
                    text=b_text,
                    start_seconds=b_start_sec,
                    end_seconds=b_end_sec,
                    start_str=b_start_str,
                    end_str=b_end_str,
                )
            )

        parsed_scenes.append(
            Scene(
                scene_number=sc_num,
                heading=heading,
                start_seconds=sc_start_sec,
                end_seconds=sc_end_sec,
                start_str=sc_start_str,
                end_str=sc_end_str,
                beats=beats,
            )
        )

    parsed_beats = sum(len(sc.beats) for sc in parsed_scenes)
    expected_beats = len(START_LINE_PATTERN.findall(content))
    if parsed_beats != expected_beats:
        logger.warning(
            f"{ep_id}: parsed {parsed_beats} beats but found {expected_beats} 'Start:' lines; "
            f"{expected_beats - parsed_beats} malformed or dropped."
        )

    return Episode(
        episode_number=ep_number,
        episode_id=ep_id,
        logline=logline,
        continuity_notes=continuity,
        scenes=parsed_scenes,
        total_duration=max_end_time,
    )


def parse_screenplay_file(file_path: str) -> Episode:
    """Reads and parses a single screenplay .txt file."""
    with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
        content = f.read()
    return parse_screenplay_text(content, filename=file_path)


def parse_all_episodes(directory_path: str) -> List[Episode]:
    """Parses all screenplay files in a directory, sorted by episode number."""
    if not os.path.isdir(directory_path):
        raise FileNotFoundError(f"Input directory not found: {directory_path}")
    files = sorted(glob.glob(os.path.join(directory_path, "*.txt")))
    if not files:
        raise FileNotFoundError(f"No .txt screenplay files found in: {directory_path}")

    episodes = []
    seen = {}
    for f in files:
        ep = parse_screenplay_file(f)
        if not ep.all_beats:
            logger.warning(f"{os.path.basename(f)}: 0 beats parsed (unsupported format?); skipped.")
            continue
        if ep.episode_number in seen:
            logger.warning(
                f"{os.path.basename(f)}: duplicate episode number {ep.episode_number} "
                f"(also {seen[ep.episode_number]}); skipped."
            )
            continue
        seen[ep.episode_number] = os.path.basename(f)
        episodes.append(ep)
    episodes.sort(key=lambda ep: ep.episode_number)
    return episodes


def format_episode_for_analysis(episode: Episode, include_camera: bool = False) -> str:
    """
    Renders episode beats into clean text with timestamps for LLM dramatic analysis.
    Focuses on DIALOGUE and ACTION to optimize tokens and clarity.
    """
    lines = [
        f"EPISODE {episode.episode_number}: {episode.logline}",
        f"Total Duration: {seconds_to_timestamp(episode.total_duration)} ({episode.total_duration:.1f}s)",
        "--- BEATS ---"
    ]

    for scene in episode.scenes:
        lines.append(f"\n[SCENE {scene.scene_number}: {scene.heading} | {scene.start_str} - {scene.end_str}]")
        for b in scene.beats:
            if b.beat_type == BeatType.CAMERA and not include_camera:
                continue
            if b.beat_type == BeatType.DIALOGUE:
                emo_str = f" ({b.emotion})" if b.emotion else ""
                lines.append(f"[{b.start_str} - {b.end_str}] {b.speaker}{emo_str}: {b.text}")
            elif b.beat_type == BeatType.ACTION:
                lines.append(f"[{b.start_str} - {b.end_str}] ACTION: {b.text}")
            elif b.beat_type == BeatType.SOUND:
                lines.append(f"[{b.start_str} - {b.end_str}] SFX: {b.text}")
            elif b.beat_type == BeatType.CAMERA and include_camera:
                lines.append(f"[{b.start_str} - {b.end_str}] CAMERA: {b.text}")

    return "\n".join(lines)


def format_segment_slice(
    episode: Episode, start_seconds: float, end_seconds: float, include_camera: bool = False
) -> str:
    """
    Renders the exact screenplay beats between start_seconds and end_seconds.
    Used by the auditor to inspect authentic dialogue and actions between hook and cliffhanger.
    """
    lines = []
    for b in episode.all_beats:
        if b.end_seconds > start_seconds - 0.1 and b.start_seconds < end_seconds + 0.1:
            if b.beat_type == BeatType.CAMERA and not include_camera:
                continue
            if b.beat_type == BeatType.DIALOGUE:
                emo_str = f" ({b.emotion})" if b.emotion else ""
                lines.append(f"[{b.start_str} - {b.end_str}] {b.speaker}{emo_str}: {b.text}")
            elif b.beat_type == BeatType.ACTION:
                lines.append(f"[{b.start_str} - {b.end_str}] ACTION: {b.text}")
            elif b.beat_type == BeatType.SOUND:
                lines.append(f"[{b.start_str} - {b.end_str}] SFX: {b.text}")
            elif b.beat_type == BeatType.CAMERA and include_camera:
                lines.append(f"[{b.start_str} - {b.end_str}] CAMERA: {b.text}")
    return "\n".join(lines)
