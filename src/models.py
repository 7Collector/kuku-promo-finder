"""
Core data models for the Kuku Promo Finder pipeline.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BeatType(str, Enum):
    CAMERA = "CAMERA"
    ACTION = "ACTION"
    DIALOGUE = "DIALOGUE"
    SOUND = "SOUND"


def parse_timestamp_to_seconds(ts: str) -> float:
    """Converts (mm:ss.ss) or mm:ss.ss or hh:mm:ss.ss into float seconds."""
    ts_clean = ts.strip("() ").strip()
    parts = ts_clean.split(":")
    if len(parts) == 2:
        return float(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return float(ts_clean)


def seconds_to_timestamp(sec: float) -> str:
    """Converts float seconds to mm:ss.ss format."""
    minutes = int(sec // 60)
    remaining_sec = sec % 60
    return f"{minutes:02d}:{remaining_sec:05.2f}"


class Beat(BaseModel):
    beat_type: BeatType
    speaker: Optional[str] = None
    emotion: Optional[str] = None
    text: str
    start_seconds: float
    end_seconds: float
    start_str: str
    end_str: str

    @property
    def duration(self) -> float:
        return max(0.0, self.end_seconds - self.start_seconds)


class Scene(BaseModel):
    scene_number: int
    heading: str
    start_seconds: float
    end_seconds: float
    start_str: str
    end_str: str
    beats: List[Beat] = Field(default_factory=list)


class Episode(BaseModel):
    episode_number: int
    episode_id: str
    logline: str
    continuity_notes: str = ""
    scenes: List[Scene] = Field(default_factory=list)
    total_duration: float = 0.0

    @property
    def all_beats(self) -> List[Beat]:
        beats = []
        for scene in self.scenes:
            beats.extend(scene.beats)
        return beats


class Segment(BaseModel):
    start: str
    end: str
    start_seconds: float
    end_seconds: float
    duration: float


class HookInfo(BaseModel):
    type: str
    name: str = ""
    timestamp: str
    timestamp_seconds: float
    quote: str
    psychological_trigger: str = ""


class CliffhangerInfo(BaseModel):
    type: str
    name: str = ""
    timestamp: str
    timestamp_seconds: float
    quote: str
    withheld_payoff: str = ""


class PromoScores(BaseModel):
    hook_strength: float = 0.0
    injustice_tension: float = 0.0
    cliffhanger_strength: float = 0.0
    standalone_clarity: float = 0.0
    payoff_withheld: float = 0.0
    composite_score: float = 0.0


class QualityAudit(BaseModel):
    passed: bool = True
    flaw_type: Optional[str] = None
    critique: str = ""
    confidence_score: float = 8.0
    risks: List[str] = Field(default_factory=list)


class PromoCandidate(BaseModel):
    promo_id: str
    rank: Optional[int] = None
    promo_type: str = "single_episode"  # 'single_episode' or 'cross_episode'
    episodes: List[int] = Field(default_factory=list)
    segments: List[Segment] = Field(default_factory=list)
    total_duration: float = 0.0
    hook: HookInfo
    cliffhanger: CliffhangerInfo
    why_it_works: str = ""
    scores: PromoScores = Field(default_factory=PromoScores)
    quality_audit: Optional[QualityAudit] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
