"""
Promo candidate extraction engine.
Combines deterministic window analysis with LLM dramatic tagging.
"""

from typing import List, Dict, Any, Optional
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
    parse_timestamp_to_seconds,
    seconds_to_timestamp,
    calculate_temporal_overlap,
)
from src.utils.logging import logger


class PromoExtractor:
    def __init__(self, taxonomy: Taxonomy, llm_provider: Optional[BaseLLMProvider] = None):
        self.taxonomy = taxonomy
        self.llm_provider = llm_provider or get_llm_provider()

    def extract_candidates_for_episode(
        self,
        episode: Episode,
        show_context: Dict[str, Any],
        prev_episode_summary: str = "",
        max_candidates: int = 3,
    ) -> List[PromoCandidate]:
        """
        Extracts promo candidates from a single episode.
        Calls LLM if live provider is active; falls back to deterministic heuristic window scanner.
        """
        if self.llm_provider.name != "heuristic":
            try:
                candidates = self._extract_via_llm(
                    episode, show_context, prev_episode_summary, max_candidates
                )
                if candidates:
                    return candidates
            except Exception as e:
                logger.warning(f"LLM extraction failed for Ep {episode.episode_number}: {e}. Falling back to heuristic scanner.")

        return self._extract_via_heuristics(episode, show_context, max_candidates)

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

        user_prompt = PROMO_USER_PROMPT_TEMPLATE.format(
            show_title=show_context.get("show_title", "Microdrama"),
            show_premise=show_context.get("premise", ""),
            protagonist_description=show_context.get("protagonist", {}).get("name", "Protagonist"),
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

        results: List[PromoCandidate] = []
        for idx, rc in enumerate(raw_candidates):
            parsed_cand = self._convert_raw_to_candidate(rc, episode, idx)
            if parsed_cand:
                results.append(parsed_cand)

        return results

    def _convert_raw_to_candidate(
        self, rc: Dict[str, Any], episode: Episode, candidate_index: int
    ) -> Optional[PromoCandidate]:
        segments_data = rc.get("segments", [])
        if not segments_data:
            return None

        segments: List[Segment] = []
        total_sec = 0.0
        for seg in segments_data:
            s_str = seg.get("start", "")
            e_str = seg.get("end", "")
            s_sec = parse_timestamp_to_seconds(s_str)
            e_sec = parse_timestamp_to_seconds(e_str)
            dur = max(0.0, e_sec - s_sec)
            total_sec += dur
            segments.append(
                Segment(
                    start=s_str,
                    end=e_str,
                    start_seconds=s_sec,
                    end_seconds=e_sec,
                    duration=dur,
                )
            )

        if not (18.0 <= total_sec <= 65.0):
            return None

        hook_data = rc.get("hook", {})
        h_ts_str = hook_data.get("timestamp", segments[0].start)
        h_ts_sec = parse_timestamp_to_seconds(h_ts_str)

        if (h_ts_sec - segments[0].start_seconds) > 3.5:
            return None

        cliff_data = rc.get("cliffhanger", {})
        c_ts_str = cliff_data.get("timestamp", segments[-1].end)
        c_ts_sec = parse_timestamp_to_seconds(c_ts_str)

        scores_dict = rc.get("scores", {})
        scores = PromoScores(
            hook_strength=float(scores_dict.get("hook_strength", 7.0)),
            injustice_tension=float(scores_dict.get("injustice_tension", 7.0)),
            cliffhanger_strength=float(scores_dict.get("cliffhanger_strength", 7.0)),
            standalone_clarity=float(scores_dict.get("standalone_clarity", 7.0)),
            payoff_withheld=float(scores_dict.get("payoff_withheld", 7.0)),
        )

        hook_type = hook_data.get("type", "public_humiliation")
        cliff_type = cliff_data.get("type", "interrupted_retaliation")

        cand = PromoCandidate(
            promo_id=f"ep{episode.episode_number:02d}_cand_{candidate_index+1}",
            promo_type="single_episode",
            episodes=[episode.episode_number],
            segments=segments,
            total_duration=total_sec,
            hook=HookInfo(
                type=hook_type,
                name=self.taxonomy.hook_by_id.get(hook_type, {}).get("name", hook_type),
                timestamp=h_ts_str,
                timestamp_seconds=h_ts_sec,
                quote=hook_data.get("text", ""),
                psychological_trigger=self.taxonomy.hook_by_id.get(hook_type, {}).get("psychological_driver", ""),
            ),
            cliffhanger=CliffhangerInfo(
                type=cliff_type,
                name=self.taxonomy.cliffhanger_by_id.get(cliff_type, {}).get("name", cliff_type),
                timestamp=c_ts_str,
                timestamp_seconds=c_ts_sec,
                quote=cliff_data.get("text", ""),
                withheld_payoff=cliff_data.get("withheld_payoff", "Conflict cuts before resolution"),
            ),
            why_it_works=rc.get("why_it_works", "High stakes conflict cuts before resolution."),
            scores=scores,
        )

        h_w = self.taxonomy.get_hook_weight(hook_type)
        c_w = self.taxonomy.get_cliffhanger_weight(cliff_type)
        cand.scores.compute_composite_score(h_w, c_w)
        return cand

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

            hook_id = matched_hook["id"] if matched_hook else "public_humiliation"
            hook_name = self.taxonomy.hook_by_id.get(hook_id, {}).get("name", "Injustice Hook")
            hook_driver = self.taxonomy.hook_by_id.get(hook_id, {}).get("psychological_driver", "High-status mistreatment")

            for j in range(i + 1, len(beats)):
                b_end = beats[j]
                dur = b_end.end_seconds - b_start.start_seconds
                if dur < 20.0:
                    continue
                if dur > 60.0:
                    break

                if b_end.beat_type not in [BeatType.DIALOGUE, BeatType.ACTION]:
                    continue

                end_text = f"{b_end.text} {b_end.speaker or ''} {b_end.emotion or ''}"
                matched_cliff = self.taxonomy.match_cliffhanger_cues(end_text)

                window_dialogues = [b for b in beats[i:j+1] if b.beat_type == BeatType.DIALOGUE]
                if len(window_dialogues) < 3:
                    continue

                cliff_id = matched_cliff["id"] if matched_cliff else "interrupted_retaliation"
                cliff_name = self.taxonomy.cliffhanger_by_id.get(cliff_id, {}).get("name", "Withheld Payoff")

                hook_strength = 8.5 if matched_hook else 7.5
                if is_emotional_lead:
                    hook_strength += 1.0

                injustice_tension = 8.0
                if any(w in (b_start.text + b_end.text).lower() for w in ["never", "beg", "servant", "marrying", "worthless", "kneel", "leave"]):
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
                            start=b_start.start_str,
                            end=b_end.end_str,
                            start_seconds=b_start.start_seconds,
                            end_seconds=b_end.end_seconds,
                            duration=dur,
                        )
                    ],
                    total_duration=dur,
                    hook=HookInfo(
                        type=hook_id,
                        name=hook_name,
                        timestamp=b_start.start_str,
                        timestamp_seconds=b_start.start_seconds,
                        quote=b_start.text[:120],
                        psychological_trigger=hook_driver,
                    ),
                    cliffhanger=CliffhangerInfo(
                        type=cliff_id,
                        name=cliff_name,
                        timestamp=b_end.end_str,
                        timestamp_seconds=b_end.end_seconds,
                        quote=b_end.text[:120],
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
        for cand in candidates_pool:
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
