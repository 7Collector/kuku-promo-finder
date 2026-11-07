# Agents & AI Collaboration Log

## Tools used
- **Antigravity** (earlier sessions) and **Claude Code** (audit and fix session, 2026-11-07): coding assistants for the parser, taxonomy, pipeline, UI and tests.
- **gpt-6-luna**: the runtime model for extraction and audit (`outputs/promos.meta.json`).

Authorship note: which design ideas (e.g. the "Blood Boils" framing, the two-layer taxonomy) came from the author versus an assistant cannot be reconstructed from the repository, so none are attributed here.

## Where AI got it wrong (each item has an artifact in git history or `outputs/`)

1. **A self-audit that could not fail.** The keyword engine's audit fail-conditions required scores the engine never produced, so it passed 87/87 candidates while the LLM auditor failed 13 of the same 15 shipped promos. Found by re-running the project's own `PromoAuditor` on the committed `outputs/promos.json` at commit `809d946`. Fix: audits are labelled by method (`llm` / `rules` / `error`), rule lint is not described as quality, and a failed audit call is marked unaudited instead of passing.
2. **Invented demo content in the UI.** The old `/analyze` page presets quoted lines ("Who dares enter", "royal sanctuary") that exist in none of the 50 screenplays, and its "auditor" was a regex that scored "Hello there" 8.79. Fix: the page and API were removed.
3. **Unsupported numbers in the write-up.** An earlier `SOLUTION_DOC.md` reported "100% Top-10 recall" and "84% passed" with no ground-truth file or run behind them, and a cost of "under 5 cents" for a run that measured 546,585 tokens. Fix: the document now cites only `outputs/promos.meta.json`; recall is reported as unmeasured.
4. **Auditor blind to the clip (earlier history).** Early audit prompts contained only the extractor's quotes and its own explanation, so it graded the extractor's pitch. Fix: the clip screenplay is injected (`src/auditor.py`), now with camera beats and tag definitions.
5. **Model output trusted.** Quotes and cuts from the model were accepted unchecked (`tests/test_validation.py` reproduces an invented quote, an off-beat cut and a cliffhanger far from the end; in the first live run, ranks 8 and 11 had a cliffhanger quote 19.5s and 23s before the clip ended, caught by an independent re-check script and fixed by the 6s cliffhanger window). Fix: `src/validation.py`.

Earlier versions of this file described three other failures (invented round timestamps, establishing-shot hooks) without any log or output behind them; they were removed rather than kept unsupported.
