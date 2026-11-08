# Kuku Promo Finder: Find the Promos (Problem 1)

**Author:** Rakshit · **Repo:** `run.py` (engine), `app/` (Next.js viewer) · **Run:** `outputs/promos.meta.json`

## 1. Problem, Product Framing & Scope
An editor watches every episode to pick 20-60s promos by hand, and new shows ship weekly. The tool reads timestamped screenplays and returns ranked promos: episode, every segment's start/end, hook, cliffhanger, and why it converts.
- **Conversion Framing:** A promo exists to create a curiosity gap strong enough that a viewer installs the app and pays to see the next moment. It does not summarize the plot and does not protect against spoilers; late-episode reveals are valid picks. Priorities: stakes legible within 3s, an immediate scroll-stopping hook, and unresolved payoff withheld at the cut. "Understood cold" is a secondary sanity check.
- **Assumptions & Caveats:** Screenplay text is the only input (no video), so visual judgements rely strictly on stage directions. Promos are single-episode cuts (composites remain experimental and disabled). *Conversion priority is an editorial assumption based on observed microdrama ad mechanics; there is no live conversion data.*

## 2. Approach: Code Enforces Constraints, AI Judges Drama
| Step | Owner | Why |
|---|---|---|
| Parse 50 episodes into 3,727 timed beats | Code (`src/parser.py`) | Timestamps must be mathematically exact |
| Window discovery, tag hook/cliffhanger, score drama, conversion intent & payoff location | LLM (`gpt-6-luna`, one call per episode) | Identifies dramatic tension, emotional betrayal, and curiosity gaps |
| Hard constraints: 20-60s, hook starts ≤3s, cuts on real beat edges (snap ≤0.5s), verbatim quotes, cliffhanger in final 6s, payoff beat verification | Code (`src/validation.py`) | Models hallucinate timestamps and quotes. Cuts within 0.5s snap to spoken edges; others drop. Hallucinated payoff locations are discarded. |
| Dual-Judge adversarial audit panel (`gpt-6-luna` + `gemini-3.5-flash-lite`): inspects clip dialogue, camera beats, and taxonomy definitions | LLM panel (`src/stages.py`, `src/auditor.py`) | Catches resolution leaks, context deficits, visual dependency, and tag mismatches |
| Tiered Rank: consensus tiers (Tier 1 > Tier 2 > Tier 3) + editorial weights + diversity penalty | Code (`src/constants.py`, `src/ranker.py`) | Tier 1 (both judges pass) ranks first, then Tier 2 (split verdict: "needs editor look"). Repeat penalties prevent feed monotony. |

**Scoring Weights (editorial priors, uncalibrated):** `hook 0.30`, `cliffhanger 0.25`, `payoff_withheld 0.20`, `injustice_tension 0.15`, `standalone_clarity 0.10`, `conversion_intent 0.00`.

## 3. Results & Measured Ablations (`outputs/ablations/`)
- **Headline Run (50 episodes):** 62 candidates proposed, 62 valid, 60 deduped across the season.
- **Independent Dual-Judge Panel (`gpt-6-luna` + `gemini-3.5-flash-lite`):**
  - Evaluated on all 60 candidates: Judge 1 pass rate **55.0%** (33/60), Judge 2 pass rate **63.3%** (38/60).
  - Raw agreement rate is **68.3%** (41/60), with Cohen's kappa **κ = 0.3493** (fair consensus).
  - Consensus audit tiers: **Tier 1 = 26, Tier 2 = 19, Tier 3 = 15** (0 audit errors). All 15 headline promos are Tier 1 consensus picks.
  - Gemini failed 3 previous top-15 promos: `ep28_cand_2` (`resolution_leak`: reveals execution & herbarium book evidence), `ep46_cand_1` (`resolution_leak`: High Priest dialogue resolves core mystery), and `ep34_cand_1` (`slow_burn`: courtroom preamble takes 15s to establish stakes).
- **Cliffhanger Trim-and-Revalidate:** When a cliffhanger beat ends before the final 6s tail window, code trims the cut to the beat's real end edge and re-verifies all hard constraints. In Ep 15, `ep15_cand_1` was recovered by trimming 7.5s (41.2s -> 33.7s).
- **Empty Episode Diagnosis:** 6 empty episodes remain in the main pool (`[6, 8, 10, 11, 17, 25]`). Episodes 6, 8, 10, 17 returned 0 model proposals (genuinely quiet dialogue); Episode 11 had cliffhanger quotes ending after cut points; Episode 25 had unsnapped start cuts. Episodes 3, 14, 22, 24, 38, 44, 47, 49 now yield valid candidates.
- **Payoff Location Verification:** 5 of top 15 promos have a code-verified payoff_location in the screenplay (Rank 2 Ep 2 `00:37.50`, Rank 3 Ep 3 `01:24.00`, Rank 13 Ep 35 `02:25.50`, Rank 14 Ep 18 `01:51.50`, Rank 15 Ep 1 `01:10.60`). The other 10 are `unknown` because the conflict resolves in later episodes or model-proposed timestamps did not snap to real beat edges (preventing hallucinated timestamps).

## 4. Failure Modes, Taxonomy Fit & System Limits
- **Invalid Offline Audit Replaced:** An earlier keyword audit passed 87/87 candidates due to unreachable score thresholds (`outputs/smoke_test_heuristic/promos.json`, commit `809d946`). Fixed: audits are labelled by method (`llm`/`rules`/`error`), rule lint is distinguished from quality, and single-judge runs refuse same-model self-auditing unless `--allow-self-audit` is explicit.
- **Taxonomy Mismatch:** In the top 15, **10 of top 15 hooks and 13 of top 15 cliffhangers** carry a model-proposed `new:` tag (e.g. `new:threatened_last_keepsake`). Novel tags receive default weight (0.90), so fine-grained taxonomy weights barely differentiate ranking without taxonomy consolidation.
- **Why Composites are Disabled:** Naive pairing across episodes severed character and emotional continuity. Safe composites require hook-first cuts followed by setup scenes with identical character IDs, validated by blind cold-read scoring.
- **Ground Truth & Recall:** Without a human-labeled ground truth (`eval/ground_truth.json`), absolute recall and precision remain **unmeasured**.

## 5. Human in the Loop & Editor Handoff
Editors review picks via the Next.js viewer or `outputs/PROMOS.md`, displaying audit tier badges, dual-judge critique breakdowns, flaw types, and cliffhanger trim indicators. `--export-csv` outputs `outputs/promos.csv` with one row per segment formatted in `mm:ss.ss` with verbatim quotes and verified `payoff_location`.

## 6. Cost & Execution Profile (Measured)
- **Committed Headline Run:** Extraction and audit panel executed with caching across OpenAI `gpt-6-luna` and Gemini `gemini-3.5-flash-lite`. Cached cost is **$0.0190**, with **$0.0002** live cost from discovery probes. Pure re-ranking is **$0.0000** and runs in **<0.1s**.
- **Stage Modularity:** Rerank, cold-read, and panel stages run independently with full token and cost provenance recorded in meta files.

## 7. Tools Used
Antigravity and Claude Code were used for pipeline implementation, validation harness, and UI. Runtime LLMs are OpenAI `gpt-6-luna` (extraction) and Google Gemini `gemini-3.5-flash-lite` (independent audit judge). See `AGENTS.md` for AI failure log.
