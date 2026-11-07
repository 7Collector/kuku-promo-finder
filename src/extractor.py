"""
Promo candidate extraction engine.
Combines deterministic window analysis with LLM dramatic tagging.
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple
from src.models import (
    Episode,
    Beat,
    BeatType,
    Segment,
    HookInfo,
    CliffhangerInfo,
    PromoScores,
    PromoCandidate,
    seconds_to_timestamp,
    parse_timestamp_to_seconds,
)
from src.taxonomy import Taxonomy
from src.parser import format_episode_for_analysis
from src.llm_client import LLMClient, SYSTEM_PROMPT


USER_PROMPT_TEMPLATE = """## Show context
Title: {show_title}
Genre/premise: {show_premise}
Protagonist: {protagonist_description}
Target audience: {audience}

## Hook taxonomy (tag against these; each has a weight)
{hook_types_yaml}

## Cliffhanger taxonomy
{cliffhanger_types_yaml}

## Episode to analyze
Episode: {episode_id}
Duration: {episode_duration}

<screenplay>
{screenplay_text_with_timestamps}
</screenplay>

{previous_episode_summary}

## Task
Find up to {max_candidates} promo candidates in this episode.

For each candidate:
1. Choose one or more segments (start, end) copied from screenplay timestamps.
   Total duration must be 20-60s. Prefer ONE continuous segment. Add a short
   setup segment only if the hook cannot make sense cold without it.
2. Identify the hook: the exact moment within the first 3 seconds of the
   first segment. Tag it with a hook type id, or propose a new type with
   "new:<name>" if none fits.
3. Identify the cliffhanger: the final beat, tagged with a cliffhanger type id.
   State what payoff is being withheld.
4. Score each dimension from 0 to 10:
   - hook_strength: would it stop a scroller within 3 seconds?
   - injustice_tension: how strongly does it build anger/empathy?
   - cliffhanger_strength: how badly does the viewer need the next beat?
   - standalone_clarity: does it make sense to a first-time viewer, with
     no prior knowledge of the show?
   - payoff_withheld: 10 means the conflict is wide open, 0 means resolved
5. Write ONE line on why it works for a cold viewer.
6. List risks: spoilers, needs-context, visual-only dependence, sarcasm, etc.

Also return "rejected_near_misses": up to 3 moments that look promo-worthy
but fail, each with the reason (e.g. resolves its own conflict, needs too much
backstory).

