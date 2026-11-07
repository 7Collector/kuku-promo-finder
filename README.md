# 🎬 Kuku Promo Finder — AI Microdrama Acquisition Engine

> Automated scroll-stopping promo discovery for vertical microdramas (Instagram Reels, TikTok, YouTube Shorts).  
> Built for the **Kuku AI Generalist Assignment (Problem 1: Find the Promos)**.

---

## ⚡ Quickstart

### 1. Setup Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Pipeline (50 Episodes in <2 seconds)
```bash
python run.py
```
Outputs are automatically generated in:
- `outputs/promos.json` — Unedited raw structured data
- `outputs/PROMOS.md` — Human-readable ranked report with quotes and quality audits

### 3. Launch Interactive Streamlit Dashboard
```bash
streamlit run app.py
```

---

## 🎯 Strategic Framing & Approach 3 Architecture

Microdramas thrive on high emotional asymmetry—specifically, **unearned injustice without immediate payoff ("blood boils")** paired with **withheld catharsis** (cutting right before comeuppance).

```
[Screenplays (.txt)]
        │
        ▼
[Stage 1: Deterministic Screenplay Parser (src/parser.py)]
   • Extracts 3,727 beats across 50 episodes with sub-second timestamps
        │
        ▼
[Stage 2: Candidate Discovery & Taxonomy Tagging (src/extractor.py)]
   • Scans 20–60s windows opening on hooks ≤ 3s
   • Tags against the "Blood Boils" & "Withheld Payoff" taxonomy
   • Builds Single-Episode clips + Cross-Episode Composites (Setup + Climax)
        │
        ▼
[Stage 3: Validation, Deduplication & MMR Diversity (src/ranker.py)]
   • Code enforces 20–60s duration and timestamp verification
   • MMR penalty prevents 10 identical slap scenes
        │
        ▼
[Stage 4: Adversarial Quality Auditor (src/auditor.py)]
   • Flags resolution leaks, context deficits, and visual dependencies
        │
        ▼
[Outputs: outputs/promos.json & outputs/PROMOS.md & Streamlit UI]
```

---

## 🧠 Pluggable Hook & Cliffhanger Taxonomy

All dramatic scoring is driven by [`config/taxonomy.yaml`](config/taxonomy.yaml) rather than hardcoded rules:

### Hook Taxonomy (The "Blood Boils" Family)
- `public_humiliation` (1.0): Protagonist mocked or belittled in front of peers.
- `physical_aggression` (0.95): Slap, push, drink thrown, physical violation.
- `intimate_betrayal` (0.95): Betrayal by fiancé, spouse, or parent at a pivotal moment.
- `class_status_contempt` (0.90): Sneering disdain treating the protagonist as dirt/servant.
- `hidden_identity_irony` (0.90): Antagonist insults protagonist, blind to their true royal identity.
- `unjust_accusation` (0.85): Innocent protagonist framed while villain smirks.

### Cliffhanger Taxonomy (Withheld Payoffs)
- `interrupted_retaliation` (1.0): Protagonist's eyes turn cold / about to counterattack; cut right before blow.
- `unexpected_savior_arrival` (0.95): Benefactor / commander arrives just as protagonist is cornered.
- `truth_half_revealed` (0.90): Identity document or crest revealed; cut before reaction.
- `mortal_ultimatum` (0.85): Impossible choice with ticking clock.

---

## 🔄 Swapping Models or Testing New Shows

To test a new show in your interview:
1. Place the screenplay `.txt` files in a folder (e.g. `assets/new_show/`).
2. Update [`config/show_context.yaml`](config/show_context.yaml) with the new premise and characters.
3. Run:
```bash
python run.py --input-dir "assets/new_show"
```

To enable a live LLM API (Gemini / OpenAI / Anthropic):
```bash
export GEMINI_API_KEY="your-api-key"
python run.py --provider gemini
```
*(If no API key is provided, the tool automatically executes via the built-in deterministic heuristic engine with zero failures!)*

---

## 📁 Repository Structure

```
├── config/
│   ├── taxonomy.yaml         # Hook & cliffhanger taxonomy
│   └── show_context.yaml      # Show profile & characters
├── src/
│   ├── parser.py              # Screenplay parser (100% deterministic)
│   ├── models.py              # Pydantic data schemas
│   ├── extractor.py           # Window discovery & taxonomy tagging
│   ├── composite.py           # Cross-episode setup/climax stitcher
│   ├── ranker.py              # Score calculation, deduplication & MMR diversity
│   ├── auditor.py             # Adversarial quality check & failure detector
│   └── llm_client.py          # Swappable LLM interface
├── outputs/
│   ├── promos.json            # Unedited raw submission output
│   └── PROMOS.md              # Formatted report with quality audits
├── app.py                     # Interactive Streamlit dashboard
├── run.py                     # CLI pipeline runner
├── requirements.txt           # Dependencies
└── AGENTS.md                  # AI collaboration & failure analysis
```
