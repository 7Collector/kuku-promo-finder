"""
Promo candidate extraction engine.
Combines deterministic window analysis with LLM dramatic tagging.
"""

import threading
from collections import Counter
from typing import List, Dict, Any, Optional, Tuple
from src.constants import CLIFF_WINDOW, EPS, HOOK_WINDOW, MAX_DURATION, MIN_DURATION
from src.validation import find_quote_beat, snap_to_beat_edge, spoken_beats
from src.models import (
    Episode,
    Beat,
    BeatType,
    Segment,
    HookInfo,
    CliffhangerInfo,
    PromoScores,
    PromoCandidate,
)
from src.taxonomy import Taxonomy
from src.parser import format_episode_for_analysis
from src.providers.base import BaseLLMProvider
from src.providers.factory import get_llm_provider
from src.prompts import PROMO_SYSTEM_PROMPT, PROMO_USER_PROMPT_TEMPLATE
from src.utils.timestamps import (
    try_parse_timestamp,
    seconds_to_timestamp,
    calculate_temporal_overlap,
)
from src.utils.logging import logger


class PromoExtractor:
    def __init__(self, taxonomy: Taxonomy, llm_provider: Optional[BaseLLMProvider] = None):
        self.taxonomy = taxonomy
        self.llm_provider = llm_provider or get_llm_provider()
        self._lock = threading.Lock()
        # Provenance and diagnostics, surfaced in run metadata.
        self.failures: Dict[int, str] = {}           # episode -> error (LLM call failed after retries)
        self.drop_reasons: Counter = Counter()        # why LLM candidates were rejected by validation
        self.dropped: List[Dict[str, Any]] = []       # the rejected candidates themselves
        self.near_misses: List[Dict[str, Any]] = []   # model-reported near misses, per episode

    def extract_candidates_for_episode(
        self,
        episode: Episode,
        show_context: Dict[str, Any],
        prev_episode_summary: str = "",
        max_candidates: int = 3,
    ) -> List[PromoCandidate]:
        """
        Extracts promo candidates from a single episode with the active provider.
        A live provider that fails is recorded in `self.failures` and yields no candidates:
        output from a different engine is never substituted silently.
        """
        if not self.llm_provider.is_live:
            cands = self._extract_via_heuristics(episode, show_context, max_candidates)
        else:
            try:
                cands = self._extract_via_llm(episode, show_context, prev_episode_summary, max_candidates)
            except Exception as e:
                logger.error(f"Extraction failed for Ep {episode.episode_number}: {e}")
                with self._lock:
                    self.failures[episode.episode_number] = str(e)
                return []
        for c in cands:
            c.engine = self.llm_provider.name
            c.model = self.llm_provider.model
        return cands

    @staticmethod
    def _cast_line(show_context: Dict[str, Any]) -> str:
        names = []
        for ant in show_context.get("antagonists", []) or []:
            if ant.get("name"):
                names.append(f"{ant['name']} (antagonist: {ant.get('role', '')})".strip())
        ml = show_context.get("male_lead") or {}
        if ml.get("name"):
            names.append(f"{ml['name']} ({ml.get('role', 'male lead')})")
        return "; ".join(names) or "(none listed)"

    def _extract_via_llm(
        self,
        episode: Episode,
        show_context: Dict[str, Any],
        prev_episode_summary: str,
        max_candidates: int,
    ) -> List[PromoCandidate]:
        screenplay_text = format_episode_for_analysis(episode, include_camera=False)
        prev_summary_block = (
            f"<previous_episode_summary>\n{prev_episode_summary}\n</previous_episode_summary>"
            if prev_episode_summary
            else ""
        )
        protagonist = show_context.get("protagonist", {}) or {}
        protagonist_desc = protagonist.get("name", "Protagonist")
        if protagonist.get("archetype"):
            protagonist_desc += f" - {protagonist['archetype']}"

        user_prompt = PROMO_USER_PROMPT_TEMPLATE.format(
            show_title=show_context.get("show_title", "Microdrama"),
            show_premise=show_context.get("premise", ""),
            protagonist_description=protagonist_desc,
            cast=self._cast_line(show_context),
            audience=show_context.get("target_platform", "TikTok / Instagram"),
            hook_types_yaml=self.taxonomy.hooks_to_yaml_string(),
            cliffhanger_types_yaml=self.taxonomy.cliffhangers_to_yaml_string(),
            episode_id=str(episode.episode_number),
            episode_duration=seconds_to_timestamp(episode.total_duration),
            screenplay_text_with_timestamps=screenplay_text,
            previous_episode_summary=prev_summary_block,
            max_candidates=max_candidates,
        )

        resp = self.llm_provider.generate_json(PROMO_SYSTEM_PROMPT, user_prompt)
        raw_candidates = resp.get("candidates", [])
        if not isinstance(raw_candidates, list):
            raise ValueError("'candidates' is not a list")

        with self._lock:
            for nm in resp.get("rejected_near_misses", []) or []:
                if isinstance(nm, dict):
                    self.near_misses.append({"episode": episode.episode_number, **nm})

        results: List[PromoCandidate] = []
        for idx, rc in enumerate(raw_candidates[:max_candidates]):
            cand, reason = self._convert_raw_to_candidate(rc, episode, idx)
            if cand:
                results.append(cand)
            else:
                with self._lock:
                    self.drop_reasons[reason] += 1
                    self.dropped.append({"episode": episode.episode_number, "reason": reason, "raw": rc})
        return results

    def _convert_raw_to_candidate(
        self, rc: Dict[str, Any], episode: Episode, candidate_index: int
    ) -> Tuple[Optional[PromoCandidate], str]:
        """
        Turns one model proposal into a validated PromoCandidate, or (None, reason).
        Cut points are snapped to authentic beat edges (tolerance SNAP_TOLERANCE) or rejected;
        quotes must exist in the screenplay; scores are clamped; types are normalized.
        """
        if not isinstance(rc, dict):
            return None, "candidate is not an object"
        segments_data = rc.get("segments") or []
        if not isinstance(segments_data, list) or not segments_data:
            return None, "no segments"

        segments: List[Segment] = []
        for seg in segments_data:
            if not isinstance(seg, dict):
                return None, "malformed segment"
            s_sec = try_parse_timestamp(seg.get("start"))
            e_sec = try_parse_timestamp(seg.get("end"))
            if s_sec is None or e_sec is None:
                return None, "invalid timestamp"
            b_start = snap_to_beat_edge(episode, s_sec, "start")
            b_end = snap_to_beat_edge(episode, e_sec, "end")
            if b_start is None or b_end is None:
                return None, "cut point is not on a real beat edge"
            if b_end.end_seconds <= b_start.start_seconds:
                return None, "segment end before start"
            segments.append(Segment(
                episode=episode.episode_number,
                start=b_start.start_str, end=b_end.end_str,
                start_seconds=b_start.start_seconds, end_seconds=b_end.end_seconds,
            ))

        total_sec = round(sum(s.duration for s in segments), 2)
        if not (MIN_DURATION - EPS <= total_sec <= MAX_DURATION + EPS):
            return None, "duration outside 20-60s"

        hook_data = rc.get("hook") or {}
        cliff_data = rc.get("cliffhanger") or {}
        hook_quote = str(hook_data.get("text", "")).strip()
        cliff_quote = str(cliff_data.get("text", "")).strip()

        first, last = segments[0], segments[-1]
        beats = spoken_beats(episode)
        hook_beat = find_quote_beat(
            [b for b in beats if first.start_seconds - EPS <= b.start_seconds <= first.start_seconds + HOOK_WINDOW + EPS],
            hook_quote,
        )
        if hook_beat is None:
            return None, "hook quote not in a beat starting within 3s of the cut"
        cliff_beat = find_quote_beat(
            [b for b in beats if last.start_seconds - EPS <= b.start_seconds
             and last.end_seconds - CLIFF_WINDOW <= b.end_seconds <= last.end_seconds + EPS],
            cliff_quote,
        )
        if cliff_beat is None:
            return None, "cliffhanger quote not in the last 6s of the clip"

        scores_dict = rc.get("scores") or {}
        try:
            scores = PromoScores(**{
                k: float(scores_dict.get(k, 5.0))
                for k in ("hook_strength", "injustice_tension", "cliffhanger_strength",
                          "standalone_clarity", "payoff_withheld")
            })
        except (TypeError, ValueError):
            return None, "non-numeric scores"

        hook_type = self.taxonomy.normalize_type(hook_data.get("type", ""), "hook", "new:unspecified")
        cliff_type = self.taxonomy.normalize_type(cliff_data.get("type", ""), "cliffhanger", "new:unspecified")
        risks = rc.get("risks") or []

        cand = PromoCandidate(
            promo_id=f"ep{episode.episode_number:02d}_cand_{candidate_index+1}",
            promo_type="single_episode",
            episodes=[episode.episode_number],
            segments=segments,
            total_duration=total_sec,
            hook=HookInfo(
                type=hook_type,
                name=self.taxonomy.hook_by_id.get(hook_type, {}).get("name", hook_type),
                timestamp=hook_beat.start_str,
                timestamp_seconds=hook_beat.start_seconds,
                quote=hook_quote,
                psychological_trigger=self.taxonomy.hook_by_id.get(hook_type, {}).get("psychological_driver", ""),
            ),
            cliffhanger=CliffhangerInfo(
                type=cliff_type,
                name=self.taxonomy.cliffhanger_by_id.get(cliff_type, {}).get("name", cliff_type),
                timestamp=cliff_beat.end_str,
                timestamp_seconds=cliff_beat.end_seconds,
                quote=cliff_quote,
                withheld_payoff=str(cliff_data.get("withheld_payoff", "")),
            ),
            why_it_works=str(rc.get("why_it_works", "")),
            risks=[str(r) for r in risks] if isinstance(risks, list) else [str(risks)],
            scores=scores,
        )
        cand.scores.compute_composite_score(
            self.taxonomy.get_hook_weight(hook_type), self.taxonomy.get_cliffhanger_weight(cliff_type)
        )
        return cand, ""

    def _extract_via_heuristics(
        self, episode: Episode, show_context: Dict[str, Any], max_candidates: int
    ) -> List[PromoCandidate]:
        beats = episode.all_beats
        if not beats:
            return []

        candidates_pool: List[PromoCandidate] = []

        for i, b_start in enumerate(beats):
            if b_start.beat_type not in [BeatType.DIALOGUE, BeatType.ACTION]:
                continue

            start_text = f"{b_start.text} {b_start.speaker or ''} {b_start.emotion or ''}"
            matched_hook = self.taxonomy.match_hook_cues(start_text)

            emo = (b_start.emotion or "").lower()
            is_emotional_lead = any(
                w in emo for w in [
                    "cold", "commanding", "blunt", "shaken", "heartbroken",
                    "gloating", "betrayed", "cruel", "furious", "unforgiving",
                    "vindictive", "mocking", "sneering", "steely", "threatening"
                ]
            )

            if not (matched_hook or is_emotional_lead):
                continue

            hook_id = None
            if matched_hook:
                hook_id = matched_hook["id"]
            else:
                start_lower = start_text.lower()
                if any(w in start_lower for w in ["wedding", "sister", "fiancé", "replace you", "marrying", "divorce", "abandon"]):
                    hook_id = "intimate_betrayal"
                elif any(w in start_lower for w in ["slap", "shove", "grab", "collar", "strike", "drag"]):
                    hook_id = "physical_aggression"
                elif any(w in start_lower for w in ["beggar", "peasant", "worthless", "dirt", "servant", "filth", "lowborn", "rubbish"]):
                    hook_id = "class_status_contempt"
                elif any(w in start_lower for w in ["thief", "stole", "blame", "fault", "lie"]):
                    hook_id = "unjust_accusation"
                elif any(w in start_lower for w in ["never", "refuse", "not afraid", "kill me"]):
                    hook_id = "life_or_death_defiance"
                elif any(w in start_lower for w in ["who do you think", "afford this", "security", "commander", "duke"]):
                    hook_id = "hidden_identity_irony"
                else:
                    hook_id = "public_humiliation"

            hook_name = self.taxonomy.hook_by_id.get(hook_id, {}).get("name", "Injustice Hook")
            hook_driver = self.taxonomy.hook_by_id.get(hook_id, {}).get("psychological_driver", "High-status mistreatment")

            for j in range(i + 1, len(beats)):
                b_end = beats[j]
                dur = b_end.end_seconds - b_start.start_seconds
                if dur < MIN_DURATION:
                    continue
                if dur > MAX_DURATION:
                    break

                if b_end.beat_type not in [BeatType.DIALOGUE, BeatType.ACTION]:
                    continue

                end_text = f"{b_end.text} {b_end.speaker or ''} {b_end.emotion or ''}"
                matched_cliff = self.taxonomy.match_cliffhanger_cues(end_text)
                if not matched_cliff and j > i:
                    prev_beat = beats[j - 1]
                    prev_text = f"{prev_beat.text} {prev_beat.speaker or ''} {prev_beat.emotion or ''}"
                    matched_cliff = self.taxonomy.match_cliffhanger_cues(prev_text)

                window_dialogues = [b for b in beats[i:j+1] if b.beat_type == BeatType.DIALOGUE]
                if len(window_dialogues) < 3:
                    continue

                cliff_id = None
                if matched_cliff:
                    cliff_id = matched_cliff["id"]
                else:
                    combined_end = (end_text + " " + (beats[j-1].text if j > i else "")).lower()
                    if any(w in combined_end for w in ["door", "doors", "halt", "stop right", "who dares", "savior", "steps between", "arrives"]):
                        cliff_id = "unexpected_savior_arrival"
                    elif any(w in combined_end for w in ["seal", "ring", "heir", "duke", "commander", "truth", "document", "watch"]):
                        cliff_id = "truth_half_revealed"
                    elif any(w in combined_end for w in ["or else", "choose", "three seconds", "last chance", "die"]):
                        cliff_id = "mortal_ultimatum"
                    elif any(w in combined_end for w in ["swings", "raises blade", "raises hand", "lunges", "strikes"]):
                        cliff_id = "mid_action_cut"
                    elif any(w in combined_end for w in ["regret", "words carefully", "touch", "not finished", "warn", "pay"]):
                        cliff_id = "interrupted_retaliation"
                    elif any(w in combined_end for w in ["steps forward", "shadows", "stranger"]):
                        cliff_id = "unexpected_arrival"
                    else:
                        cliff_id = "interrupted_retaliation"

                cliff_name = self.taxonomy.cliffhanger_by_id.get(cliff_id, {}).get("name", "Withheld Payoff")

                hook_strength = 8.5 if matched_hook else 7.5
                if is_emotional_lead:
                    hook_strength += 1.0

                injustice_tension = 8.0
                injustice_tokens = [
                    "never", "beg", "servant", "marrying", "marry", "worthless", "kneel", "leave",
                    "betray", "altar", "ruined", "ruin", "steal", "stole", "arrest", "theft", "slap", "shove", "dirt"
                ]
                if any(w in (b_start.text + b_end.text).lower() for w in injustice_tokens):
                    injustice_tension += 1.5

                cliff_strength = 8.5 if matched_cliff else 7.5
                clarity = 8.5
                payoff = 9.0

                # Improved cold viewer explanation avoiding literal "Speaker"
                if b_start.speaker:
                    why = f"Cold viewers instantly lock onto {b_start.speaker}'s confrontation; cuts right as tension peaks without resolving."
                else:
                    why = "Cold viewers lock onto the sudden confrontation; cuts at the peak of injustice before any payoff."

                cand = PromoCandidate(
                    promo_id=f"ep{episode.episode_number:02d}_{b_start.start_str.replace(':', '')}_{b_end.end_str.replace(':', '')}",
                    promo_type="single_episode",
                    episodes=[episode.episode_number],
                    segments=[
                        Segment(
                            episode=episode.episode_number,
                            start=b_start.start_str,
                            end=b_end.end_str,
                            start_seconds=b_start.start_seconds,
                            end_seconds=b_end.end_seconds,
                            duration=round(dur, 2),
                        )
                    ],
                    total_duration=round(dur, 2),
                    hook=HookInfo(
                        type=hook_id,
                        name=hook_name,
                        timestamp=b_start.start_str,
                        timestamp_seconds=b_start.start_seconds,
                        quote=b_start.text,
                        psychological_trigger=hook_driver,
                    ),
                    cliffhanger=CliffhangerInfo(
                        type=cliff_id,
                        name=cliff_name,
                        timestamp=b_end.end_str,
                        timestamp_seconds=b_end.end_seconds,
                        quote=b_end.text,
                        withheld_payoff="Conflict cuts before resolution or comeuppance.",
                    ),
                    why_it_works=why,
                    scores=PromoScores(
                        hook_strength=min(10.0, hook_strength),
                        injustice_tension=min(10.0, injustice_tension),
                        cliffhanger_strength=min(10.0, cliff_strength),
                        standalone_clarity=min(10.0, clarity),
                        payoff_withheld=min(10.0, payoff),
                    ),
                )

                # Use canonical scoring method
                h_w = self.taxonomy.get_hook_weight(hook_id)
                c_w = self.taxonomy.get_cliffhanger_weight(cliff_id)
                cand.scores.compute_composite_score(h_w, c_w)

                candidates_pool.append(cand)

        # Sort using canonical composite score
        candidates_pool.sort(key=lambda c: c.scores.composite_score, reverse=True)

        selected: List[PromoCandidate] = []
        selected_hooks = set()

        # Pass 1: Select highest-scoring candidates across diverse hook archetypes
        for cand in candidates_pool:
            if cand.hook.type in selected_hooks:
                continue
            overlap = False
            for s in selected:
                _, ratio = calculate_temporal_overlap(
                    cand.segments[0].start_seconds,
                    cand.segments[0].end_seconds,
                    s.segments[0].start_seconds,
                    s.segments[0].end_seconds,
                )
                if ratio > 0.40:
                    overlap = True
                    break
            if not overlap:
                selected.append(cand)
                selected_hooks.add(cand.hook.type)
                if len(selected) >= max_candidates:
                    break

        # Pass 2: Fill remaining quota if needed
        if len(selected) < max_candidates:
            for cand in candidates_pool:
                if cand in selected:
                    continue
                overlap = False
                for s in selected:
                    _, ratio = calculate_temporal_overlap(
                        cand.segments[0].start_seconds,
                        cand.segments[0].end_seconds,
                        s.segments[0].start_seconds,
                        s.segments[0].end_seconds,
                    )
                    if ratio > 0.40:
                        overlap = True
                        break
                if not overlap:
                    selected.append(cand)
                    if len(selected) >= max_candidates:
                        break

        return selected
