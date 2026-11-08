# Kuku Promo Finder

Finds 20-60s promo clips (hook in the first 3s, cliffhanger ending, understandable cold) in timestamped microdrama screenplays, ranks them, and audits each one. Built for the Kuku AI Generalist assignment, Problem 1.

- Engine: Python (`run.py`). Viewer: Next.js (`app/`), read-only.
- Write-up: `SOLUTION_DOC.md` (PDF: `SOLUTION_DOC.pdf`). AI collaboration log: `AGENTS.md`.

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # add OPENAI_API_KEY and GEMINI_API_KEY

# Headline committed run (Dual-Judge Audit Panel with Tiered Ranking):
python run.py --provider openai --model gpt-6-luna --audit-panel --export-csv

# Standard run with independent Gemini judge:
python run.py --provider openai --model gpt-6-luna

# Offline keyword smoke test (about 1s; labelled as such in every output):
python run.py --provider heuristic

# Run automated claims verification and unit test suite:
python eval/verify_claims.py
python -m unittest discover -s tests -t .
```

A provider you name explicitly must have its key; otherwise the run stops with an error. It never silently switches to the keyword engine. Responses are cached in `.cache/kuku/`, so re-running an unchanged prompt is free; use `--no-cache` to force fresh calls.

### Roles, Independent Judges & The Refuse-Same-Model Rule

- **Extractor Role:** OpenAI `gpt-6-luna` proposes candidate windows, verbatim quotes, and dramatic tags.
- **Judge Role:** Google Gemini (`gemini-3.5-flash-lite`, discovered dynamically via API) acts as an independent adversarial judge.
- **Refuse-Same-Model Rule:** The pipeline strictly refuses to run if the extractor model is configured as the sole auditor (e.g. OpenAI grading its own work) unless `--allow-self-audit` is explicitly passed.
- **Audit Panel (`--audit-panel`):** Runs a two-judge panel (`openai:gpt-6-luna` + `gemini-3.5-flash-lite`).
- **Tiered Ranking:**
  - **Tier 1:** Both judges pass (consensus quality).
  - **Tier 2:** Split verdict (marked "needs editor look" with both critiques).
  - **Tier 3:** Both judges fail.
  - Candidates with `audit_error` or marked `not_audited` are excluded from the top 15. The ranker sorts Tier 1 first, then Tier 2, applying repeat penalties.
- **`--audit-top-n N`:** Audits only the N highest-scoring candidates by composite score; remaining candidates are marked `not_audited` and excluded from top tiers.
- **`--allow-self-audit`:** Permits using the extractor model as the sole judge when only one API key is available.

### Outputs (`outputs/`)

| File | Contents |
|---|---|
| `promos.json` | Top 15, with segments, hook, cliffhanger, scores, audit result, `engine`, `model` |
| `PROMOS.md` | Readable report; states engine, model, audit method and counts in its header |
| `promos.pool.json` | All candidates after validation and de-duplication, with audits |
| `promos.rejected.json` | Model-reported near misses and proposals dropped by validation |
| `promos.meta.json` | Provider/model, counts, failures, token usage, wall time, git commit |
| `promos.csv` | Exported promo segments when `--export-csv` is run |
| `smoke_test_heuristic/` | Keyword-engine output, kept for comparison only |

Exit codes: 0 ok; 1 completed but incomplete (failed episodes or unaudited candidates, see meta); 2 bad input or configuration; 3 nothing to write. Existing outputs are never overwritten by an empty or failed run.

## Modular LLM Stages & CLI Options

Every new LLM stage is a CLI flag, **off by default**. Plain `python run.py` keeps roughly its current cost (~$0.12) and ~4 min wall time.

| Flag | Default | Description | Measured Cost / Time |
|---|---|---|---|
| `--cold-read` | `off` | Zero-context blind model evaluation of clip text. Returns perceived characters, plot, confusion, and a 0-10 `stakes_are_clear` score. Diagnostics only. | ~$0.03 / ~20s |
| `--use-cold-read-in-rank` | `off` | Replaces `standalone_clarity` with the blind `cold_read` score in the rank formula. | $0.00 / 0s |
| `--audit-panel <p:m,p:m>` | `off` | Two independent audit judges requiring consensus (both must pass). Degrades cleanly with a warning if only one provider key is configured. | ~$0.08 / ~30s |
| `--rerank` | `off` | Listwise LLM reranking of top audit-passing candidates run twice with varied seeds. Blends with weighted score. | ~$0.02 / ~15s |
| `--auto-profile` | `off` | Pre-pass analyzing all episodes to generate a draft show profile (`config/shows/<show>.generated.yaml`). | ~$0.04 / ~20s |
| `--consolidate-taxonomy` | `off` | Clusters model-invented `new:` tags into canonical types with rules, writing `config/taxonomy.suggested.yaml`. Never edits taxonomy.yaml directly. | ~$0.02 / ~10s |
| `--recheck-empty` | `off` | Relaxed extraction for empty episodes to distinguish model strictness from genuinely quiet scenes. Writes `outputs/promos.recheck.json`. | ~$0.03 / ~20s |
| `--export-csv [path]` | `off` | Exports promo segments to CSV (1 row per segment) with mm:ss.ss timecodes, quotes, and payoff locations. Default path: `outputs/promos.csv`. | $0.00 / 0s |
| `--scoring-weights <k=v>` | `hook=0.30,...` | Override editorial weights (defaults: hook=0.30, cliffhanger=0.25, payoff_withheld=0.20, injustice_tension=0.15, standalone_clarity=0.10, conversion_intent=0.0). | $0.00 / 0s |

### Editor Handoff (`--export-csv`)
Running `python run.py --export-csv` outputs `outputs/promos.csv` structured with one row per segment:
- Columns: `promo_id`, `rank`, `episode`, `segment_order`, `start_time`, `end_time`, `duration_seconds`, `hook_quote`, `cliffhanger_quote`, `payoff_location`, `audit_verdict`.
- Timestamps are formatted as `mm:ss.ss` ready for direct NLE timeline pasting.

## Composites (Status & Future Design)
Composites (cross-episode splices) are **off by default and out of scope**. The original experimental builder paired scenes across episodes without verifying character or emotional continuity, producing incoherent splices.

**Future Design Rules for Composites:**
1. **Hook first:** Opening cut must grab attention within 3s; never delay the hook.
2. **Short setup:** Follow immediately with an earlier setup scene featuring identical characters and conflict.
3. **LLM proposal, code validation:** Candidate pairings proposed from a cast/arc summary, strictly verified by code against beat boundaries and character presence.
4. **Strict gating:** The composite candidate is kept only if its blind `--cold-read` score strictly beats the single-episode cut.

## What is enforced in code
`src/validation.py` and `src/ranker.py`: total 20-60s; hook beat starts within 3s of the opening cut; every cut is on a real beat edge (LLM times within 0.5s are snapped, others dropped); hook and cliffhanger quotes exist verbatim in the screenplay; the cliffhanger ends the clip (last 6s); scores clamped to 0-10. Audit-passing promos rank above failing ones, with a count-based penalty for repeated hook types and episodes.

## Another show
```bash
cp config/shows/_template.yaml config/shows/my_show.yaml    # edit title, premise, characters
python run.py --show my_show --input-dir path/to/screenplays
```
Screenplays must use the same layout: `**SPEAKER (emotion):**` then `Start: (mm:ss.ss) | End: (mm:ss.ss)` then the text. Anything else parses to zero beats and the run stops with an error. A custom `--input-dir` without `--show`/`--context` is refused, and outputs go to `outputs/<show>/`. Hook types are config; add one in `config/taxonomy.yaml` with no code change.

Other options: `--audit-model` / `--audit-provider` (configure an explicit independent judge; by default discovers Gemini flash), `--allow-self-audit` (permits extractor to self-audit if only one key is available), `--composites` (experimental cross-episode splices, off by default), `--top-k`, `--workers`.

## Evaluation
No hand-picked ground truth exists yet, so recall is unmeasured. To measure it: write your picks to `eval/ground_truth.json` (format in `eval/recall.py`) before looking at the output, then `python eval/recall.py`.

## Web Viewer & Custom Screenplay API (Vercel Ready)
```bash
npm install && npm run dev      # http://localhost:3000
```
- **Interactive UI:** Click **"Upload Custom Script"** on the home page to upload your own screenplays as multiple `.txt` files, a `.zip` archive, or by pasting formatted screenplay text. Run extraction and auditing via Gemini, OpenAI, or the offline heuristic engine with live progress, download ranked CSV/JSON, or reset to the shipped baseline anytime.
- **Vercel Free Tier Deployment:**
  - Designed for serverless zero-dependency execution in Next.js (Node.js runtime).
  - Add your LLM keys in Vercel Project Settings $\rightarrow$ Environment Variables: `GEMINI_API_KEY` (recommended, fast & free-tier friendly) or `OPENAI_API_KEY`.
- **REST API (`/api/pipeline/analyze`):**
  - `POST /api/pipeline/analyze`: Accepts `multipart/form-data` (with `.txt` or `.zip` files) or JSON `{ provider: "gemini"|"openai"|"heuristic", screenplayText: "...", format: "json"|"csv" }`. Returns ranked promos with verbatim quotes, timestamps, audit tiers, and payoff locations.
  - `GET /api/pipeline/status`: Checks if server environment keys are configured.

## Layout
```
run.py            CLI pipeline          eval/recall.py     recall against your picks
src/parser.py     screenplay -> beats   src/validation.py  hard-rule checks
src/extractor.py  LLM / keyword windows src/auditor.py     adversarial audit
src/ranker.py     scoring, ranking      src/composite.py   experimental splices
src/providers/    gemini, openai, anthropic, heuristic, retry, cache
config/           taxonomy.yaml, shows/<show>.yaml
app/ lib/         Next.js viewer        tests/             unit tests
outputs/          committed results     AUDIT.md           the audit these changes answer
```
