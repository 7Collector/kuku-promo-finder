# Kuku Promo Finder: Audit Against PS.md (Problem 1)

Audited 2026-11-07 at commit `809d946`. No source files were changed; every run used a scratch clone in `/tmp/kuku-audit`. The earlier `AUDIT.md` was not read or used (moved to `/tmp/kuku-audit/AUDIT.old.md`). Per your decision, Next.js is the only UI: `app.py` is treated as to-be-removed (M12) and the human-review claim is judged against Next.js alone.

## 1. Verdict

**Not submittable today.** The core pipeline runs and its timestamps are sound, but the submission misdescribes what it is.

1. **Wrong engine, empty audit.** `outputs/promos.json` is keyword-heuristic output with a rule audit that cannot fail (15/15 pass). The project's own LLM auditor passes **2/15** of those same promos.
2. **Numbers that don't hold up.** "100% recall" has no ground truth behind it, "84% pass" matches no run, and cost and runtime are off by 19× and 10×. The Rank 1 story is also wrong.
3. **Demo and interview failure modes.** `/analyze` is a regex that praises "Hello there" (8.79, "Excellent emotional hook") with two invented presets. Unparseable input exits 0 and overwrites outputs with `[]`. Also: no PDF, no repo link.

---

## 2. Brief compliance

| Requirement | Status | Evidence |
|---|---|---|
| Episode, ordered segments, hook, cliffhanger, one-line why | **PARTIAL** | All fields exist, but `Segment` has no episode field (`src/models.py:62`), so composites rely on list position. `why_it_works` is 2 templates across 87 candidates: 81 "Cold viewers instantly lock onto X's confrontation…" and 6 "…lock onto the sudden confrontation…". |
| 20–60s total | **PASS** (output), **PARTIAL** (code) | Recomputed from raw timestamps: 15/15 within 20.10–45.70s. Code tolerates 19.5–60.5 (`src/ranker.py:28`) and 18–65 at intake (`src/extractor.py:123`). |
| Cut points are real beat boundaries | **PASS** (output), **FAIL** (enforcement) | Independent parser: 15/15 committed, and 0 of 63 segments off-beat in the live pool. Nothing in code checks this: a fake provider's window passed `validate_constraints` with no comparison to any beat. Rank 7 ends at 01:32.20, inside dialogue beat 01:32.10–01:33.20 ("That is his coat!"), so the line is cut off. |
| Hook within first 3s | **PASS** (mechanical), **PARTIAL** (real) | Delay is 0.00s on 15/15 because heuristic windows start on the tagged beat. Code allows 3.5s (`src/ranker.py:36`). Several "hooks" don't hook: "What wedding?", "Every one, my Lord." |
| Quotes verbatim at stated timestamps | **PARTIAL** | Substring match on 15/15 after removing an artifact, but Rank 6's cliffhanger contains literal `--- SCRIPT END ---`, Rank 3's hook and Rank 12's cliffhanger are cut at 120 chars mid-sentence (`src/extractor.py:316,324`). The live pool has 3 of 58 candidates with non-verbatim `ACTION:`/`SFX:` prefixes. No code validates quotes. |
| Real hook, unresolved end, makes sense cold | **PARTIAL** | My read of all 15 (end of §3): 3 strong, 5 usable with trims, 4 weak, 3 should not ship. |
| Ranking with rationale | **PARTIAL** | Ranking exists and is monotonic. Doc rationale covers Rank 1 only, and that paragraph has false facts. In the committed run, scores are constants plus keyword bumps. Only `audit.passed` feeds in; `confidence_score` and `risks` are ignored. |
| Cross-episode composites | **PARTIAL** | One present (Rank 8, `comp_ep01_ep25`). It splices "What do you mean?" onto "Who?" from an unrelated scene. Pairing has no narrative logic (P3). |
| Quality check with real runs and honest failures | **FAIL** | Committed audit passes 87/87 with a templated critique. Real failures exist only in git history and in my live run; the doc's numbers match neither. |
| Reusable, model easy to swap | **PARTIAL** | OpenAI verified end to end. Anthropic will fail per its docs (M2). New show needs a hand-written YAML and exact screenplay format (§5). |
| Raw unedited output from all 50 episodes | **PARTIAL** | Byte-identical to a fresh heuristic run, so unedited. But only the top 15 of 87 are saved, and nothing records the engine. |
| Tools used + one AI failure in doc | **PARTIAL** | Present, with no logs or artifacts behind the examples (§4). |
| PDF ≤ 2 pages | **FAIL** | No PDF in the repo. `SOLUTION_DOC.md` rendered to **4 pages** (Chrome, 11pt Arial, default margins). |
| Prototype link | **FAIL** | `git remote` is empty and no URL appears in the docs. Vercel deployment is claimed but unverified. |

