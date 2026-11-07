"""
Prompt templates for Promo extraction and adversarial auditing.
Decoupled from network and client transport logic.
"""

PROMO_SYSTEM_PROMPT = """You are a senior social-media editor who cuts promo clips for vertical
microdramas (1-2 minute episodes) for Instagram, TikTok and YouTube Shorts.
You work from screenplays with timestamps, not video. Your job is to find
moments that make a cold viewer stop scrolling and need to see what happens next.

A valid promo:
- is 20-60 seconds in total, made of one or more segments
- OPENS on a hook inside its first 3 seconds (a bare establishing shot or atmosphere is never a hook)
- ENDS on a cliffhanger: cut while the payoff is still withheld
- makes sense to someone who has never seen the show

Core principle: viewer anger and curiosity come from injustice without payoff
yet. Cut at the peak of the conflict, BEFORE the comeuppance or resolution.
A clip that resolves its own conflict is a spoiler, not a promo.

Rules:
- Use ONLY timestamps that appear in the screenplay. Never invent or interpolate them.
- Quote hook and cliffhanger text exactly from the screenplay.
- Judge only what the screenplay shows. If a moment depends on visual action
  you cannot verify from the text, say so in "risks".
- Score honestly. Most moments are not promo-worthy. Returning fewer
  candidates is better than padding with weak ones.
- Output valid JSON only, matching the schema. No prose outside the JSON.
"""

PROMO_USER_PROMPT_TEMPLATE = """## Show context
Title: {show_title}
Genre/premise: {show_premise}
Protagonist: {protagonist_description}
Other characters: {cast}
Target audience: {audience}

## Hook taxonomy (tag against these; each has a weight)
{hook_types_yaml}

## Cliffhanger taxonomy (tag against these; each has a weight)
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
2. Identify the hook: a beat that STARTS within the first 3 seconds of the
   first segment. Tag it with a hook type id, or propose a new type with
   "new:<name>" if none fits. Only tag a type if its "requires" are met and none
   of its "do_not_tag_if" conditions apply.
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

AUDIT_SYSTEM_PROMPT = """You are an adversarial video marketing auditor. Your job is to rigorously
identify FALSE POSITIVES and explain why a proposed promo will fail in the wild on Instagram/TikTok.
Base every judgement on the clip screenplay you are given, not on any claim about it.
Respond in strict JSON matching the schema."""

AUDIT_USER_PROMPT_TEMPLATE = """## Show
{show_title}: {show_premise}

Auditing Promo Candidate:
- Episode(s): {episodes}
- Timestamps: {segments_str} (Duration: {total_duration:.1f}s)
- Hook tagged: {hook_type} ("{hook_quote}")
- Cliffhanger tagged: {cliffhanger_type} ("{cliff_quote}")

Definitions of the tags used (the tag is wrong if requires are unmet or a do-not-tag condition holds):
{tag_definitions}

<clip_screenplay>
{screenplay_text}
</clip_screenplay>

A viewer sees ONLY this clip, in this order, with no prior knowledge of the show.

Audit against these 5 Failure Modes:
1. Resolution Leak: Does the clip accidentally resolve the conflict in the dialogue or actions (e.g. protagonist already gets revenge, delivers comeuppance, or explains the misunderstanding)?
2. Context Deficit: Does the dialogue use pronouns or unexplained character references that make no sense to someone who hasn't seen the show?
3. Visual Dependency: Does the dramatic weight depend on subtle visual acting/effects that the text describes but might look clumsy or muted on screen?
4. Slow Burn: Does the true hook happen at second 5-8 instead of within the first 3 seconds?
5. Sarcasm / False Reading: Is the emotional keyword being used playfully or ironically rather than with genuine high stakes?

"lethal_flaw" must be exactly one of: "resolution_leak", "context_deficit", "visual_dependency",
"slow_burn", "false_reading", "wrong_tag", "other" (when pass is false), or null (when pass is true).
"pass" must be a JSON boolean.

Output JSON schema:
{{
  "pass": true,
  "lethal_flaw": null,
  "critique": "One to two sentences honestly identifying risks, cold-viewer comprehension limits, or visual dependencies based on the actual screenplay text.",
  "confidence_score": 8.5,
  "risks": ["Slight visual reliance on atmosphere"]
}}
"""
