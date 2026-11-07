"""
Core domain data models for Kuku Promo Finder pipeline (Pydantic v2).
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, model_validator
from src.utils.timestamps import (
    parse_timestamp_to_seconds,
    seconds_to_timestamp,
)


class BeatType(str, Enum):
    CAMERA = "CAMERA"
    ACTION = "ACTION"
    DIALOGUE = "DIALOGUE"
    SOUND = "SOUND"


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
    duration: float = 0.0

    @model_validator(mode="after")
    def compute_duration(self) -> "Segment":
        if self.duration <= 0.0:
            self.duration = max(0.0, self.end_seconds - self.start_seconds)
        return self


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
    hook_strength: float = 7.0
    injustice_tension: float = 7.0
    cliffhanger_strength: float = 7.0
    standalone_clarity: float = 7.0
    payoff_withheld: float = 7.0
    composite_score: float = 0.0
    adjusted_score: float = 0.0
    diversity_penalty: float = 1.0
    audit_multiplier: float = 1.0

    def compute_composite_score(self, hook_weight: float = 1.0, cliff_weight: float = 1.0) -> float:
        """
        Single canonical scoring formula for the entire pipeline:
        Base = 0.30*hook + 0.25*cliffhanger + 0.20*injustice + 0.15*clarity + 0.10*payoff
        Composite = Base * hook_weight * cliff_weight
        """
        base = (
            0.30 * self.hook_strength
            + 0.25 * self.cliffhanger_strength
            + 0.20 * self.injustice_tension
            + 0.15 * self.standalone_clarity
            + 0.10 * self.payoff_withheld
        )
        self.composite_score = round(base * hook_weight * cliff_weight, 2)
        if self.adjusted_score == 0.0:
            self.adjusted_score = self.composite_score
        return self.composite_score


class QualityAudit(BaseModel):
    passed: bool = True
    flaw_type: Optional[str] = None
    critique: str = ""
    confidence_score: float = 8.0
    risks: List[str] = Field(default_factory=list)


class PromoCandidate(BaseModel):
    promo_id: str
    rank: Optional[int] = None
    promo_type: Literal["single_episode", "cross_episode"] = "single_episode"
    episodes: List[int] = Field(default_factory=list)
    segments: List[Segment] = Field(default_factory=list)
    total_duration: float = 0.0
    hook: HookInfo
    cliffhanger: CliffhangerInfo
    why_it_works: str = ""
    scores: PromoScores = Field(default_factory=PromoScores)
    quality_audit: Optional[QualityAudit] = None

    @model_validator(mode="after")
    def sync_total_duration(self) -> "PromoCandidate":
        if self.segments:
            calc_dur = sum(s.duration for s in self.segments)
            if self.total_duration <= 0.0 or abs(self.total_duration - calc_dur) > 0.5:
                self.total_duration = round(calc_dur, 2)
        return self

    @property
    def effective_score(self) -> float:
        return self.scores.adjusted_score if self.scores.adjusted_score > 0 else self.scores.composite_score

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
