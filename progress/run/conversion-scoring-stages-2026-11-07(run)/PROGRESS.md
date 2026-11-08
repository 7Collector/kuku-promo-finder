# Progress / Run Tracker

## Run identity

- **Title:** `Reframe scoring around conversion, add measured LLM stages, fix docs`
- **Run folder:** `progress/run/conversion-scoring-stages-2026-11-07(run)/`
- **Started:** `2026-11-07 19:23 IST`
- **Last updated:** `2026-11-07 19:54 IST`
- **Owner/agent:** `Antigravity`
- **Requested outcome:** `Reframe promo discovery and audit around conversion intent; update prompts, models, and ranker with new weights; add 6 modular LLM stage flags (--cold-read, --audit-panel, --rerank, --auto-profile, --consolidate-taxonomy, --recheck-empty); add --export-csv; run ablations and commit outputs/ablations/<name>/; summarize in SUMMARY.md; update docs and regenerate 2-page SOLUTION_DOC.pdf; ensure Next.js viewer works without new pages.`
- **Scope:** `src/`, `config/`, `run.py`, `eval/`, `app/`, `lib/`, `tests/`, `outputs/ablations/`, `SOLUTION_DOC.md`, `SOLUTION_DOC.pdf`, `README.md`, `AGENTS.md`
- **Out of scope:** Hand-picking subjective human ground-truth (user responsibility), extending composites (explicitly out of scope, docs only), modifying Next.js page structure (viewer changes limited to display of new fields).

## Status

**State:** `COMPLETE`

**Current sentence:** `All tasks completed, ablations run and committed, test suite passing (46/46), Next.js build clean, 2-page SOLUTION_DOC.pdf regenerated, and summary report ready.`

**Completion criteria:**

- [x] Product framing & prompt changes: "stakes legible within 3s", `conversion_intent` (0-10) + reason, `payoff_location` with beat verification, auditor pay-to-see question.
- [x] Scoring: weights defined in `src/constants.py` (hook 0.30, cliffhanger 0.25, payoff_withheld 0.20, injustice 0.15, clarity 0.10, conversion_intent 0.0 default).
- [x] Six LLM stages implemented as flags (off by default): `--cold-read`, `--audit-panel`, `--rerank`, `--auto-profile`, `--consolidate-taxonomy`, `--recheck-empty`.
- [x] Editor handoff: `--export-csv` with required columns and timecodes in mm:ss.ss.
- [x] Evaluation: extend `eval/recall.py` (handles missing ground truth gracefully); run ablations and generate `outputs/ablations/SUMMARY.md`.
- [x] Doc corrections: `SOLUTION_DOC.md` (fix invented types 9/15 hooks, 12/15 cliffhangers, quiet scenes, conversion framing, tool audit artifact), `AGENTS.md` (TODO for user design attribution), `README.md` (all new flags documented), 2-page `SOLUTION_DOC.pdf`.
- [x] Verification: all existing tests pass + comprehensive tests for new stages, fake provider hallucination rejection, CSV export, weight configs; `next build` passes.

## Plan & Execution

| Step | Status | Evidence / result |
| --- | --- | --- |
| 1. Backup baseline run to `outputs/ablations/baseline/` | DONE | `outputs/ablations/baseline/` populated |
| 2. Scoring weights in `src/constants.py` & `src/models.py` | DONE | Hook 0.30, Cliff 0.25, Payoff 0.20, Inj 0.15, Clarity 0.10, Conv 0.0 |
| 3. Payoff location beat validation in `src/validation.py` | DONE | `verify_payoff_location` snaps to real spoken beat edges |
| 4. Prompts update in `src/prompts.py` | DONE | Reframed on curiosity gap, 3s stakes, conversion intent, payoff location |
| 5. Extractor & Auditor integration | DONE | Candidate `stages`, `conversion_intent`, auditor conversion score |
| 6. Implement 6 LLM stages + `--export-csv` in `src/stages.py` & `run.py` | DONE | Stages A-F, parallel cold read & panel, CSV export |
| 7. Update Next.js viewer (`app/page.tsx`) | DONE | Renders payoff location, conversion intent, stages; `npm run build` passes |
| 8. Extend `eval/recall.py` | DONE | Handles unmeasured ground truth gracefully, supports `--all-ablations` |
| 9. Run ablations and generate `outputs/ablations/SUMMARY.md` | DONE | All 5 ablation variants measured and documented |
| 10. Update docs (`SOLUTION_DOC.md`, `README.md`, `AGENTS.md`) & generate PDF | DONE | 2-page `SOLUTION_DOC.pdf`, accurate counts, composite future work |
| 11. Add unit tests and verify all tests pass | DONE | 46/46 tests pass in `python3 -m unittest` |

## Work log

### 2026-11-07 19:23 IST — Run initialization & Model/Weight updates
- **Changed:** `outputs/ablations/baseline/` created; `src/constants.py` and `src/models.py` updated.

### 2026-11-07 19:35 IST — Validation, Prompts, Modular Stages, Next.js UI
- **Implemented:** `verify_payoff_location()`, `src/prompts.py` reframed, `src/stages.py` created with Stages A-F and CSV export.
- **Updated:** `app/page.tsx` updated with conversion fields. Verified Next.js builds cleanly.

### 2026-11-07 19:45 IST — Ablation Runs & Real Show Pipeline Execution
- **Executed:** Ablation suite across 50 episodes; generated `outputs/ablations/SUMMARY.md`.
- **Generated:** `config/shows/broken_soldier.generated.yaml` (Stage D), `config/taxonomy.suggested.yaml` (Stage E), `outputs/promos.recheck.json` (Stage F).
- **Executed:** Baseline `python run.py` completed end-to-end (110 calls, 60 candidates audited, 34 pass, 15 ranked).
- **Executed:** `python run.py --export-csv` generates `outputs/promos.csv`.

### 2026-11-07 19:53 IST — Documentation, PDF Generation & Verification
- **Updated:** `SOLUTION_DOC.md` updated with measured figures, conversion framing caveat, quiet scenes analysis, composite design rules.
- **Generated:** `SOLUTION_DOC.pdf` compiled via Headless Chrome (verified exactly 2 pages).
- **Updated:** `README.md` and `AGENTS.md` (marked TODO for user design attribution).
- **Tested:** All 46 unit tests pass.
