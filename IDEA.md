# IDEA: Promo Finder for Microdrama Screenplays

## Problem Choice & Strategic Framing

**Problem 1: Find the Promos.**
In the fast-growing vertical microdrama ecosystem (1–2 minute episodes, TikTok/Reels/Shorts format), promo acquisition ads are the lifeblood of customer acquisition. Today, human editors watch every episode manually.

We frame this as a **Psychological Hook & Injustice Pipeline**:
Microdramas thrive on high emotional asymmetry—specifically, **injustice without immediate resolution** ("blood boils": public humiliation, slap, class contempt, unprovoked betrayal) paired with **withheld catharsis** (cutting right before the comeuppance or rescue). 

Our architecture combines:
1. **Deterministic Code / Physical Constraints**: Absolute timestamp verification, strict 20–60s duration windows, hook ≤ 3s enforcement, and embedding-based diversity reranking (MMR).
2. **LLM Dramatic Judgment**: Hook & cliffhanger taxonomy classification, cold-viewer stand-alone comprehension, withheld-payoff evaluation, and adversarial self-critique.
3. **Pluggable Taxonomy**: Zero hardcoded show logic; switching to a new show during the interview only requires a lightweight YAML config.

---

## The Hook & Cliffhanger Taxonomy

### 1. Hook Taxonomy (The "Blood Boils" Family)
- **`public_humiliation`** (Weight 1.0): Protagonist mocked or belittled in front of peers/crowd.
- **`physical_aggression`** (Weight 0.95): Slap, push, drink thrown, physical violation.
- **`intimate_betrayal`** (Weight 0.95): Betrayal by fiancé, spouse, or parent at a pivotal moment (e.g., wedding).
- **`class_status_contempt`** (Weight 0.90): Sneering disdain treating the protagonist as dirt/servant.
- **`hidden_identity_irony`** (Weight 0.90): Antagonist insults protagonist, blind to their true royal/wealthy identity.
- **`unjust_accusation`** (Weight 0.85): Innocent protagonist framed or blamed while villain smirks.

### 2. Cliffhanger Taxonomy (The "Payoff Withheld" Family)
- **`interrupted_retaliation`** (Weight 1.0): Protagonist's eyes turn cold / starts to counterattack, cut right before strike.
- **`unexpected_savior_arrival`** (Weight 0.95): Powerful benefactor / tycoon / commander arrives just as protagonist is cornered.
- **`truth_half_revealed`** (Weight 0.90): Secret lineage, DNA test, or royal token revealed, cut before reaction.
- **`mortal_ultimatum`** (Weight 0.85): Impossible choice with immediate stakes presented.

---

## System Architecture: The 4-Stage Pipeline

```
[Screenplays (.txt)]
        │
        ▼
[Stage 1: Deterministic Screenplay Parser]
   • Structured Scene/Dialogue/Action/Camera Beats
   • Precise millisecond timestamps
        │
        ▼
[Stage 2: LLM Candidate Discovery & Tagging]
   • Prompt with Hook & Cliffhanger Taxonomy
   • Evaluates 5 dimensions: Hook, Injustice, Cliffhanger, Standalone Clarity, Payoff Withheld
   • Identifies Single-Episode Candidates + Cross-Episode Composites (Setup + Climax)
        │
        ▼
[Stage 3: Deterministic Rule Validator & Diversity Reranker]
   • Code checks: Total duration 20–60s, hook ≤ 3.0s, timestamps exist in text
   • Composite continuity verification
   • MMR (Maximal Marginal Relevance) / hook-type penalization to prevent 10 identical slap scenes
        │
        ▼
[Stage 4: Adversarial Self-Critique & Honest Quality Check]
   • Evaluates failure modes: Resolution leaks, context deficits, visual-only dependencies
   • Produces ranked top promos with "why it works" and actionable quality warnings
```

---

## Detailed Stage Breakdown

### Stage 1: Deterministic Parse
- Ingests all 50 screenplay files (`assets/I Married a Broken Soldier. He was a Duke/`).
- Extracts:
  - Episode metadata (Episode number, logline, continuity notes).
  - Scenes (Scene number, heading, start/end timestamps).
  - Granular beats (Type: `DIALOGUE` / `ACTION` / `CAMERA`, character, emotion cue, text, start timestamp, end timestamp).