---

## 3. Findings

### Blockers

**B1. The submitted raw output comes from the keyword engine and doesn't say so. (S)**
- *Evidence:* a clean no-key run matches `HEAD:outputs/promos.json` byte for byte. The JSON has no engine field and `PROMOS.md` is titled "Official Ranked Promos". All 15 audits pass with `flaw_type: null` and templated critiques. `standalone_clarity` is 8.5 and `payoff_withheld` 9.0 on 87/87 (`src/extractor.py:288-289`). `withheld_payoff` is one sentence on 87/87.
- *Why it matters:* the doc's "Gave to AI" section describes semantic judgment that produced none of the delivered output. A reviewer who opens the JSON will see the templates.
- *Fix:* commit a live run as the raw output, add `engine`, `model` and `generated_at` to the output, and keep heuristic results in a separate labelled file.

**B2. The committed quality check cannot fail. (M)**
- *Evidence:* the rule audit fails only if `payoff_withheld < 7` or `standalone_clarity < 7` (`src/auditor.py:118-128`), and heuristics hard-code 9.0 and 8.5. Composites force 9.0 on both (`src/composite.py:147-148`). The lore tokens include the literal `alexander (the broken soldier / duke)`, which can never match. Result: 87/87 pass.
- *Measured contrast:* running the project's `PromoAuditor` with `gpt-6-luna` on the committed 15 gives **2 pass, 13 fail** (only ranks 3 and 5 pass). The full live pipeline gives **26/58 (45%)**.
- *Why it matters:* "where does your tool pick badly?" is one of three tasks in the brief.
- *Fix:* make the LLM audit the reported result, label rule checks as lint only, and publish real pass/fail counts plus failing examples. Remove `test_resolution_leak_detected` as evidence, since it uses `payoff_withheld=4.0`, which the heuristic path can't produce.

