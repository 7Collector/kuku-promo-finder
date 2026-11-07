# 🎬 Kuku Promo Finder — AI Microdrama Acquisition Engine

> Automated scroll-stopping promo discovery for vertical microdramas (Instagram Reels, TikTok, YouTube Shorts).  
> Built for the **Kuku AI Generalist Assignment (Problem 1: Find the Promos)**.  
> Styled with the **Omega Design System** and engineered for instant **Vercel** deployment.

---

## 🚀 Vercel & Web Quickstart

This application is built with **Next.js (App Router)** and TypeScript, engineered to deploy directly to Vercel with zero configuration.

### 1. Run Web Application Locally
```bash
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view:
- **`/` (Ranked Promos):** Featured Hero Board card, archetype filter chips, search, and detail modal.
- **`/analyze` (Reusable Cut Tool):** Interactive tester to evaluate any custom screenplay cut against the taxonomy, duration bounds, and adversarial auditor.
- **`/episodes` (Screenplay Inspector):** 50-episode browser with millisecond beat breakdowns.

### 2. Deploy to Vercel
Simply push to GitHub and import into Vercel:
```bash
# Or via Vercel CLI:
vercel
```
Vercel automatically detects Next.js, builds the static pages and serverless API routes (`/api/promos`, `/api/analyze`, `/api/episodes`, `/api/taxonomy`).

---

## 🐍 Python Core Pipeline Quickstart

```bash
# 1. Setup Python Environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Run Pipeline (<2s with heuristic engine, or ~20s parallelized with frontier LLMs)
PYTHONPATH=. python3 run.py

# 3. (Optional) Run Streamlit Review Dashboard
streamlit run app.py

# 4. Run Standard Unit Test Suite (10 tests)
PYTHONPATH=. python3 -m unittest discover tests
```

---

## 🏛️ Omega Design System Implementation

The web interface is built using the **Omega Design System** (`Design/omega-design-system`):
- **Quiet Paper & Ink:** Surfaces sit on `--paper` (`#F2F3F0`) with white surface cards (`#FFFFFF`) and hairlines (`#DADCD7`). No harsh drop shadows.
- **The One Dark Board:** The #1 ranked promo is presented on the focal dark surface (`--board: #1C2422`) with glowing accent mark.
- **Ballpoint Accent:** `--accent: #2B4FD8` for interactive controls, tabs, and focus states.
- **Tabular Figures:** Numbers (times, scores, counts, percentages) use `.om-num` (`font-feature-settings: "tnum"`).
- **The AI Gradient:** `--ai-gradient` is used strictly as a mark/sparkle for AI-derived dramatic scores and audits.
- **Sentence Case:** Consistent sentence case everywhere (no all-caps).

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
python3 run.py --provider gemini

# Or with OpenAI:
export OPENAI_API_KEY="your-openai-key"
python3 run.py --provider openai

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
   • Extracts 3,727 beats across 50 episodes with millisecond timestamps
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
[Deliverables: Next.js Web App / Vercel + outputs/promos.json + outputs/PROMOS.md]
```

---

## 📁 Repository Structure

```
├── app/                      # Next.js App Router (Vercel-ready)
│   ├── globals.css           # Omega Design System token imports & layout
│   ├── layout.tsx            # Root scaffold with Omega navigation header
│   ├── page.tsx              # Main dashboard (Hero Board, Filter Bar, Cards/Table view)
│   ├── analyze/page.tsx      # Reusable interactive promo cut tool
│   ├── episodes/page.tsx     # 50-episode screenplay browser
│   └── api/                  # Serverless API routes
│       ├── promos/route.ts   # Filterable promos endpoint
│       ├── analyze/route.ts  # Dynamic cut evaluation endpoint
│       ├── episodes/route.ts # Screenplay beat fetcher
│       └── taxonomy/route.ts # Taxonomy definitions endpoint
├── Design/
│   └── omega-design-system/  # Complete Omega tokens, CSS, components & guidelines
├── public/
│   └── fonts/                # Vendored Inter font families
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
├── run.py                     # CLI pipeline entrypoint (parallelized)
├── app.py                     # Streamlit review dashboard
├── requirements.txt           # Python dependencies
├── package.json               # Next.js & React dependencies
├── tsconfig.json              # TypeScript configuration
├── next.config.mjs            # Next.js configuration
├── SOLUTION_DOC.md            # Official 2-page submission solution document
└── AGENTS.md                  # AI collaboration & failure analysis
```