- Normalizes timestamps to floating-point seconds and standardized `mm:ss.ss` string formats.

### Stage 2: LLM Dramatic Analysis
- Ingests structured episode beats + previous episode logline context.
- Identifies candidates meeting the 20–60s constraint.
- Labels hooks and cliffhangers against the taxonomy.
- Scores candidates (0–10 scale) on:
  - `hook_strength`
  - `injustice_tension`
  - `cliffhanger_strength`
  - `standalone_clarity`
  - `payoff_withheld`

### Stage 3: Cross-Episode Composites
- Combines setup from earlier episodes (e.g., establishing Juliana's noble heart or wedding humiliation) with high-octane confrontation in later episodes (e.g., the Duke defending her).
- Ensures Segment A (5–12s setup) + Segment B (20–45s climax) totals 25–55s.

### Stage 4: Code Validation, Scoring & Reranking
- **Score formula**:
  $$\text{Base Score} = 0.30 \times \text{hook} + 0.25 \times \text{cliffhanger} + 0.20 \times \text{injustice} + 0.15 \times \text{clarity} + 0.10 \times \text{payoff}$$
  $$\text{Final Score} = \text{Base Score} \times \text{taxonomy\_weight}$$
- **Deduplication & Diversity**:
  - Drops candidates with >50% timestamp overlap within the same episode.
  - Applies a diversity penalty to successive picks of the same hook type.

### Stage 5: Adversarial Quality Check (Where AI Got It Wrong)
- Runs a specialized critique prompt on the top candidates to detect:
  1. *Resolution leak* (the clip inadvertently resolves the tension).
  2. *Context deficit* (inside jokes or pronouns that baffle cold viewers).
  3. *Visual dependency* (cinematography actions that cannot be guaranteed from text alone).
  4. *Slow burn* (dramatic peak arrives too late for TikTok attention spans).

---

## Output Contract

Each promo in the final output (JSON + Markdown) contains:
```json
{
  "rank": 1,
  "promo_id": "promo_ep01_01",
  "type": "single_episode",
  "episode": 1,
  "segments": [
    {"start": "00:11.00", "end": "00:52.40", "duration_sec": 41.4}
  ],
  "hook": {
    "type": "intimate_betrayal",
    "timestamp": "00:11.30",
    "quote": "You should turn around, Juliana.",
    "psychological_trigger": "Altar betrayal in front of society"
  },
  "cliffhanger": {
    "type": "interrupted_retaliation",
    "timestamp": "00:49.00",
    "quote": "Gerald turns his back as Juliana reaches out",
    "withheld_payoff": "Will Juliana accept exile or does someone intervene?"
  },
  "why_it_works": "Cold scrollers immediately understand the universal sting of wedding betrayal; cuts right before Juliana breaks down.",
  "scores": {
    "composite_score": 9.2,
    "hook_strength": 9.5,
    "injustice_tension": 9.5,
    "cliffhanger_strength": 9.0,
    "standalone_clarity": 9.0,
    "payoff_withheld": 9.0
  },
  "quality_audit": {
    "pass": true,
    "risks": ["Slight visual reliance on cathedral atmosphere"],
    "cold_viewer_clarity": "High"
  }
}
```

---

## Tech Stack & Architecture

- **Language**: Python 3.10+
- **LLM Layer**: Swappable LLM interface (supports Gemini API, Claude API, OpenAI, or local Ollama). Zero vector database required; fits cleanly in in-memory execution.
- **Frontend / Review Tool**: Clean Streamlit web dashboard allowing editors to preview promo segments, filter by hook type, inspect exact quotes, and review critique notes.
- **CLI**: Self-contained runner script `python run.py --input-dir assets/... --output outputs/promos.json`.

---

## Alignment with Kuku Evaluation Criteria

1. **Problem choice & framing**: Directly attacks the viral user acquisition mechanic (rage-bait injustice + withheld resolution).
2. **Approach & scale**: Strictly splits deterministic rules (code) from semantic intuition (LLM). Cost per show is pennies (~50 calls).
3. **Quality checking**: Built-in adversarial auditor that flags text-only assumptions and resolution leaks.
4. **Interview re-runnability**: 100% config-driven taxonomy. Swap the show script folder and the taxonomy YAML, and it executes out-of-the-box.
