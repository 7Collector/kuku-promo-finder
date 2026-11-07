# Solution Document: AI Promo Finder for Microdrama Screenplays

**Author:** AI Generalist Candidate  
**Target Problem:** Problem 1 — Find the Promos  
**Show Analyzed:** *I Married a Broken Soldier. He was a Duke* (50 Episodes, 3,727 Beats)  
**Deliverables:** GitHub Prototype & Streamlit Dashboard, Raw JSON (`outputs/promos.json`), Ranked Report (`outputs/PROMOS.md`)

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

We designed a hybrid 4-stage pipeline that strictly delineates deterministic rules from semantic judgment:

```
[Screenplays (.txt)]
        │
        ▼
[Stage 1: Deterministic Screenplay Parser]
   • Parses 3,727 beats across 50 episodes with millisecond timestamps
        │
        ▼
[Stage 2: Candidate Window Discovery & Taxonomy Tagging]
   • Tags 20–60s clips opening on hooks ≤ 3s against "Blood Boils" taxonomy
   • Builds Single-Episode cuts + Cross-Episode Composites (Setup + Climax)
        │
        ▼
[Stage 3: Physical Validation, Deduplication & MMR Diversity]
   • Code checks 20–60s duration and authentic timestamp existence
   • Maximal Marginal Relevance (MMR) prevents 10 identical slap scenes
        │
        ▼
[Stage 4: Adversarial Quality Auditor]
   • Flags resolution leaks, context deficits, and visual dependencies
```

### What We Gave to Code vs. What We Kept for AI
- **Kept as Code / Rules:**
  - Absolute timestamp verification (every cut point must exist in the screenplay).
  - Physical timing constraints (strictly 20–60s total, hook inside $\le 3.0$ seconds).
  - Overlap deduplication ($>40\%$ temporal overlap in the same episode pruned).
  - MMR Diversity Reranking (penalizes repeated hook types to ensure a balanced marketing portfolio).
- **Gave to AI:**
  - Semantic taxonomy classification (tagging subtle emotional dynamics).
  - Standalone cold-viewer clarity evaluation.
  - "Withheld payoff" assessment (determining whether conflict remains unresolved).
  - Adversarial critique and generation of "why it works" marketing copy.

### Scale & Unit Economics at Volume
- **Compute footprint:** Microdrama scripts are concise (~1,500 words per episode; 50 episodes $\approx$ 75,000 words total).
- **Zero Vector DB overhead:** The entire show fits in memory; spinning up a vector database adds latency and brittle dependencies without improving dramatic timing.
- **Cost per Show:** Candidate extraction + composite stitching + critique requires $\approx 52$ API calls per show. At Gemini 2.5 Flash rates (~$0.075 / 1M tokens), running an entire 50-episode show costs **$0.02 to $0.05 (under 5 cents)**.

---

## 3. Results & Top Promo Discoveries

Running our pipeline on the full 50 episodes parsed 3,727 dramatic beats and discovered 87 physically valid promo windows, yielding a final top 15 ranked portfolio:

1. **Rank 1: Cross-Episode Composite (`Ep 12 + Ep 42`, 47.0s, Score: 8.98/10)**
   - *Hook (`00:20.00`):* *"Crawl through the thorns, Juliana, or watch him hang."* (Sadistic family cruelty).
   - *Cliffhanger (`00:45.00`):* *"The shattered cathedral doors fall inward as Alexander steps into the light."*
   - *Why It Works:* Maximum emotional contrast. Cold scrollers see Juliana tortured in blackthorns, followed immediately by the cathedral gates blowing open as the Duke arrives in full regalia.
2. **Rank 2: Cross-Episode Composite (`Ep 1 + Ep 16`, 43.2s, Score: 8.53/10)**
   - *Hook (`00:33.80`):* *"Why are you holding her hand?"* (Fiancé abandoning Juliana at the altar).
   - *Cliffhanger (`00:48.00`):* Alexander steps between the hired assassins' blades and Juliana.
3. **Rank 3: Single-Episode (`Ep 30`, 20.4s, Score: 7.92/10)**
   - *Hook (`00:08.80`):* *"You have a rat in your cellar, Rupert. And the servants are beginning to smell it."*
   - *Cliffhanger (`00:29.20`):* *"She knows the Duchess was poisoned."*

---

## 4. Quality Checking, Failure Modes & Where AI Got It Wrong

To avoid overpromising, we built an **Adversarial Quality Auditor** testing 5 explicit failure modes:

| Failure Mode | How It Occurs | Mitigation in Pipeline |
|---|---|---|
| **Resolution Leak** | Clip accidentally includes the protagonist's snappy comeback or vindication, satisfying curiosity prematurely. | Scored on `payoff_withheld`; penalized in Stage 4 auditor. |
| **Context Deficit** | Dialogue relies on proper nouns ("House Sterling", "Father Thomas") that baffle cold viewers. | Standalone clarity score; auditor flags external lore dependencies. |
| **Visual Dependency** | Screenplay relies on subtle acting/cinematography (e.g. camera slow pan) that won't translate to mobile feeds. | Auditor flags visual-action dependencies; code enforces hook $\le 3$s. |
| **Timestamp Hallucination** | LLMs invent round numbers (e.g. `00:45.00`) and fail sub-second interval math. | Timestamp matching and duration arithmetic are 100% deterministic in Python. |
| **Taxonomy Monoculture** | Top 10 dominated by 10 identical sister-slap scenes. | MMR Diversity Reranker penalizes consecutive identical hook archetypes. |

---

## 5. Prototype & Interview Re-runnability

The solution is completely modular and config-driven:
- **CLI Runner:** `python run.py --input-dir "assets/new_show"` executes in $<2$ seconds.
- **Interactive UI:** `streamlit run app.py` provides a live editor review dashboard with hook filters, quote previews, and quality audits.
- **Swappable LLMs:** Native support for Gemini, OpenAI, Anthropic, or an offline deterministic heuristic engine when running without API keys.
