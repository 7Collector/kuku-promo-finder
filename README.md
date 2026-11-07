# Kuku Promo Finder

Finds 20-60s promo clips (hook in the first 3s, cliffhanger ending, understandable cold) in timestamped microdrama screenplays, ranks them, and audits each one. Built for the Kuku AI Generalist assignment, Problem 1.

- Engine: Python (`run.py`). Viewer: Next.js (`app/`), read-only.
- Write-up: `SOLUTION_DOC.md` (PDF: `SOLUTION_DOC.pdf`). AI collaboration log: `AGENTS.md`.

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # add ONE key: OPENAI_API_KEY, GEMINI_API_KEY or ANTHROPIC_API_KEY

python run.py                       # first provider with a key (about 4 min for 50 episodes, 8 parallel calls)
python run.py --provider openai --model gpt-6-luna
python run.py --provider heuristic  # offline keyword smoke test (about 1s); labelled as such in every output
python -m unittest discover -s tests -t .
```

A provider you name explicitly must have its key; otherwise the run stops with an error. It never silently switches to the keyword engine. Responses are cached in `.cache/kuku/`, so re-running an unchanged prompt is free; use `--no-cache` to force fresh calls.

### Outputs (`outputs/`)

| File | Contents |
|---|---|
| `promos.json` | Top 15, with segments, hook, cliffhanger, scores, audit result, `engine`, `model` |
| `PROMOS.md` | Readable report; states engine, model, audit method and counts in its header |
| `promos.pool.json` | All candidates after validation and de-duplication, with audits |
| `promos.rejected.json` | Model-reported near misses and proposals dropped by validation |
| `promos.meta.json` | Provider/model, counts, failures, token usage, wall time, git commit |
| `smoke_test_heuristic/` | Keyword-engine output, kept for comparison only |

Exit codes: 0 ok; 1 completed but incomplete (failed episodes or unaudited candidates, see meta); 2 bad input or configuration; 3 nothing to write. Existing outputs are never overwritten by an empty or failed run.

## What is enforced in code
`src/validation.py` and `src/ranker.py`: total 20-60s; hook beat starts within 3s of the opening cut; every cut is on a real beat edge (LLM times within 0.5s are snapped, others dropped); hook and cliffhanger quotes exist verbatim in the screenplay; the cliffhanger ends the clip (last 6s); scores clamped to 0-10. Audit-passing promos rank above failing ones, with a count-based penalty for repeated hook types and episodes.

## Another show
```bash
cp config/shows/_template.yaml config/shows/my_show.yaml    # edit title, premise, characters
python run.py --show my_show --input-dir path/to/screenplays
```
Screenplays must use the same layout: `**SPEAKER (emotion):**` then `Start: (mm:ss.ss) | End: (mm:ss.ss)` then the text. Anything else parses to zero beats and the run stops with an error. A custom `--input-dir` without `--show`/`--context` is refused, and outputs go to `outputs/<show>/`. Hook types are config; add one in `config/taxonomy.yaml` with no code change.

Other options: `--audit-model` / `--audit-provider` (independent judge; by default the extractor model grades its own picks), `--composites` (experimental cross-episode splices, off by default), `--top-k`, `--workers`.

## Evaluation
No hand-picked ground truth exists yet, so recall is unmeasured. To measure it: write your picks to `eval/ground_truth.json` (format in `eval/recall.py`) before looking at the output, then `python eval/recall.py`.

## Web viewer
```bash
npm install && npm run dev      # http://localhost:3000
```
Pages: ranked promos (with audit verdict and flaw type) and a screenplay beat browser. It reads `outputs/` and `assets/` from disk (override with `KUKU_OUTPUT_DIR`, `KUKU_ASSETS_DIR`, `KUKU_SHOW`); it has no approve/reject controls and has not been deployed.

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
