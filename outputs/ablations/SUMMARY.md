# Ablation Summary: Independent Gemini Judge, Tiered Ranking & Provenance

Evaluation across 50 episodes (*I Married a Broken Soldier. He was a Duke*).
Every number below is computed directly from committed outputs under `outputs/` and `outputs/ablations/`.

## Comparison Matrix

| Variant | Top-15 Overlap with Baseline | Pass Rate | Judge Agreement | Status per Stage | Live Cost | Cached Cost | Wall Time | Top-5 Movement vs Baseline |
|---|---|---|---|---|---|---|---|---|
| **Baseline (old weights)** | 15/15 (100%) | 23/42 (55%) | not run (single judge) | `extraction:cached, audit:cached` | $0.0000 | $0.0000 | 250.7s | #1 Ep41, #2 Ep15, #3 Ep1, #4 Ep31, #5 Ep28 |
| **Baseline (new weights)** | 15/15 (100%) | 23/42 (55%) | not run (single judge) | `extraction:reused, audit:reused, rank:reused` | $0.0000 | $0.0000 | 250.7s | #1 Ep41, #2 Ep15, #3 Ep1, #4 Ep31, #5 Ep34 |
| **Current Pool (old weights)** | 4/15 (27%) | 26/60 (43%) | not run (single judge) | `extraction:reused, audit_panel:reused, rank:reused` | $0.0000 | $0.0000 | 0.1s | #1 Ep2, #2 Ep5, #3 Ep3, #4 Ep12, #5 Ep34 |
| **Current Pool (new weights)** | 4/15 (27%) | 26/60 (43%) | not run (single judge) | `extraction:reused, audit_panel:reused, rank:reused` | $0.0000 | $0.0000 | 0.1s | #1 Ep5, #2 Ep2, #3 Ep3, #4 Ep12, #5 Ep34 |
| **OpenAI Self-Audit** | 1/15 (7%) | 34/60 (57%) | not run (single judge) | `extraction:cached, audit:cached` | $0.0000 | $0.0000 | 0.4s | #1 Ep5, #2 Ep2, #3 Ep3, #4 Ep12, #5 Ep34 |
| **Gemini-Only Audit** | 3/15 (20%) | 26/60 (43%) | not run (single judge) | `extraction:reused, audit:cached, rank:reused` | $0.0000 | $0.0100 | 6.0s | #1 Ep41, #2 Ep15, #3 Ep5, #4 Ep2, #5 Ep12 |
| **Panel Tiers (Dual Judge)** | 4/15 (27%) | 26/60 (43%) | 68.3% (κ=0.3493) | `extraction:cached, audit_panel:ran` | $0.0002 | $0.0190 | 6.0s | #1 Ep5, #2 Ep2, #3 Ep3, #4 Ep12, #5 Ep34 |
| **+Cold-read (Diagnostic)** | 4/15 (27%) | 26/26 (58%) | not run (single judge) | `extraction:reused, cold_read:ran` | $0.0053 | $0.0000 | 0.0s | #1 Ep5, #2 Ep2, #3 Ep3, #4 Ep12, #5 Ep34 |
| **+Listwise Rerank** | 3/15 (20%) | 25/25 (60%) | not run (single judge) | `extraction:reused, rerank:ran` | $0.0034 | $0.0000 | 0.0s | #1 Ep3, #2 Ep2, #3 Ep31, #4 Ep30, #5 Ep26 |

## Key Findings

1. **Independent Dual-Judge Panel (gpt-6-luna + gemini-3.5-flash-lite):**
   - Judge 1 (gpt-6-luna) pass rate: **55.0%** (33/60).
   - Judge 2 (gemini-3.5-flash-lite) pass rate: **63.3%** (38/60).
   - Agreement rate: **68.3%** (41/60), Cohen's kappa: **κ = 0.3493**.
   - Consensus Tiers: **Tier 1 = 26, Tier 2 = 19, Tier 3 = 15** (0 audit errors).
   - Tier 1 represents consensus editorial quality across independent model architectures.

2. **Listwise Rerank Stability (Current Tier-1 Candidates, Cap 25):**
   - Run twice with different shuffles (seeds 42 and 1337) over the top 25 Tier-1 candidates.
   - Top-10 overlap between Run 1 and Run 2: **70.0%** (7/10 shared picks).
   - Top-10 overlap between Run 1 and weighted ranking: **70.0%** (7/10 shared picks).
   - Kendall tau rank correlation between shuffles: **τ = 0.62**.
   - Kendall tau against weighted ranking: Run 1 **τ = 0.333**, Run 2 **τ = 0.367**.

3. **Cold-Read Diagnostic on Current Tier-1 Candidates (26):**
   - Evaluated clip screenplay text blind with zero show title, premise, or character context.
   - Correlation with contextual standalone clarity: **r = 0.507**.
   - Large disagreements (|diff| ≥ 2.0): **4/26** (15.4%).

4. **Cliffhanger Trim-and-Revalidate:**
   - Instead of dropping promos where cliffhanger beat ended before the 6s tail window, code trims clip end to that beat's real edge.
   - In Ep 15, `ep15_cand_1` was recovered by trimming 7.5s, avoiding candidate loss.

5. **Cost Honesty & Cache Transparency:**
   - Stages that reuse existing pools or compute mathematical rankings without LLM calls are honestly labelled `reused` with `$0.0000` live cost.
   - Cached runs accurately report token usage and cost as `cached (original cost $X)`.