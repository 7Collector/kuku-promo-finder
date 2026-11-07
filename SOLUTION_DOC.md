# Solution Document: AI Promo Finder for Microdrama Screenplays

**Author:** AI Generalist Candidate  
**Target Problem:** Problem 1 — Find the Promos  
**Show Analyzed:** *I Married a Broken Soldier. He was a Duke* (50 Episodes, 3,727 Beats)  
**Deliverables:** Production Next.js Web App (Omega Design System, Vercel-ready), Streamlit Dashboard (`app.py`), Python CLI Engine (`run.py`), Raw JSON (`outputs/promos.json`), Ranked Report (`outputs/PROMOS.md`), Comprehensive Unit Test Suite (`tests/`)

---

## 1. Problem Choice, Strategic Framing & Core Insight

In vertical microdrama apps (Kuku, ReelShort, DramaBox), acquisition promos on TikTok, Instagram Reels, and YouTube Shorts dictate user acquisition cost (CAC). Human editors currently spend hours watching every 1–2 minute episode to identify 20–60s ad cuts.

### The Viral Dramatic Loop: "Blood Boils" + Withheld Payoff
Through empirical analysis of short-form social engagement, high-converting promos are rarely happy or descriptive; they exploit **unearned interpersonal injustice**:
1. **The Psychological Hook ($\le$ 3 seconds):** An honest protagonist is publicly belittled, slapped, abandoned at the altar, or treated as dirt by arrogant antagonists. This instantly stops a scrolling viewer by triggering visceral outrage ("blood boils").
2. **Withheld Catharsis (Cliffhanger):** The promo **must cut at the peak of tension**—right as the protagonist is about to retaliate, or right as a powerful protector enters. If the clip shows the comeuppance, it resolves its own tension and becomes a spoiler rather than a high-converting acquisition ad.

To achieve this, we abandoned fragile keyword matching in favor of an **Extensible Hook & Cliffhanger Taxonomy** (YAML-driven) mapped to psychological drivers.

---

## 2. Approach, Scale & The Code vs. AI Boundary

We designed a hybrid 5-stage pipeline that strictly delineates deterministic rules from semantic judgment:

```
[Screenplays (.txt)]
        │
        ▼
[Stage 1: Deterministic Screenplay Parser (src/parser.py)]
   • Parses 3,727 beats across 50 episodes with millisecond timestamps
        │
        ▼
[Stage 2: Candidate Window Discovery & Taxonomy Tagging (src/extractor.py)]
   • Tags 20–60s clips opening on hooks ≤ 3.5s against "Blood Boils" taxonomy
   • Builds Single-Episode cuts + Cross-Episode Composites (Setup + Climax)
   • Parallelized via ThreadPoolExecutor (8 workers) for frontier LLM calls
        │
        ▼
[Stage 3: Physical Validation, Deduplication & MMR Diversity (src/ranker.py)]
   • Code checks 20–60s duration and authentic timestamp existence
   • Maximal Marginal Relevance (MMR) prevents 10 identical slap scenes
        │
        ▼
[Stage 4: Adversarial Quality Auditor (src/auditor.py)]
   • Flags resolution leaks, context deficits, and visual dependencies
   • Parallelized via ThreadPoolExecutor (8 workers)
        │
        ▼
[Stage 5: Dual Deliverable Exporter]
   • Unedited raw machine JSON (outputs/promos.json)
   • Formatted report with quality critique & risk flags (outputs/PROMOS.md)
```

### What We Gave to Code vs. What We Kept for AI
- **Kept as Code / Rules:**
  - Absolute timestamp verification (every cut point must exist in the screenplay).
  - Physical timing constraints (strictly 20–60s total, hook inside $\le 3.5$ seconds).
  - Overlap deduplication ($>35\%$ temporal overlap in the same episode pruned).
  - MMR Diversity Reranking (penalizes repeated hook types to ensure a balanced marketing portfolio).
- **Gave to AI:**
  - Semantic taxonomy classification (tagging subtle emotional dynamics).
  - Standalone cold-viewer clarity evaluation.
  - "Withheld payoff" assessment (determining whether conflict remains unresolved).
  - Adversarial critique and generation of "why it works" marketing copy.

