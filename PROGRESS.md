# Progress / Run Tracker

## Run identity

- **Title:** `Fix everything in AUDIT.md`
- **Started:** 2026-11-07
- **Last updated:** 2026-11-07 (mid-run)
- **Source of truth:** `AUDIT.md` (finding IDs below refer to it)
- **Rules:** keep Next.js as the only UI (no Streamlit); do not invent evidence; numbers in docs must come from a named, committed run.

## Status

**State:** `COMPLETE (pending user actions below)`

**Current step:** all code and doc work done and verified; remaining items need the user.

## Done so far

- [x] `src/constants.py`: 20-60s, 3.0s hook window, snap tolerance in one place (B-limits, m4)
- [x] `src/utils/timestamps.py`: strict `try_parse_timestamp` rejects `09:99.00` (M4)
- [x] `src/models.py`: `Segment.episode`, score clamp 0-10, `QualityAudit.method`, per-promo `engine`/`model`/`risks`, float noise rounded (M4, B1, m)
- [x] `src/parser.py`: strips `--- SCRIPT END ---`, filename-based episode number with warning, drops end<start beats, warns on malformed beats, skips empty/duplicate episodes, raises on missing dir (M1, m1)
- [x] `src/validation.py`: beat-edge, quote, duration and hook-window checks, independent of provider (M4)
- [x] Providers: key only in headers and scrubbed from errors (M14), Anthropic `temperature` removed and text blocks selected (M2), usage accounting, retry/backoff, disk cache (M11), registry; unknown or keyless provider now errors instead of silently using heuristics (M3)
- [x] `src/llm_client.py` removed (m2)
- [x] `src/extractor.py`: validates and snaps LLM output, no silent heuristic fallback, failures and drop reasons recorded, quotes no longer truncated, cast sent in prompt (M3, M4, M7)
- [x] Prompts: cast line, audit gets show context, tag definitions, camera beats planned, flaw enum (M6)

## Remaining

- [x] `src/auditor.py`: strict bool, flaw enum, no silent rule fallback, separate audit model, dead code (M4, M5, M6, m2)
- [x] `src/composite.py`: opt-in, honest scores, episode-number cutoffs (M9)
- [x] `src/ranker.py`: strict limits, passes ranked before fails, episode-aware dedup, aligned defaults, drop "MMR" naming (M5, m4, m5)
- [x] `run.py`: provenance + meta + pool files, previous-episode logline, no empty overwrite, non-zero exit codes, `--show`/`--context` guard, per-show output dir, `--audit-model`, `--no-cache`, step labels (B1, M1, M3, M6, M7, m7)
- [x] Config: single show file in `config/shows/`, add template (m3)
- [x] Tests for validation, parser, factory, extractor, auditor, ranker
- [x] Remove `app.py`, Streamlit/pandas/rich deps and references (M12)
- [x] Next.js: remove fake `/analyze`, fix `\Z` regex, 404 on bad episode, derive counts from data, correct taxonomy route path (B4, M15)
- [x] Removed `CLAIMS_VERIFICATION.md`, `progress/`, unused `Design/` files, duplicate zip (M13, m9)
- [x] Live run on the real show; commit raw output, pool, rejects, meta (B1, B2)
- [x] Rewrite `SOLUTION_DOC.md` to 2 pages from the measured run; export PDF (B3, B5, M10)
- [x] Rewrite `README.md` and `AGENTS.md` with artifact-backed claims (B3)
- [x] Final verification: tests, `next build`, robustness cases from AUDIT.md section 3 M1

## Verification

- 34 unit tests pass. `next build` passes; `/api/episodes?ep=1` returns 95 beats (was 94), `?ep=999` returns 404, `/analyze` returns 404.
- Bad input (missing dir, SRT timestamps, unknown/keyless provider, custom dir without a show) exits 2 and writes nothing.
- Live run `gpt-6-luna`: 92 calls, 250.7s, 546,585 tokens (about $0.12); 44 valid candidates, 42 after dedup, 23 passed / 19 failed audit; top 15 pass all hard-rule checks in an independent re-verification (durations, beat edges, hook window, verbatim quotes, cliffhanger at the end).
- `SOLUTION_DOC.pdf` renders to 2 pages.

## Notes

- 33 unit tests pass; `next build` passes (one Turbopack tracing warning from runtime-configurable asset paths).
- Added `eval/recall.py`: computes recall/precision against `eval/ground_truth.json` once the user commits hand-picked promos.
- Extractor and auditor share one model in the committed run (self-graded); `--audit-model` supports an independent judge.

## Needs the user (cannot be done by me)

- Hand-pick 8-10 promos **before** looking at new results and commit them, so recall can be computed (B3). Until then no recall is claimed.
- Push the repo and, optionally, deploy to Vercel (B5). There is no git remote configured.
- Say which parts of the design (e.g. the "Blood Boils" framing, two-layer taxonomy) were yours, so `AGENTS.md` attribution is correct.
