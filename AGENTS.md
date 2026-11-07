# Agents

## Tools Used

- **Antigravity (Claude Opus 4.6 Thinking)** — Primary AI coding assistant for ideation, architecture design, deterministic parsing, pipeline implementation, and UI.
- **Claude** — Used for brainstorming, approach discussion, and iterating on ideas and prompt structures.

## Where AI Got It Wrong

1. **Timestamp Hallucination & Math Drift**:
   When prompt-tested on raw screenplay text, zero-shot LLMs frequently hallucinated clean, rounded timestamps (e.g. guessing `00:45.00` or `01:00.00`) that did not exist in the screenplay, and routinely miscalculated time intervals (claiming `00:18.00` to `00:52.00` was 40 seconds). 
   *How we fixed it:* Kept timestamp arithmetic and boundary matching 100% deterministic in Python code (`src/parser.py` and `src/ranker.py`), requiring every cut point to match an authentic beat start/end.

2. **Conflating Ambient Cinematography with Viral Hooks**:
   Without explicit negative constraints, LLMs repeatedly proposed opening promos on atmospheric shots (e.g., `00:00.00` camera pans across the cathedral doors). On vertical short-form platforms (TikTok/Reels), 3 seconds of a camera panning an empty doorway leads to an instant swipe.
   *How we fixed it:* Enforced a hard code rule that the hook must trigger within $\le 3.0$ seconds of the opening cut, backed by our "Blood Boils" hook taxonomy targeting interpersonal injustice and immediate dialogue confrontation.

3. **Over-Engineering Vector Databases (RAG) for Small Corpus**:
   Initial architectural ideation proposed building an embedding vector store (Chroma/FAISS) to retrieve promo moments. However, across all 50 microdrama episodes, the total dramatic text is only ~75,000 words. Spinning up a vector database added latency, dependencies, and infrastructure overhead without improving the model's ability to judge dramatic timing or withheld cliffhangers.
   *How we fixed it:* Used in-memory parsed objects with deterministic window extraction and fast LLM semantic scoring, keeping the pipeline self-contained and instant to run on new show inputs during interviews.