**B3. Quantitative and factual claims in the doc are unsupported or contradicted. (S)**
- *100% Top-10 recall against "5 human-edited moments":* no list exists anywhere in the tree or history, and there is no earlier artifact. All five items are in this same run's top 10, including `comp_ep01_ep25`, which is simply the first pair the algorithm found. `CLAIMS_VERIFICATION.md:186` records a reviewer telling you to add this metric, and the claim arrives in the same commit (`809d946`) as this output. **If you did pick these before the run, commit the list and say when; otherwise delete the claim.** A reviewer would treat it as fabricated.
- *84% pass rate:* matches no run. Committed: 100% (87/87). Historic live: 33% (5/15, `66940d3`). Mine: 45% (26/58). "87 candidates" is the heuristic count; the two numbers appear to come from different engines.
- *Rank 1 paragraph (`SOLUTION_DOC.md:120`):* "the heirloom is shattered" is false. It's thrown into a puddle, and the script says "They dirtied it. That is not the same thing." The live auditor independently flagged this on `ep05_cand_1`: "The claimed destruction never happens". Clarissa isn't "screaming" (she's "Gleeful, Mocking"). "0.00s context deficit" is not a metric the code computes.
- *Cost and runtime:* see §4.
- *Fix:* replace them with measured numbers from one named run.

**B4. `/analyze` is presented as the adversarial auditor but is a regex with invented demo data. (S to remove)**
- *Evidence:* `app/api/analyze/route.ts:59-63,89-97` sets hook strength by `hookQuote.length > 5` and clarity and payoff as constants, and passes anything of valid duration. POST with `"Hello there"` / `"Have a nice day and resolved all"` returns composite 8.79, passed, "Excellent emotional hook; cuts at peak tension before retribution." Timestamps `99:00–99:25` also pass. It never reads a screenplay.
- *Invented presets:* "Crawl through the blackthorn" (Ep 12 preset) and "Who dares enter", "royal sanctuary", "full ducal crest" (Ep 42 preset) occur in **0 of 50** files (`app/analyze/page.tsx:30-46`). AI-generated dialogue in the demo of a tool whose pitch is timestamp and quote fidelity.
- *Fix:* delete the page and route, or relabel it "duration and taxonomy calculator", with no audit verdict and presets taken from real beats.

**B5. Required deliverables are missing. (S)**
- *Evidence:* no PDF, doc is 4 pages rendered, no remote or deployed link, no video (optional).
- *Fix:* cut to 2 pages (drop the ASCII pipeline and the model list; §6), export the PDF, push the repo. Deploy Next.js only if it fits the time.

### Major

**M1. Bad input succeeds silently and destroys the previous output. (S)**
*Evidence (all exit 0):*

| Input | Result |
|---|---|
| Nonexistent directory | 0 episodes, `[]` written |
| SRT timestamps (`00:00:11,300`) | 0 beats, `[]` written |
| No `**bold**` headers | 0 beats, `[]` written |
| Plain screenplay, no timestamps | 0 beats, `[]` written |
| No `EPISODE NUMBER` line | All episodes become Ep 1 (`src/parser.py:79`), dedup silently reduces 6→2, wrong labels |
| Malformed beat lines | Dropped with no warning (287→284); end-before-start beat kept |
| Missing episode | No warning; composite cutoffs compare `len()` to episode numbers (`src/composite.py:40-41`) |
| Empty file | Counted as parsed, given episode number 1, collides with the real Ep 1 |

Defaults point at the submitted `outputs/` files. *Why:* the interview runs on a new input. *Fix:* non-zero exit on 0 beats, a parse report, no output write on empty, per-show output folders.

**M2. `--provider anthropic` will fail on its default model. (S)**
*Evidence:* `src/providers/anthropic.py:46` sends `temperature: 0.2`. [Anthropic's docs](https://platform.claude.com/docs/en/models/sonnet-5-5/overview) say that on `claude-sonnet-5-5`, "Setting `temperature`, `top_p`, or `top_k` returns a 400 error." Adaptive thinking is also on by default, while the adapter reads only `content[0]` (`:58`), which may not be the text block. Not run, as there is no Anthropic key. Combined with M3, every call would fall back to heuristics while the log prints `Active Engine: anthropic`. *Fix:* drop `temperature`, select text blocks by type, test once with a key.

**M3. Failures degrade silently into a different engine that outranks real LLM results. (M)**
*Evidence:* `--provider anthropic` with no key: exit 0, 137 warnings, output byte-identical to heuristic, header says anthropic. `--provider bogus` silently uses heuristic (`src/providers/factory.py:53`). There are no retries, no 429 handling and no per-candidate provenance. Heuristic raw scores start at 7.38 and 52 of 58 live candidates score below that, so one failed episode's keyword clip would beat almost all real ones. *Fix:* fail fast on auth or unknown provider, retry on 429/5xx, tag each candidate's engine, never mix engines in one ranking.

**M4. LLM output is trusted without validation. (S–M)**
*Evidence from a fake provider:* an invented hook quote was accepted, as was the type `new:made_up`, cliffhanger timestamp `09:99.00`, and `hook_strength: 99` (composite 25.28, on a "/10" scale). `"pass": "false"` becomes `passed=True` (`src/auditor.py:87`). Malformed audit fields silently fall back to the rule audit, which then passes. *Fix:* require cut points to match beats, quotes to match the beat at their timestamp, clamp scores to 0–10, parse with a strict schema, drop on failure and count drops. This is the claim AGENTS.md already makes.

**M5. Audit penalties don't work as documented. (S)**
*Evidence:* the 0.65× multiplier requires `flaw_type == "resolution_leak"` exactly (`src/ranker.py:125`), but the prompt requests free text. Live: **0 of 32** failures carried that value, including 2 whose text mentions resolution. A failing candidate outranks passing ones (live Rank 9 FAIL above PASS at 10, 13, 14), despite the log line "passing promos prioritized". *Fix:* enum for flaw types; rank all passes above all fails, or say plainly that it's a soft penalty.

**M6. Self-grading, and an auditor missing inputs. (S–M)**
*Evidence:* same provider instance for extraction and audit (`run.py:61,121`). `CLAIMS_VERIFICATION.md` M5 says this was "RESOLVED" with independent model config; no such code exists. The auditor gets the extractor's pitch, but no show context and no taxonomy definitions, so it can't apply `requires` or `do_not_tag_if`. Camera beats are excluded (`src/auditor.py:55`), though failure mode 3 is about visuals. Extractor scores don't predict the audit: passers vs failers average clarity 7.27 vs 7.30 and payoff 8.50 vs 8.78. *Fix:* `--audit-model`, pass definitions and camera beats, drop the extractor's claim.

**M7. Prompts receive wrong or thin data, and useful output is discarded. (S)**
*Evidence:* the "previous episode summary" is the *current* episode's logline (`run.py:73`). Only the protagonist's name is sent (`src/extractor.py:75`), not antagonists or premise detail. The model analyzes one episode at a time, so it can never propose a cross-episode promo. Candidate `risks` and all 123 `rejected_near_misses` are discarded. *Fix:* use the actual prior logline, send cast, save rejects as quality evidence.

**M8. Heuristic tags are mostly fallback noise, and "diversity" depends on them. (M, or S if you stop presenting heuristics as the product)**
*Evidence:* `interrupted_retaliation` is on 14/15 promos and 82/87 candidates because it's the `else` branch (`src/extractor.py:271`). By my read it fits ranks 1 and 3 and arguably few others; it's on "Like a circle?" and on a clutched blanket. Rank 4 is `secret_status_reveal` only because "my Lord" is a cue. Rank 6 is `life_or_death_defiance` with no peril. 63/87 hooks are `public_humiliation`, the hook fallback. *Fix:* use heuristics as a labelled smoke test only.

**M9. Composites are arbitrary and their scores are invented. (M)**
*Evidence:* pairs the first early and late candidates passing thresholds every heuristic candidate meets (19/19 and 49/49), with no plot, character or score logic (`src/composite.py:59-96`). Scores are floored: clarity 9.0, payoff ≥9, hook ≥8.5, which gives the composite the second-highest raw score among the committed 15 (8.82) and Rank 1 on the new-show test. The LLM auditor on `comp_ep01_ep25`: "abruptly cuts from 'What do you mean?' to 'Who?' with no audible or clear narrative bridge". *Fix:* have the LLM pick and justify pairs from a show-level candidate list, or remove composites and state the limit. The brief says "can", not "must".

**M10. Cost, token and time claims are wrong by large factors. (S)** See §4. Doc: ~171k tokens, <5¢, 20–25s. Measured: 538k tokens, 227s, ~$0.13 on gpt-6-luna, ~$0.95 estimated on Gemini.

**M11. No cache, no checkpoint. (M)**
*Evidence:* no caching in `src/`, outputs written only at the end. Every re-run re-spends all 108 calls and ~4 minutes; a crash at call 107 loses everything. For an interview run this is a real risk. *Fix:* disk cache keyed on hash of prompt and model, 30 lines.

**M12. Streamlit is to be removed, and "human in the loop" has no implementation. (S)**
*Evidence:* Next.js has no approve, reject, trim or export control (grep on all pages), and `app.py` has no buttons at all (AppTest: runs with no exceptions, `buttons=[]`). `SOLUTION_DOC.md:135` claims "one-click approve, trim, or reject". Remove `app.py`; `streamlit` and `pandas` from `requirements.txt`; references at `README.md:22-23,112,121` and `SOLUTION_DOC.md:6,135,143`. *Fix:* describe the human step honestly (editor reviews the ranked report), or add one approve/reject control with JSON export.

**M13. Internal process files in the repo contradict the submission. (S)**
*Evidence:* `CLAIMS_VERIFICATION.md` opens "100% Verified" and marks items resolved that aren't (M5; L3 "calibrated", with no calibration anywhere). It also quotes reviewer feedback. `PROGRESS.md` says "None. All requested issues have been resolved". *Fix:* remove these and `progress/` from the submission.

**M14. Gemini API key can leak into logs. (S)**
*Evidence:* the key is in the URL (`src/providers/gemini.py:34`). A fake key produced: `400 Client Error: Bad Request for url: …:generateContent?key=FAKEKEY123`. `src/extractor.py:54` logs that exception text. *Fix:* use the `x-goog-api-key` header.

**M15. Next.js duplicates logic and has show-specific hard-coding. (S–M)**
*Evidence:* the app uses **static JSON** for promos, plus a **TypeScript re-implementation** of the parser and scoring formula; it never calls Python. `\Z` in JS regex is not an end anchor (`app/api/episodes/route.ts:30,35`), so `/episodes` **drops the final beat in 50/50 episodes** (e.g. 94 vs 95). `?ep=999` returns Ep 999 with the contents of episode 1. Show path is hard-coded (`route.ts:10`), as are "50 episodes · 3,727 beats" (`app/layout.tsx:134`, `app/page.tsx:194`) and the 50-episode list (`app/episodes/page.tsx:38`). The UI shows "Passed audit" on heuristic results. *Fix:* have Python emit a beats JSON for the UI to read, and derive counts from data.

### Minor

| ID | Finding | Evidence | Effort |
|---|---|---|---|
| m1 | Parser keeps `--- SCRIPT END ---` in the final beat, 50/50 episodes | Rank 6 cliffhanger; `src/parser.py:27` | S |
| m2 | Dead code | `src/auditor.py:144-156` after `return`; `src/llm_client.py` unused; `rich` never imported | S |
| m3 | `config/shows/` is never read; identical to `show_context.yaml` apart from comments | `grep shows/ src run.py` is empty; doc says to add a show there | S |
| m4 | Weights are uncalibrated; diversity defaults differ between code (0.88/0.90) and call (0.82/0.85) | `src/ranker.py:88-89`, `run.py:144` | S |
| m5 | "MMR" is a tag and episode count penalty; no similarity, text or character term | `src/ranker.py:112-117`; `IDEA.md` line 56 names MMR, but nothing implements it | S (rename) |
| m6 | Heuristic ties favour shortest window: 10/15 promos ≤ 25s, end beat not chosen on quality | Sort at `src/extractor.py:345` | M |
| m7 | Stage labels mix `[n/5]` and `[n/6]`; two "6"s | `run.py:45,105,148` | S |
| m8 | Speaker names unmerged: `JULIANA` / `LADY JULIANA`; `THE FORMER GROOM` / `GERALD`. Cold-viewer why-text exposes screenplay labels such as "LADY IN GOLD GOWN" | Parser output | M |
| m9 | Fonts stored twice, zip duplicates the assets, 246 of 358 tracked files are `Design/` | `git ls-files` | S |
| m10 | README tree omits `progress/`, `public/`, `src/llm_client.py`. `PYTHONPATH=.` is unnecessary (works without it) | Clean run | S |

### Quality-check gap: my read of all 15 committed promos

| # | Promo | My verdict | Why | LLM audit |
|---|---|---|---|---|
| 1 | Ep5 00:59–01:40 | Usable | Opens *after* the ledger is thrown (00:54.50), so the hook refers to something unseen. 15s comfort sag in the middle. Great last line | FAIL |
| 2 | Ep2 00:00–00:23 | **Strong** | Instant, clear, cold-friendly. Ending is a cruel line, not a true cliffhanger | FAIL |
| 3 | Ep15 00:47–01:07 | **Best** | Shove, blood, club raised, Alexander charges. Mis-tag aside, it's what the brief asks for | PASS |
| 4 | Ep33 01:09–01:32 | Weak | "She" unexplained, "Like a circle?" means nothing cold. Hook tag is a cue collision | FAIL |
| 5 | Ep20 00:15–00:39 | Weak | Villains plotting; opens on a reply to a missing line; names unknown people. Answered next line | PASS |
| 6 | Ep44 00:49–01:10 | **Don't ship** | Spoiler: Duke rejects Catherine, which *is* the comeuppance, and picks Juliana. The LLM auditor failed it on dead air, not the spoiler | FAIL |
| 7 | Ep11 01:07–01:32 | Usable | Good tension; "one blow would destroy her life". Cuts a line in half at the end | FAIL |
| 8 | Ep1+25 composite | **Don't ship** | Unrelated scenes; "What do you mean?" → "Who?" | FAIL |
| 9 | Ep46 01:41–02:03 | Weak | Legal jargon opener; solid final threat; heavy backstory | FAIL |
| 10 | Ep29 01:24–01:48 | Usable | Strong first 20s; ends on a soft V.O., one line before the much better "they will not take Alexander" | FAIL |
| 11 | Ep36 02:26–03:12 | Usable | "What wedding?" is a weak open, but "Because before that wedding begins…" is the best cut in the set. Start later | FAIL |
| 12 | Ep40 01:06–01:50 | **Don't ship** | "Every one, my Lord." opener; nearly 15s without dialogue (01:17.40–01:32.00); ends on smiles | FAIL |
| 13 | Ep26 00:30–00:55 | Weak | Quiet bedside scene tagged class contempt; ends on clutching a blanket, just before the poison line | FAIL |
| 14 | Ep12 00:00–00:23 | **Strong** | Arrest on line one, clear injustice, low threat ending | FAIL |
| 15 | Ep3 00:02–00:43 | Usable | Clear, cruel, sustained; could lose 15s | FAIL |

**Tally: 3 strong, 5 usable, 4 weak, 3 don't ship.** The LLM auditor is not ground truth either: it failed promos I rate strong (2, 14) and passed one I rate weak (5). It's more specific but uncalibrated, and both opinions here are unvalidated.

**Ground truth:** none exists. There are **no hand-picked promos** in the repo, so recall and precision are currently unmeasurable.

**Zero-candidate episodes:** only two exist, Ep 6 and Ep 8, and both engines agree. I read both. Ep 6 (cottage, rain, comfort) and Ep 8 (herbs, beard jokes, gentle bonding) have no conflict; **no good promo was missed**. As a third sample I read Ep 9 (one candidate): the rumor tag at 01:28 is the right choice, though the sick-child scene to "Why isn't it working?" (00:06–00:54) could also have worked.

**Hook diversity in top 10: an artifact.** With penalties at 1.0, the top 10 is **100% `public_humiliation`**. With penalties it shows 8 types, but I judge 4 of the 10 tags wrong (ranks 4, 5, 6, 9) and rank 8 arguable. Rank 15 (raw 8.80) falls below Rank 9 (raw 6.64) purely on penalties. The variety is largely label variety.

**Promos that pass the project's own audit:** 15/15 per committed output, 2/15 under its LLM auditor, 11/15 of the fresh live top 15. The docs reflect none of these.

**Live vs heuristic:** only 4 promos overlap in time out of 15; 6 of 15 share an episode. Live Rank 1 is Ep3 ("Wherever a discarded daughter belongs."), and Ep 5, the heuristic Rank 1, is live Rank 12 with a longer cut (00:49–01:40), failed. Live also emits `new:*` tags on 32/58 hooks and 39/58 cliffhangers, which get the default 0.80 weight, an unintended penalty (`src/taxonomy.py:67`).

### Pipeline and design notes
- **Parser overlap:** 1,952 adjacent beats overlap (mostly camera) and 8 go backward. Kept as-is, which is correct for overlap but not checked for ordering. Precision variants `mm:ss`, `mm:ss.sss` and CRLF all work.
- **Window discovery:** heuristic windows can only start on a dialogue or action beat matching a cue or emotion word, and can't be multi-segment. Windows may span scene breaks (ranks 12, 15 span 2 scenes). No payoff or resolution analysis at all. LLM sees whole episodes minus camera beats, one at a time.
- **Dedup:** threshold 0.35 of the shorter interval, strict `>`. Exactly 0.35 is kept, 0.36 removed, as documented. Adversarial: composites compare clock times across *different* episodes, so a promo with no real overlap was removed (`src/ranker.py:66-75`). A composite and the single-episode clip it reuses are both kept (`:59`).
- **Code vs LLM:** Rules: parsing, duration and hook windows, composite assembly, dedup, ranking formula. LLM: candidates, tags, 5 scores, quotes, audit verdict. All LLM fields are trusted apart from the duration and hook window (M4).
- **Tests:** real behaviour on ranker, dedup and prompt injection. Hand-built candidates elsewhere. `test_parse_assets_pack` is real but light.
- **Secrets:** clean. `.env` is ignored and absent from history; no keys in HEAD (`sk-` hits are CSS classes).
- **Scope:** over-built for 2–3 hours. Three UIs became two with this decision, plus 246 design files and a 988-line dashboard. Reviewers' first path should be one live run, one report, one short doc.
- **Audit spend:** roughly $0.14 on your OpenAI key (two pipeline runs + 15 audits).

---

## 4. Claims vs reality

| Claim | Where | Status | Evidence |
|---|---|---|---|
| 50 episodes, 3,727 beats | README, doc | **Supported** | Independent stdlib parser: 3,727 |
| Centisecond timestamps | README, doc | **Supported** | Source format `mm:ss.ss` |
| 14 unit tests | README, doc | **Supported, but limited** | 14/14 pass, 0 skipped, 0.1s. None imports `PromoExtractor` or a live provider adapter. They missed `SCRIPT END`, empty runs and the unfailing audit |
| Offline <2s | README, doc | **Supported** | 1.29s wall |
| Live ~20–25s | README, doc | **Contradicted** | **227s**, 108 calls. Mean extraction latency 25.4s, so 20s is about one call |
| 171k tokens per show | Doc | **Contradicted** | **538k**: 357,130 in + 180,869 out (141,484 reasoning) |
| ~2,500 tokens per extraction prompt | Doc | **Contradicted** | Mean 6,109 |
| ~35 audited clips, ~600 tokens | Doc | **Contradicted** | 58 clips; 891 in + 694 out each |
| ~1,500 words per episode | Doc | **Contradicted** | 876 mean across beats |
| Gemini rates $0.075/$0.30; $0.02–0.04 per show | Doc | **Contradicted** | Search results for Google's [What's new](https://ai.google.dev/gemini-api/docs/latest-model) page give $0.75/$3.75 through 2026-12-31; $0.075 is reported as the *cached* input rate. Official pricing page not opened. Applying that to my token counts gives ~$0.95, an estimate since Gemini's reasoning use may differ. Measured on `gpt-6-luna`: ~$0.13 at [$0.10/$0.50](https://developers.openai.com/docs/models/gpt-6-luna) (output rate from aggregators) |
| 87 candidates | Doc | **Supported, heuristic only** | Live: 59 single + 2 composites → 58 |
| 84% passed cleanly | Doc | **Contradicted** | 100%, 33% or 45% depending on run; none is 84% |
| 100% Top-10 recall vs 5 editor picks | Doc | **Unsupported** | No ground truth exists (see B3) |
| "95% of the extraction chore" | Doc:133 | **Unsupported** | No measurement |
| One-click approve, trim, reject | Doc:135 | **Contradicted** | No such controls |
| `/analyze` tests against the adversarial auditor | README, Doc:136 | **Contradicted** | Regex and constants |
| Case: Ep 42 penalty "prevented a spoiler entering top ranks" | Doc:110 | **Contradicted** | Quote is real (`66940d3`), but it was **Rank 4** with no penalty code then |
| Case: Ep 01 clenched hand → tightened taxonomy | Doc:111 | **Supported** | Quote in `66940d3`; `do_not_tag_if` exists |
| Case: Ep 35 "led directly to" Composite Builder | Doc:112 | **Contradicted** | `src/composite.py` is in the first commit (`c68aac5`), before the flagged run (`66940d3`) |
| Rank 1 narrative | Doc:120 | **Contradicted** | See B3 |
| 100% config-driven for a new show | Doc:146 | **Contradicted** | §5 |
| New show = `config/shows/<x>.yaml` | Doc:146 | **Contradicted** | Directory never read; must pass `--context` |
| Hook ≤ 3.0s enforced by code | AGENTS | **Contradicted** | Code is 3.5s; doc elsewhere says 3.5 while reports say 3 |
| Every cut must match a beat | AGENTS, Doc:61 | **Contradicted as a control** | No check exists; true of outputs only because heuristics start from beats |
| Supported models | README | **Partly** | `gpt-6-luna`: in `/v1/models`, 108/108 HTTP 200. `claude-sonnet-5-5`: ID confirmed in docs, adapter will 400 (M2). `gemini-3.8-flash`: ID per Google's page in search results; adapter unrun, no key |
| Deterministic ranking | Doc | **Supported, heuristic only** | Identical across hash seeds. Live: not deterministic |
| 2-page document | README | **Contradicted** | 4 pages as rendered |
| Antigravity (Claude Opus 4.6 Thinking) & Claude | AGENTS, Doc | **Partly** | "Antigravity" appears in `PROGRESS.md`; the model name is unverified |

### AI-failure claims in AGENTS.md

| Claim | Status | Note |
|---|---|---|
| 1. LLM invented `00:45.00`; said 00:18–00:52 was 40s | **No artifact** | No log, prompt or output anywhere. Current model: 0 of 63 segments off-beat. The stated fix (beat matching in code) does not exist. |
| 2. LLMs opened on establishing shots of cathedral doors | **No artifact** | The stated fix (≤3.0s) is really 3.5s and doesn't test what the hook is. |
| 3. Auditor blind to mid-clip dialogue | **Real gap, doubtful attribution** | Git confirms the prompt lacked screenplay text. `CLAIMS_VERIFICATION.md` shows an outside reviewer caught it, and it's a design omission, not a model mistake. "Hallucinated" has no evidence. |

**Attribution:** I can't tell from the repo who originated the "Blood Boils" framing or the two-layer taxonomy; `IDEA.md` (deleted) has no author. AGENTS.md credits the AI for "two-layer taxonomy design", yet the taxonomy split was a reviewer-prompted fix per `CLAIMS_VERIFICATION.md` M3. Only you know what was yours; correct it either way.

**A strong true failure is available instead:** the keyword engine's Rank 1 story and 15/15 audit, where the LLM auditor rejected 13/15. Or the `66940d3` run, where the top 5 ranks all failed audit while ranking ignored it.

---

## 5. Reusability test

Test show: "Boardroom Ashes", a corporate revenge thriller I wrote as a fixture (4 episodes, 49 beats). **Caveat:** I wrote it in the existing format and it's small, so it tests themes, not format variance. Robustness cases are in M1.

```bash
# Step 1: hand-write config, no template or generator (~5 min)
#   show_title, premise, protagonist, antagonists, male_lead, show_cues_overlay
# Step 2:
python run.py --provider openai \
  --input-dir "newshow/Boardroom Ashes" --context newshow_ctx.yaml \
  --output-json out.json --output-md out.md
```

| Run | Time | Result |
|---|---|---|
| Heuristic | 0.18s | 3 promos, **no Ep 1 at all**, so "You're fired, Maya" was missed; champagne-over-head skipped in Ep 3. "You came to beg" won on the word `beg`. Audit 3/3 |
| Live `gpt-6-luna` | 32s | 5 promos. Found "You're fired" and "Get in the car, and I'll tell you what he did to your father". Audit 3 pass, 2 fail. Rank 1 is a composite, helped by M9's score floors |
| Forgot `--context` | n/a | No warning. Report says the show is "I Married a Broken Soldier", and live prompts would carry the Duke premise |
| Full-scale estimate | ~4 min | 227s measured on 50 episodes |

**Manual edits needed:**
- **Required:** the show YAML, and the `--context` flag.
- **Required to avoid overwriting submitted results:** `--output-json`, `--output-md`.
- **If format differs at all:** parser changes (`src/parser.py:24-29`), as it needs `**HEADER**` + `Start: | End:`. Different format gives 0 beats and exit 0.
- **Next.js, for the new show to appear:** path in `app/api/episodes/route.ts:10`, counts at `app/layout.tsx:134`, `app/page.tsx:194`, `app/episodes/page.tsx:38`; `/analyze` presets; copying the outputs over.
- **Heuristic quality only:** hard-coded words in `src/extractor.py:198-202,213-223,258-268,280-283`, period terms in `INANIMATE_OBJECT_TOKENS`.

**Taxonomy show-specificity:** LLM path is fine; the definitions travel well. Cues lean period: `my lord`, `your excellency`, `bow down`, `crest`, `heir`, `signet`, `carriage halts`. A new show needs little in the overlay for LLM use, but heuristics stay weak regardless.

**Missing API key:** no crash, which is good, but "graceful" is the wrong word: exit 0 and a header naming the wrong engine (M3).

**New hook type, config only: PASS.** Added `corporate_ouster` to a copy of the taxonomy; registered as 11 types and tagged promos with no code edits. Hard-coded fallback chains don't know about it; `new:*` tags from the LLM aren't fed back.

**Provider swap:** a fake provider subclass plugged into `PromoExtractor` and `PromoAuditor` with no pipeline edits. Reaching it from `--provider` needs a factory edit (no registry). Also, `name == "heuristic"` checks are scattered in `run.py`, `extractor.py`, `auditor.py`.

---

## 6. Recommended fix order (3–4 hours)

| # | Task | Fixes | Time |
|---|---|---|---|
| 1 | Add validation (beat match, quote match, score clamp), strict audit schema, flaw enum, engine metadata | M4, M5, B1 | 45m |
| 2 | Fail loudly: no empty overwrite, non-zero exit, no silent engine swap, retries, disk cache | M1, M3, M11 | 40m |
| 3 | Fix prompts: true previous logline, cast, definitions and camera to auditor. Fix `SCRIPT END`, Anthropic params, Gemini header | M2, M6, M7, M14, m1 | 25m |
| 4 | **Hand-pick 8–10 promos yourself before looking at new results**, commit them, compute recall | B3, §3 | 30m |
| 5 | Run live, commit as raw output with the full candidate pool and rejects | B1, B2 | 10m |
| 6 | Decide composites: LLM-justified, or removed and stated as a limit | M9 | 20m |
| 7 | Remove `/analyze` or relabel it; fix `\Z`; remove Streamlit and process files | B4, M12, M13, M15 | 25m |
| 8 | Rewrite the doc to 2 pages from measured numbers, with honest failures; export PDF; push repo | B3, B5, M10 | 45m |

Cut first if short of time: step 6 (remove composites), Next.js deployment, Next.js parser cleanup beyond `\Z`.

---

## 7. Things that are genuinely good

- **Timestamp integrity:** an independent parser matched all 3,727 beats, durations and boundaries held on 15/15 committed promos, and 0 of 63 live segments were off-beat.
- **The live auditor gives specific, checkable critiques**, like catching "the claimed destruction never happens" on Ep 5, which also contradicts your own doc. It's a strong basis for the quality section once it's the reported result.
- **The live pipeline ran cleanly:** 108/108 calls succeeded, no warnings, and all 50 episodes produced results, with Ep 6 and 8 correctly empty under both engines.
- **Taxonomy and provider boundaries are real:** a new hook type needs config only, a fake provider plugged in without pipeline edits, and the LLM handled a different genre well.
- **Reproducible offline path:** byte-identical across runs and hash seeds, 1.29s, and 14/14 tests on a clean install, with secrets kept out of git.
