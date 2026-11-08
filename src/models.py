"""
Core domain data models for Kuku Promo Finder pipeline (Pydantic v2).
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, model_validator, field_validator
from src.utils.timestamps import (
    parse_timestamp_to_seconds,
    seconds_to_timestamp,
)
from src.constants import (
    WEIGHT_HOOK,
    WEIGHT_CLIFFHANGER,
    WEIGHT_PAYOFF_WITHHELD,
    WEIGHT_INJUSTICE_TENSION,
    WEIGHT_STANDALONE_CLARITY,
    WEIGHT_CONVERSION_INTENT,
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
    episode: Optional[int] = None
    start: str
    end: str
    start_seconds: float
    end_seconds: float
    duration: float = 0.0

    @model_validator(mode="after")
    def compute_duration(self) -> "Segment":
        if self.duration <= 0.0:
            self.duration = max(0.0, self.end_seconds - self.start_seconds)
        self.duration = round(self.duration, 2)
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
    conversion_intent: float = 0.0
    composite_score: float = 0.0
    adjusted_score: float = 0.0
    diversity_penalty: float = 1.0
    audit_multiplier: float = 1.0

    @field_validator(
        "hook_strength", "injustice_tension", "cliffhanger_strength",
        "standalone_clarity", "payoff_withheld", "conversion_intent", mode="after",
    )
    @classmethod
    def _clamp_0_10(cls, v: float) -> float:
        return max(0.0, min(10.0, float(v)))

    def compute_composite_score(
        self,
        hook_weight: float = 1.0,
        cliff_weight: float = 1.0,
        weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Single canonical scoring formula for the entire pipeline, using editorial prior weights
        from src/constants.py:
        Base = 0.30*hook + 0.25*cliffhanger + 0.20*payoff_withheld + 0.15*injustice + 0.10*clarity
        If conversion_intent weight > 0, blend conversion_intent in as a separate term.
        Composite = Base * hook_weight * cliff_weight
        """
        w_hook = weights.get("hook", WEIGHT_HOOK) if weights else WEIGHT_HOOK
        w_cliff = weights.get("cliffhanger", WEIGHT_CLIFFHANGER) if weights else WEIGHT_CLIFFHANGER
        w_payoff = weights.get("payoff_withheld", WEIGHT_PAYOFF_WITHHELD) if weights else WEIGHT_PAYOFF_WITHHELD
        w_inj = weights.get("injustice_tension", WEIGHT_INJUSTICE_TENSION) if weights else WEIGHT_INJUSTICE_TENSION
        w_clarity = weights.get("standalone_clarity", WEIGHT_STANDALONE_CLARITY) if weights else WEIGHT_STANDALONE_CLARITY
        w_conv = weights.get("conversion_intent", WEIGHT_CONVERSION_INTENT) if weights else WEIGHT_CONVERSION_INTENT

        base = (
            w_hook * self.hook_strength
            + w_cliff * self.cliffhanger_strength
            + w_payoff * self.payoff_withheld
            + w_inj * self.injustice_tension
            + w_clarity * self.standalone_clarity
        )
        if w_conv > 0.0:
            base = (1.0 - w_conv) * base + w_conv * self.conversion_intent

        self.composite_score = round(base * hook_weight * cliff_weight, 2)
        if self.adjusted_score == 0.0:
            self.adjusted_score = self.composite_score
        return self.composite_score


class QualityAudit(BaseModel):
    passed: bool = True
    # "llm" = model read the clip screenplay; "rules" = offline lint (NOT a quality judgement);
    # "error" = the audit call failed and the candidate is unaudited; "not_audited" = excluded by --audit-top-n.
    method: Literal["llm", "rules", "error", "not_audited"] = "rules"
    audit_model: str = ""
    flaw_type: Optional[str] = None
    critique: str = ""
    confidence_score: float = 8.0
    conversion_intent: Optional[float] = None
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
    risks: List[str] = Field(default_factory=list)
    scores: PromoScores = Field(default_factory=PromoScores)
    quality_audit: Optional[QualityAudit] = None
    engine: str = ""
    model: str = ""
    extractor_model: str = ""
    trimmed_from_end: bool = False
    seconds_removed: float = 0.0
    audit_tier: Optional[int] = None
    judge_verdicts: List[Dict[str, Any]] = Field(default_factory=list)
    conversion_intent: Optional[float] = None
    conversion_reason: str = ""
    payoff_location: Optional[str] = None
    stages: List[str] = Field(default_factory=list)
    cold_read: Optional[Dict[str, Any]] = None
    audit_panel: Optional[Dict[str, Any]] = None
    rerank: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def sync_total_duration(self) -> "PromoCandidate":
        if self.segments:
            calc_dur = sum(s.duration for s in self.segments)
            if self.total_duration <= 0.0 or abs(self.total_duration - calc_dur) > 0.5:
                self.total_duration = round(calc_dur, 2)
        self.total_duration = round(self.total_duration, 2)
        return self

    @property
    def effective_score(self) -> float:
        return self.scores.adjusted_score if self.scores.adjusted_score > 0 else self.scores.composite_score

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