## Output schema
{{
  "episode_id": "string",
  "candidates": [
    {{
      "segments": [{{"start": "mm:ss.ss", "end": "mm:ss.ss"}}],
      "total_seconds": 45.0,
      "hook": {{"type": "string", "timestamp": "mm:ss.ss", "text": "exact quote"}},
      "cliffhanger": {{"type": "string", "timestamp": "mm:ss.ss", "text": "exact quote", "withheld_payoff": "string"}},
      "scores": {{
        "hook_strength": 9,
        "injustice_tension": 9,
        "cliffhanger_strength": 8,
        "standalone_clarity": 8,
        "payoff_withheld": 9
      }},
      "why_it_works": "one line",
      "risks": ["string"]
    }}
  ],
  "rejected_near_misses": [{{"start": "mm:ss.ss", "end": "mm:ss.ss", "reason": "string"}}]
}}
"""


class PromoExtractor:
    def __init__(self, taxonomy: Taxonomy, llm_client: Optional[LLMClient] = None):
        self.taxonomy = taxonomy
        self.llm_client = llm_client or LLMClient()

    def extract_candidates_for_episode(
        self,
        episode: Episode,
        show_context: Dict[str, Any],
        prev_episode_summary: str = "",
        max_candidates: int = 3,
    ) -> List[PromoCandidate]:
        """
        Extracts promo candidates from a single episode.
        Uses LLM if API is available, otherwise uses deterministic heuristic extraction.
        """
        if self.llm_client.provider != "heuristic":
            try:
                candidates = self._extract_via_llm(
                    episode, show_context, prev_episode_summary, max_candidates
                )
                if candidates:
                    return candidates
            except Exception as e:
                print(f"[Warning] LLM extraction failed for Ep {episode.episode_number}: {e}. Falling back to heuristic extractor.")

        # Fallback / Default Deterministic Extraction
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

        user_prompt = USER_PROMPT_TEMPLATE.format(
            show_title=show_context.get("show_title", "Microdrama"),
            show_premise=show_context.get("premise", ""),
            protagonist_description=show_context.get("protagonist", {}).get("name", "Protagonist"),
            audience=show_context.get("target_platform", "TikTok / Instagram"),
            hook_types_yaml=self.taxonomy.to_yaml_string(),
            cliffhanger_types_yaml="",
            episode_id=str(episode.episode_number),
            episode_duration=seconds_to_timestamp(episode.total_duration),
            screenplay_text_with_timestamps=screenplay_text,
            previous_episode_summary=prev_summary_block,
            max_candidates=max_candidates,
        )

        resp = self.llm_client.generate_json(SYSTEM_PROMPT, user_prompt)
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
        """Validates and converts LLM JSON output to PromoCandidate."""
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

        # Enforce 20 to 60s total duration
        if not (18.0 <= total_sec <= 65.0):
            return None

        hook_data = rc.get("hook", {})
        h_ts_str = hook_data.get("timestamp", segments[0].start)
        h_ts_sec = parse_timestamp_to_seconds(h_ts_str)

        # Enforce hook within first 3.5s of first segment
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

        return PromoCandidate(
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
                withheld_payoff=cliff_data.get("withheld_payoff", "Conflict unresolved"),
            ),
            why_it_works=rc.get("why_it_works", "High stakes conflict cuts before resolution."),
            scores=scores,
        )

    def _extract_via_heuristics(
        self, episode: Episode, show_context: Dict[str, Any], max_candidates: int
    ) -> List[PromoCandidate]:
        """
        Deterministic, offline window scanner that finds high-impact promo moments.
        Scans all beats, pairs candidate hooks with candidate cliffhangers within 20-60s,
        and computes scoring based on emotional cues and dialogue tension.
        """
        beats = episode.all_beats
        if not beats:
            return []

        candidates_pool: List[PromoCandidate] = []

        # Find potential hook start beats (dialogue with high emotion or hook cue)
        for i, b_start in enumerate(beats):
            if b_start.beat_type != BeatType.DIALOGUE and b_start.beat_type != BeatType.ACTION:
                continue

            # Check hook match
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

            # Look forward for closing cliffhanger beats 20 to 60s later
            for j in range(i + 1, len(beats)):
                b_end = beats[j]
                dur = b_end.end_seconds - b_start.start_seconds
                if dur < 20.0:
                    continue
                if dur > 60.0:
                    break  # Exceeded max duration window

                # b_end should be dialogue or decisive action
                if b_end.beat_type not in [BeatType.DIALOGUE, BeatType.ACTION]:
                    continue

                end_text = f"{b_end.text} {b_end.speaker or ''} {b_end.emotion or ''}"
                matched_cliff = self.taxonomy.match_cliffhanger_cues(end_text)
                
                # Check dialogue density
                window_dialogues = [b for b in beats[i:j+1] if b.beat_type == BeatType.DIALOGUE]
                if len(window_dialogues) < 3:
                    continue

                cliff_id = matched_cliff["id"] if matched_cliff else "interrupted_retaliation"
                cliff_name = self.taxonomy.cliffhanger_by_id.get(cliff_id, {}).get("name", "Withheld Payoff")

                # Compute heuristic dimension scores (0-10)
                hook_strength = 8.5 if matched_hook else 7.5
                if is_emotional_lead:
                    hook_strength += 1.0

                injustice_tension = 8.0
                if any(w in (b_start.text + b_end.text).lower() for w in ["never", "beg", "servant", "marrying", "worthless", "kneel", "leave"]):
                    injustice_tension += 1.5

                cliff_strength = 8.5 if matched_cliff else 7.5
                clarity = 8.5
                payoff = 9.0

                # Formulate "why it works"
                spk = b_start.speaker or "Speaker"
                why = f"Cold viewers instantly lock onto {spk}'s confrontation; cuts right as tension peaks without giving away the outcome."

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
                candidates_pool.append(cand)

        # Sort by preliminary score and return top non-overlapping candidates
        candidates_pool.sort(
            key=lambda c: (
                c.scores.hook_strength * 0.35 +
                c.scores.cliffhanger_strength * 0.35 +
                c.scores.injustice_tension * 0.30
            ),
            reverse=True,
        )

        # Deduplicate heavily overlapping candidates within this episode
        selected: List[PromoCandidate] = []
        for cand in candidates_pool:
            overlap = False
            for s in selected:
                # check time overlap
                start_max = max(cand.segments[0].start_seconds, s.segments[0].start_seconds)
                end_min = min(cand.segments[0].end_seconds, s.segments[0].end_seconds)
                if end_min > start_max:
                    overlap_dur = end_min - start_max
                    if overlap_dur / min(cand.total_duration, s.total_duration) > 0.40:
                        overlap = True
                        break
            if not overlap:
                selected.append(cand)
            if len(selected) >= max_candidates:
                break

        return selected
