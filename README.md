# 🎬 Kuku Promo Finder — AI Microdrama Acquisition Engine

> Automated scroll-stopping promo discovery for vertical microdramas (Instagram Reels, TikTok, YouTube Shorts).  
> Built for the **Kuku AI Generalist Assignment (Problem 1: Find the Promos)**.  
> Combines deterministic Python parsing, an extensible two-layer taxonomy, cross-episode composite stitching, and adversarial quality auditing.

---

## 🐍 1. Python Core Pipeline Quickstart (Headline Path)

The headline deliverable is a production-grade, reproducible Python engine with zero mandatory external API costs.

```bash
# 1. Setup Python Virtual Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Run Pipeline (<2s with offline heuristic engine, or ~20s parallelized with frontier LLMs)
PYTHONPATH=. python3 run.py

# 3. (Optional) Run Streamlit Review Dashboard
streamlit run app.py

# 4. Run Automated Test Suite (14 unit tests)
PYTHONPATH=. python3 -m unittest discover tests
```

Outputs are automatically generated to:
- **`outputs/promos.json`:** Raw, unedited JSON output meeting all assignment schema requirements.
- **`outputs/PROMOS.md`:** Ranked editorial report complete with timestamps, hook/cliffhanger quotes, and quality audit cards.

---

## 🚀 2. Next.js Web Application & Vercel Deployment

An interactive visual explorer styled with the **Omega Design System** (`Design/omega-design-system`), engineered for instant **Vercel** deployment:

```bash
# Run web application locally
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view:
- **`/` (Ranked Promos):** Hero Board showcasing the #1 ranked promo on the focal dark surface, archetype filter chips, search, and detail modal.
- **`/analyze` (Reusable Cut Tool):** Interactive editor tool allowing reviewers to test any custom screenplay cut against the taxonomy, duration bounds (20–60s), and adversarial auditor with one-click presets.
- **`/episodes` (Screenplay Inspector):** 50-episode browser with centisecond beat breakdowns and emotion tags.

To deploy on Vercel:
```bash
vercel
```

---

## 🤖 Supported Frontier Models

The pipeline implements the **Provider Strategy Pattern** (`src/providers/`):
- **Google Gemini:** `gemini-3.8-flash` (Default for `--provider gemini`)
- **OpenAI:** `gpt-6-luna` (Default for `--provider openai`)
- **Anthropic Claude:** `claude-sonnet-5-5` (Default for `--provider anthropic`)
- **Offline Heuristic Engine:** Runs instantaneously at $0.00 cost when no API keys are configured.

To run with a live provider:
```bash
export OPENAI_API_KEY="your-openai-key"
python3 run.py --provider openai

# Or with Gemini:
export GEMINI_API_KEY="your-gemini-key"
python3 run.py --provider gemini

# Or with Claude:
export ANTHROPIC_API_KEY="your-anthropic-key"
python3 run.py --provider anthropic
```

---

## 🎯 Architecture & Pipeline Stages

```
[Screenplays (.txt)]
        │
        ▼
[Stage 1: Deterministic Screenplay Parser (src/parser.py)]
   • Extracts 3,727 beats across 50 episodes with centisecond timestamps (ss.ss)
        │
        ▼
[Stage 2: Candidate Discovery & Composite Pairing (src/extractor.py, src/composite.py)]
   • Scans 20–60s windows opening on hooks ≤ 3.5s
   • Tags against the Two-Layer Taxonomy (core generic rules + show cue overlay)
   • Synthesizes Single-Episode cuts + Cross-Episode Composites (Setup + Climax)
        │
        ▼
[Stage 3: Physical Validation & Deduplication (src/ranker.py)]
   • Enforces 20–60s duration and verified screenplay timestamp cut points
   • Deduplicates overlapping candidates (>35% temporal overlap pruned)
        │
        ▼
[Stage 4: Adversarial Quality Auditor (src/auditor.py)]
   • Injects exact <clip_screenplay> dialogue slices between hook and cliffhanger
   • Tests 5 failure modes: resolution leaks, context deficits, visual dependencies, slow burns, sarcasm
        │
        ▼
[Stage 5: Audit-Informed MMR Diversity Reranking (src/ranker.py)]
   • Penalizes failed audits (0.78x multiplier; 0.65x for resolution leaks)
   • MMR penalty ensures balanced marketing variety across hook archetypes
        │
        ▼
[Deliverables: outputs/promos.json + outputs/PROMOS.md + Streamlit & Next.js UIs]
```

---

## 📁 Repository Structure

```
├── run.py                     # CLI pipeline entrypoint (parallelized)
├── app.py                     # Streamlit review dashboard
├── config/
│   ├── taxonomy.yaml          # Core generic hook & cliffhanger taxonomy (with requires/do_not_tag_if)
│   ├── show_context.yaml      # Show profile, characters & show cue overlay
│   └── shows/                 # Modular show overlays (e.g. broken_soldier.yaml)
├── src/
│   ├── parser.py              # Screenplay parser (100% deterministic, centisecond math)
│   ├── models.py              # Pydantic data schemas (PromoScores, PromoCandidate, QualityAudit)
│   ├── extractor.py           # Window discovery & taxonomy tagging
│   ├── composite.py           # Dynamic cross-episode composite promo builder
│   ├── ranker.py              # Canonical scoring, deduplication & audit-informed MMR
│   ├── auditor.py             # Adversarial quality check with screenplay beat injection
│   ├── prompts.py             # Decoupled domain prompt templates
│   ├── taxonomy.py            # Two-layer taxonomy loader & word-boundary regex matcher
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
├── app/                       # Next.js App Router (Omega Design System, Vercel-ready)
│   ├── globals.css            # Omega Design System token imports & layout
│   ├── layout.tsx             # Root scaffold with Omega navigation header
│   ├── page.tsx               # Main dashboard (Hero Board, Filter Bar, Detail Modal)
│   ├── analyze/page.tsx       # Reusable interactive promo cut tool
│   ├── episodes/page.tsx      # 50-episode screenplay browser
│   └── api/                   # Serverless API routes (/api/promos, /api/analyze, etc.)
├── Design/
│   └── omega-design-system/   # Complete Omega tokens, CSS, components & guidelines
├── outputs/
│   ├── promos.json            # Unedited raw submission output
│   └── PROMOS.md              # Formatted report with quality audits
├── tests/
│   ├── test_parser.py         # Screenplay parser tests
│   ├── test_taxonomy.py       # Word boundary & collision tests
│   ├── test_ranker.py         # Timing constraint, audit penalty & MMR tests
│   ├── test_auditor.py        # Resolution leak, visual risk & slice injection tests
│   └── test_composite.py      # Cross-episode composite builder tests
├── requirements.txt           # Python dependencies
├── package.json               # Next.js & React dependencies
├── tsconfig.json              # TypeScript configuration
├── next.config.mjs            # Next.js configuration
├── SOLUTION_DOC.md            # Official 2-page submission solution document
├── AGENTS.md                  # AI collaboration & failure analysis
├── CLAIMS_VERIFICATION.md     # Codebase audit & claims verification matrix
└── PROGRESS.md                # Task tracker and verification record
```