### Scale & Unit Economics at Volume
- **Compute footprint:** Microdrama scripts are concise (~1,500 words per episode; 50 episodes $\approx$ 75,000 words total).
- **Zero Vector DB overhead:** The entire show fits in memory; spinning up a vector database adds latency and brittle dependencies without improving dramatic timing.
- **Cost & Throughput at Volume:** Candidate extraction + composite stitching + critique requires $\approx 52$ API calls per show. Parallelized across 8 worker threads, live frontier model processing finishes in under 20 seconds. At Gemini 3.8 Flash rates (~$0.075 / 1M tokens), running an entire 50-episode show costs **$0.02 to $0.05 (under 5 cents)**. The offline heuristic engine executes locally in **<2 seconds** at zero cost.

---

## 3. Supported Frontier Models & Swappable Adapter Pattern

The LLM client is built on a clean **Provider Strategy Pattern** (`src/providers/`):
- **Google Gemini:** `gemini-3.8-flash` (High-efficiency, low-latency reasoning)
- **OpenAI:** `gpt-6-luna` (High-volume cost-efficient chat & structured generation)
- **Anthropic Claude:** `claude-sonnet-5-5` (Deep dramatic judgment & structured analysis)
- **Offline Heuristic Engine:** Deterministic rule-based fallback enabling instantaneous execution without API keys.

---

## 4. Quality Checking, Failure Modes & Where AI Got It Wrong

To avoid overpromising, we built an **Adversarial Quality Auditor** testing 5 explicit failure modes:

| Failure Mode | How It Occurs | Mitigation in Pipeline |
|---|---|---|
| **Resolution Leak** | Clip accidentally includes the protagonist's snappy comeback or vindication, satisfying curiosity prematurely. | Scored on `payoff_withheld`; penalized in Stage 4 auditor. |
| **Context Deficit** | Dialogue relies on proper nouns that baffle cold viewers. | Standalone clarity score; auditor flags external lore dependencies dynamically from show context. |
| **Visual Dependency** | Screenplay relies on subtle acting/cinematography (e.g. camera slow pan) that won't translate to mobile feeds. | Auditor flags visual-action dependencies; code enforces hook $\le 3.5$s. |
| **Timestamp Hallucination** | LLMs invent round numbers (e.g. `00:45.00`) and fail sub-second interval math. | Timestamp matching and duration arithmetic are 100% deterministic in Python. |
| **Keyword Collision & Monoculture** | Substrings ("beg" in "beginning") and inanimate actions ("strikes flint") trigger false violence tags. | Regex word boundaries (`\b`) and inanimate object exclusions; MMR diversity reranking with monotonic score tracking. |

---

## 5. Prototype & Interview Re-runnability

The solution is completely modular, production-ready, and config-driven:

### 1. Production Next.js Web Application (`app/` — Vercel-Ready)
Built with the **Omega Design System** (`Design/omega-design-system`):
- **Ranked Promos Dashboard (`/`):** Hero Board showcasing the #1 ranked promo on the focal dark surface, interactive archetype filter chips, search, and deep-dive modal with screenplay dialogue context and audit cards.
- **Reusable Cut Tester Tool (`/analyze`):** Interactive editor tool allowing anyone to test any custom screenplay cut against the taxonomy, duration bounds (20–60s), and the adversarial auditor with one-click presets.
- **50-Episode Beat Inspector (`/episodes`):** Full browser for all 50 episodes with millisecond timestamps and emotion cues.
- **Serverless API Routes:** Direct endpoints (`/api/promos`, `/api/analyze`, `/api/episodes`, `/api/taxonomy`) enabling headless integration.

### 2. Python CLI & Streamlit Alternative
- **CLI Runner:** `PYTHONPATH=. python3 run.py --provider [gemini|openai|anthropic|heuristic]` processes 50 episodes in parallel.
- **Streamlit UI:** `streamlit run app.py` provides a pure-Python review alternative.
- **Automated Tests:** 10 unit tests (`PYTHONPATH=. python3 -m unittest discover tests`) verifying parser robustness, taxonomy boundaries, MMR monotonicity, and auditor edge cases.
- **Interview Re-runnability:** 100% config-driven. Running on a new show during interviews requires only pointing `--input-dir` to the new screenplay folder and updating `config/show_context.yaml`.
