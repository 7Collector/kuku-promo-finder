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

### 3. Run Unit Test Suite
```bash
python3 -m unittest discover tests
```

### 4. Launch Interactive Streamlit Dashboard
```bash
streamlit run app.py
```

---

## 🤖 Supported Frontier Models

The pipeline implements the **Provider Strategy Pattern** (`src/providers/`):
- **Google Gemini:** `gemini-3.8-flash` (Default for `--provider gemini`)
- **OpenAI:** `gpt-6-luna` (Default for `--provider openai`)
- **Anthropic Claude:** `claude-sonnet-5-5` (Default for `--provider anthropic`)
- **Offline Heuristic Engine:** Runs instantaneously when no API keys are configured.

To run with a live provider:
```bash
export GEMINI_API_KEY="your-gemini-key"
python run.py --provider gemini

# Or with OpenAI:
export OPENAI_API_KEY="your-openai-key"
python run.py --provider openai

# Or with Claude:
export ANTHROPIC_API_KEY="your-anthropic-key"
python run.py --provider anthropic
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
   • Scans 20–60s windows opening on hooks ≤ 3.5s
   • Tags against the "Blood Boils" & "Withheld Payoff" taxonomy
   • Builds Single-Episode clips + Cross-Episode Composites (Setup + Climax)
        │
        ▼
[Stage 3: Validation, Deduplication & MMR Diversity (src/ranker.py)]
   • Code enforces 20–60s duration and timestamp verification
   • MMR penalty prevents 10 identical slap scenes with monotonic rank tracking
        │
        ▼
[Stage 4: Adversarial Quality Auditor (src/auditor.py)]
   • Flags resolution leaks, context deficits, and visual dependencies
        │
        ▼
[Outputs: outputs/promos.json & outputs/PROMOS.md & Streamlit UI]
```

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
│   ├── composite.py           # Show-agnostic cross-episode composite builder
│   ├── ranker.py              # Canonical score calculation, deduplication & MMR diversity
│   ├── auditor.py             # Adversarial quality check & failure detector
│   ├── prompts.py             # Decoupled domain prompts
│   ├── taxonomy.py            # Word-boundary matcher & false positive filters
│   ├── utils/
│   │   ├── timestamps.py      # Timestamp conversion & overlap math
│   │   └── logging.py         # Structured application logger
│   └── providers/
│       ├── base.py            # BaseLLMProvider interface
│       ├── gemini.py          # Gemini 3.8 Flash adapter
│       ├── openai.py          # GPT-6 Luna adapter
│       ├── anthropic.py       # Claude Sonnet 5.5 adapter
│       ├── heuristic.py       # Offline fallback adapter
│       └── factory.py         # Provider factory
├── outputs/
│   ├── promos.json            # Unedited raw submission output
│   └── PROMOS.md              # Formatted report with quality audits
├── tests/
│   ├── test_parser.py         # Screenplay parser tests
│   ├── test_taxonomy.py       # Word boundary & collision tests
│   ├── test_ranker.py         # Timing constraint & MMR tests
│   └── test_auditor.py        # Resolution leak & risk audit tests
├── app.py                     # Interactive Streamlit dashboard
├── run.py                     # CLI pipeline runner
├── requirements.txt           # Dependencies
└── AGENTS.md                  # AI collaboration & failure analysis
```
