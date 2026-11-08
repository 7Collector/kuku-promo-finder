# Kuku Promo Finder

[![Live Web App](https://img.shields.io/badge/Live%20Web%20App-kuku--promo--finder--theta.vercel.app-000000?style=for-the-badge&logo=vercel)](https://kuku-promo-finder-theta.vercel.app/)
[![Solution Doc](https://img.shields.io/badge/Solution%20Doc-2--Page%20PDF-0b3d91?style=for-the-badge&logo=adobeacrobatreader)](SOLUTION_DOC.pdf)
[![Unit Tests](https://img.shields.io/badge/Unit%20Tests-55%2F55%20Passing-success?style=for-the-badge&logo=python)](tests/)
[![Dual-Judge Panel](https://img.shields.io/badge/Dual--Judge%20Audit-OpenAI%20%2B%20Gemini-orange?style=for-the-badge&logo=google)](outputs/promos.meta.json)
[![Claims Verified](https://img.shields.io/badge/Claims%20Harness-100%25%20Verified-brightgreen?style=for-the-badge)](eval/verify_claims.py)

Automated viral promo discovery for vertical microdramas (Instagram Reels, TikTok, YouTube Shorts). Built for the **Kuku AI Generalist Assignment (Problem 1: Find the Promos)**.

The system parses timestamped screenplays, extracts 20–60s high-conversion clips (scroll-stopping hook $\le 3\text{s}$, unresolved cliffhanger, unearned interpersonal injustice), enforces hard temporal boundaries in deterministic code, subjects candidates to an adversarial dual-judge consensus audit (`gpt-6-luna` + `gemini-3.5-flash-lite`), and reranks with diversity penalties.

---

## Key Deliverables & Quick Links

| Deliverable | Location | Description |
|---|---|---|
| **Live Web App** | [kuku-promo-finder-theta.vercel.app](https://kuku-promo-finder-theta.vercel.app/) | Interactive Next.js viewer with custom screenplay upload & analysis |
| **Solution Document** | [`SOLUTION_DOC.pdf`](SOLUTION_DOC.pdf) · [`SOLUTION_DOC.md`](SOLUTION_DOC.md) | Formatted 2-page executive write-up answering all brief questions |
| **Ranked Promos** | [`outputs/PROMOS.md`](outputs/PROMOS.md) · [`promos.json`](outputs/promos.json) | Top 15 consensus promos with verbatim quotes and payoff locations |
| **Editor Handoff CSV** | [`outputs/promos.csv`](outputs/promos.csv) | Segment-by-segment NLE timecodes (`mm:ss.ss`) and quotes |
| **Ablation Studies** | [`outputs/ablations/SUMMARY.md`](outputs/ablations/SUMMARY.md) | Measured comparison of weights, judge models, and rerankers |
| **AI Collaboration Log** | [`AGENTS.md`](AGENTS.md) | Tools used, authorship attribution, and real AI failure log |
| **Verification Harness** | [`eval/verify_claims.py`](eval/verify_claims.py) | Automated script proving every claim in documentation matches outputs |

---

## 1. Web Viewer & Custom Screenplay API (Vercel Ready)

The web platform is deployed live on **Vercel Free Tier**:  
👉 **[https://kuku-promo-finder-theta.vercel.app/](https://kuku-promo-finder-theta.vercel.app/)**

### Interactive Screenplay Ingestion
- **Upload Custom Script:** Click **"Upload Custom Script"** on the home page to upload your own microdrama screenplays.
  - Supports multiple `.txt` files or a `.zip` archive.
  - Or paste screenplay text directly with one-click sample loading.
- **Model Selection & Key Autodetection:**
  - **Google Gemini** (default runner; note that free-tier keys may encounter rate limits on burst requests, so the client runs with concurrency=1 and patient exponential backoff).
  - **OpenAI** (`gpt-4o-mini`, `gpt-6-luna` with concurrency=4).
  - **Offline Heuristic Smoke Test:** 0 API calls, 0 cost, instant preview.
  - Automatically detects `GEMINI_API_KEY` or `OPENAI_API_KEY` configured in Vercel environment variables, with optional user override.
- **Export & Workflow:** Filter by hook archetype, inspect dual-judge critiques, download NLE-ready `custom_promos.csv` or `custom_promos.json`, and reset to baseline anytime.

### Verified Vercel Free-Tier Limits
All serverless function configurations conform to verified Vercel Hobby specifications (Source: [Vercel Function Limitations](https://vercel.com/docs/functions/limitations)):
- **Request Body Size Limit:** **4.5 MB** (`4,718,592` bytes). Uploads exceeding this limit are pre-checked and rejected with guidance to split `.zip` files.
- **Function Execution Duration:** Up to **300 seconds** maximum on Hobby (configured to `maxDuration = 60` for individual modular routes to stay well under limits).

### Vercel Environment Variables
Configure the following environment variables in your Vercel Project Settings:
- `GEMINI_API_KEY`: API key for Google Gemini model calls (default runtime provider for custom screenplay uploads).
- `OPENAI_API_KEY`: API key for OpenAI model calls (`gpt-6-luna` extraction and judge audits).

### Zero-Dependency Serverless REST API
- **`POST /api/pipeline/analyze`**
  - Accepts `multipart/form-data` with `.txt`/`.zip` files or JSON:
    ```bash
    curl -X POST https://kuku-promo-finder-theta.vercel.app/api/pipeline/analyze \
      -H "Content-Type: application/json" \
      -d '{
        "provider": "gemini",
        "showTitle": "My Custom Show",
        "screenplayText": "EPISODE NUMBER: 1\n\n**JULIANA (crying):**\nStart: (00:00.00) | End: (00:03.50)\nI cannot marry you, Julian!...\n--- SCRIPT END ---"
      }'
    ```
  - Pass `"format": "csv"` for direct CSV spreadsheet download.
- **`GET /api/pipeline/status`**: Checks available Vercel server environment keys.

---

## 2. Core Architecture: Code Enforces Constraints, AI Judges Drama

```
Screenplay Text (.txt / .zip)
       │
       ▼
[1] Deterministic Parser (`src/parser.py` / `lib/pipeline.ts`)
    └─ Mathematically exact timestamps (`mm:ss.ss` ➔ seconds), spoken vs camera beats
       │
       ▼
[2] Window Discovery & Tagging (`src/extractor.py`)
    └─ LLM (`gpt-6-luna` or Gemini) identifies scroll-stopping hooks & curiosity gaps
       │
       ▼
[3] Hard Validation & Cliffhanger Trimming (`src/validation.py`)
    ├─ Enforces 20.0s – 60.0s duration
    ├─ Hook beat starts within ≤ 3.0s of opening cut
    ├─ Cut snapping: cuts within ≤ 0.5s snap to spoken beat edges; off-beat cuts drop
    ├─ Verbatim quote verification against actual dialogue
    ├─ Cliffhanger tail window: cliffhanger beat must be in final 6.0s
    ├─ Cliffhanger Trim-and-Revalidate: trims trailing fluff to recover valid promos
    └─ Code-verified payoff location: ensures resolution timestamp exists in screenplay
       │
       ▼
[4] Adversarial Dual-Judge Audit Panel (`src/auditor.py` + `src/stages.py`)
    ├─ Judge 1: OpenAI `gpt-6-luna`
    ├─ Judge 2: Google Gemini (`gemini-3.5-flash-lite`, discovered dynamically via API)
    └─ Refuse-Same-Model Rule: strictly refuses extractor grading its own work
       │
       ▼
[5] Consensus Tiered Diversity Ranking (`src/ranker.py`)
    ├─ Tier 1: Consensus Pass (both judges pass)
    ├─ Tier 2: Split Verdict ("needs editor look")
    ├─ Tier 3: Both Fail (excluded from top tiers)
    └─ Diversity penalties: repeat hook ×0.82, repeat episode ×0.85
```

### Canonical Engine (Python) vs Web Engine (TypeScript)
- **Canonical Pipeline (`src/` in Python):** Canonical for all committed outputs, evaluation ablations, and test suites. Implements the complete multi-stage research pipeline: dual-judge consensus panel (`--audit-panel`), blind cold-read evaluation (Stage A), listwise reranking (Stage C), automated show profiling (Stage D), taxonomy consolidation (Stage E), and empty-episode rechecking (Stage F).
- **Interactive Web Engine (`lib/pipeline.ts` in TypeScript):** Serves the browser upload tool and REST APIs on Vercel without Python runtime overhead.
  - *Supported in TypeScript:* Single judge & dual audit tiers, 20-60s physical constraint checking, hook ≤3s window enforcement, spoken beat edge cut snapping (≤0.5s tolerance), verbatim quote verification, cliffhanger tail trimming recovery, payoff location verification (*timestamp validated as a real beat; meaning not checked*), and count-based repeat penalties.
  - *Not supported in TypeScript:* Stage A blind cold read, Stage C listwise rerank, Stage D auto-profile, and Stage E taxonomy clustering (which remain offline research tools in Python).

---

## 3. Measured Results on 50 Episodes

Every figure below is derived directly from committed files and verified by [`eval/verify_claims.py`](eval/verify_claims.py):

- **Candidate Pool:** 62 proposed $\rightarrow$ 62 valid $\rightarrow$ 60 deduped across the season.
- **Dual-Judge Panel Agreement:**
  - Extractor: OpenAI `gpt-6-luna`.
  - Judge 1 (`gpt-6-luna`) Pass Rate: **55.0%** (33/60).
  - Judge 2 (`gemini-3.5-flash-lite`) Pass Rate: **63.3%** (38/60).
  - Agreement Rate: **68.3%** (41/60), Cohen's kappa **$\kappa = 0.3493$** (fair consensus).
- **Consensus Tiers:** **Tier 1 = 26, Tier 2 = 19, Tier 3 = 15** (0 audit errors). All 15 headline promos are Tier 1 consensus picks.
- **Cliffhanger Trimming Recovery:** In Ep 15, `ep15_cand_1` was recovered by trimming 7.5s (41.2s $\rightarrow$ 33.7s), meeting the 6s cliffhanger window without dropping the candidate.
- **Payoff Locations:** 5 of top 15 promos have a code-verified payoff_location in the screenplay (timestamp validated as a real beat; meaning not checked); the other 10 are marked `unknown` because the conflict resolves in later episodes or proposed timestamps did not snap to real spoken edges.
- **Empty Episodes:** The empty-episode drop (13 to 6) came mainly from the conversion prompt, with cliffhanger trimming recovering one candidate (Ep 15). 6 empty episodes remain in the main pool (`[6, 8, 10, 11, 17, 25]`). Quiet scenes (6, 8, 10, 17) have 0 model proposals; Ep 11 and 25 had hard constraint violations.
- **Cost Profile:** Total spend across all runs in `outputs/cost_ledger.json` is **$0.0134** (headline run: $0.0002 live, $0.0190 cached; ablations and extra stages: $0.0132 live). Pure mathematical reranking is **$0.0000** and runs in **<0.1s**.

---

## 4. Run It Locally

### Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # Add OPENAI_API_KEY and GEMINI_API_KEY
```

### Execution Commands
```bash
# Headline committed run (Dual-Judge Audit Panel with Tiered Ranking & CSV export):
python run.py --provider openai --model gpt-6-luna --audit-panel --export-csv

# Standard run with independent Gemini judge:
python run.py --provider openai --model gpt-6-luna

# Offline keyword smoke test (about 1s; labelled as such in every output):
python run.py --provider heuristic

# Run automated claims verification harness and 55 unit tests:
python eval/verify_claims.py
python -m unittest discover -s tests -t .

# Run Next.js web application locally:
npm install && npm run dev    # http://localhost:3000
```

---

## 5. Modular LLM Stages & CLI Options

Every stage is a modular CLI flag, **off by default**. Plain `python run.py` preserves baseline behavior.

| Flag | Default | Description | Measured Cost / Time |
|---|---|---|---|
| `--audit-panel [p:m,p:m]` | `off` | Two independent audit judges requiring consensus (defaults to `openai:gpt-6-luna` + Gemini flash). | ~$0.08 / ~30s |
| `--cold-read` | `off` | Zero-context blind model evaluation of clip text returning perceived plot, stakes, and confusion. | ~$0.03 / ~20s |
| `--use-cold-read-in-rank`| `off` | Replaces `standalone_clarity` with blind `cold_read` score in ranking. | $0.00 / 0s |
| `--rerank` | `off` | Listwise LLM reranking of top candidates run twice with varied seeds. | ~$0.02 / ~15s |
| `--auto-profile` | `off` | Pre-pass analyzing all episodes to generate a draft show profile. | ~$0.04 / ~20s |
| `--consolidate-taxonomy` | `off` | Clusters model-invented `new:` tags into canonical suggestions. | ~$0.02 / ~10s |
| `--recheck-empty` | `off` | Relaxed extraction for empty episodes to distinguish quiet dialogue. | ~$0.03 / ~20s |
| `--export-csv [path]` | `off` | Exports promo segments to CSV (1 row per segment) with `mm:ss.ss` timecodes. | $0.00 / 0s |
| `--scoring-weights <k=v>`| `hook=0.30,...` | Override editorial weights as JSON or comma-separated `key=value` pairs. | $0.00 / 0s |

---

## 6. Outputs Directory Structure (`outputs/`)

| File | Contents |
|---|---|
| `promos.json` | Top 15 ranked promos with segments, verbatim quotes, scores, audit tiers, and judge critiques |
| `PROMOS.md` | Human-readable markdown catalog with audit tier badges, timecodes, and payoff locations |
| `promos.csv` | NLE timeline-ready segment export (`mm:ss.ss` timestamps) |
| `promos.pool.json` | Full candidate pool (60 valid candidates) with dual-judge verdicts |
| `promos.rejected.json` | Candidate proposals dropped by validation (with exact failure reasons) |
| `promos.meta.json` | Full provenance: models, token counts, costs, agreement rates, and git commit |
| `ablations/SUMMARY.md` | Full ablation comparison across weights, models, cold reads, and reranking |

---

## 7. What is Enforced in Code vs What AI Decides

| Responsibility | Enforced By | Mechanism |
|---|---|---|
| **Timestamps & Bounds** | Deterministic Code (`src/validation.py`) | Snapped to real spoken beat edges ($\le 0.5\text{s}$ tolerance); $20\text{s} \le \text{duration} \le 60\text{s}$. |
| **Hook Window** | Deterministic Code (`src/validation.py`) | Opening cut must reach hook beat in $\le 3.0\text{s}$. |
| **Quote Integrity** | Deterministic Code (`src/validation.py`) | Hook and cliffhanger quotes must match screenplay beats verbatim. |
| **Cliffhanger Timing** | Deterministic Code (`src/validation.py`) | Cliffhanger beat must be in the final $6.0\text{s}$ (with end-trimming recovery). |
| **Payoff Verification** | Deterministic Code (`src/validation.py`) | Proposed payoff timestamp must match spoken beat in screenplay or is marked `unknown`. |
| **Dramatic Tension** | Frontier LLM (`gpt-6-luna`) | Identifies curiosity gaps, unearned injustice, and scroll-stopping power. |
| **Quality & Flaw Audit** | Dual-Judge Panel (`gpt-6-luna` + Gemini) | Catches resolution leaks, context deficits, visual dependencies, and tag errors. |
| **Feed Diversity** | Deterministic Code (`src/ranker.py`) | Mathematical penalty for repeated hook archetypes ($\times 0.82$) and episodes ($\times 0.85$). |

---

## 8. Repository Layout

```
run.py            CLI pipeline orchestrator        eval/verify_claims.py  Automated claims verification harness
src/parser.py     Screenplay parser (to beats)    eval/recall.py         Recall against ground-truth picks
src/validation.py Deterministic hard-rule checks   lib/pipeline.ts        Zero-dependency TypeScript pipeline engine
src/extractor.py  LLM candidate extraction        app/                   Next.js web application (React 19)
src/auditor.py    Adversarial audit judge         components/            Custom upload modal & UI components
src/ranker.py     Diversity ranker                config/                taxonomy.yaml, shows/<show>.yaml
src/stages.py     Modular LLM stages A-F          tests/                 55 unit tests (100% pass)
outputs/          Headline committed outputs      SOLUTION_DOC.pdf       2-page executive submission document
```
