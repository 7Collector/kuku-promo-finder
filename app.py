"""
Streamlit Web Application for Kuku Promo Finder.
Interactive promo previewer, taxonomy filter, and screenplay inspector.
"""

import os
import json
import yaml
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Kuku Promo Finder",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROMOS_JSON_PATH = "outputs/promos.json"
TAXONOMY_PATH = "config/taxonomy.yaml"
CONTEXT_PATH = "config/show_context.yaml"


@st.cache_data
def load_data():
    promos = []
    if os.path.exists(PROMOS_JSON_PATH):
        with open(PROMOS_JSON_PATH, "r", encoding="utf-8") as f:
            promos = json.load(f)

    taxonomy = {}
    if os.path.exists(TAXONOMY_PATH):
        with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
            taxonomy = yaml.safe_load(f) or {}

    context = {}
    if os.path.exists(CONTEXT_PATH):
        with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
            context = yaml.safe_load(f) or {}

    return promos, taxonomy, context


promos, taxonomy, context = load_data()

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.title("🎬 Kuku Promo Finder")
    st.markdown("**AI Microdrama Promo Optimization**")
    st.divider()

    st.subheader("Show Profile")
    st.markdown(f"**Title:** {context.get('show_title', 'Unknown')}")
    st.markdown(f"**Platform:** {context.get('target_platform', 'Reels / TikTok')}")
    st.caption(f"{context.get('premise', '')[:160]}...")
    st.divider()

    st.subheader("Filters")
    promo_types = ["All", "Single Episode", "Cross Episode"]
    sel_type = st.selectbox("Promo Type", promo_types)

    hook_options = ["All"] + [h["id"] for h in taxonomy.get("hooks", [])]
    sel_hook = st.selectbox("Hook Archetype", hook_options)

    min_score = st.slider("Minimum Effective Score", 0.0, 10.0, 0.0, 0.5)

    st.divider()
    st.info("💡 **Core Principle:** Injustice without immediate payoff triggers rage-bait scroll-stopping attention.")

# ----------------- MAIN CONTENT -----------------
st.title("Top Ranked Microdrama Promos")
st.markdown("Automated scroll-stopping promo discovery tailored for Instagram Reels, TikTok, and YouTube Shorts.")

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Promos Ranked", len(promos))
with col2:
    st.metric("Top Score", f"{promos[0]['scores']['adjusted_score']} / 10" if promos else "N/A")
with col3:
    st.metric("Hook Taxonomy Types", len(taxonomy.get("hooks", [])))
with col4:
    st.metric("Screenplays Analyzed", "50 Episodes (3,727 beats)")

st.divider()

# Filter logic
filtered_promos = []
for p in promos:
    if sel_type == "Single Episode" and p.get("promo_type") != "single_episode":
        continue
    if sel_type == "Cross Episode" and p.get("promo_type") != "cross_episode":
        continue
    if sel_hook != "All" and p.get("hook", {}).get("type") != sel_hook:
        continue
    cand_score = p.get("scores", {}).get("adjusted_score") or p.get("scores", {}).get("composite_score", 0)
    if cand_score < min_score:
        continue
    filtered_promos.append(p)

# Promo Cards Display
tab_cards, tab_table, tab_taxonomy = st.tabs(["🔥 Promo Cards", "📊 Data Table", "📋 Hook & Cliffhanger Taxonomy"])

with tab_cards:
    if not filtered_promos:
        st.warning("No promos match the selected filter criteria.")
    else:
        for p in filtered_promos:
            rank = p.get("rank", 0)
            score = p.get("scores", {}).get("adjusted_score") or p.get("scores", {}).get("composite_score", 0)
            raw_score = p.get("scores", {}).get("composite_score", score)
            penalty = p.get("scores", {}).get("diversity_penalty", 1.0)
            eps_str = ", ".join(f"Ep {e}" for e in p.get("episodes", []))
            dur = p.get("total_duration", 0)
            p_type = p.get("promo_type", "").replace("_", " ").title()

            with st.container(border=True):
                head_col1, head_col2 = st.columns([4, 1])
                with head_col1:
                    st.markdown(f"### Rank {rank}: {p['hook']['name']} `({p_type})`")
                    st.caption(f"**Target:** {eps_str} | **Duration:** {dur:.1f}s | **Hook:** `{p['hook']['type']}`")
                with head_col2:
                    st.metric("Effective Score", f"{score:.2f}", delta=f"Raw: {raw_score:.2f}" if penalty < 1.0 else None)

                # Segments
                segs_text = " | ".join(f"`{s['start']} → {s['end']}` ({s['duration']:.1f}s)" for s in p.get("segments", []))
                st.markdown(f"**Timestamps:** {segs_text}")

                c_hook, c_cliff = st.columns(2)
                with c_hook:
                    st.markdown("**🎯 The Hook (First 3 Seconds):**")
                    st.info(f"*{p['hook']['quote']}*\n\n**Driver:** {p['hook'].get('psychological_trigger', '')}")
                with c_cliff:
                    st.markdown("**🛑 The Cliffhanger (Payoff Withheld):**")
                    st.warning(f"*{p['cliffhanger']['quote']}*\n\n**Withheld Payoff:** {p['cliffhanger'].get('withheld_payoff', '')}")

                st.markdown(f"**💡 Why It Works for Cold Viewers:** {p.get('why_it_works', '')}")

                # Quality Audit Section
                audit = p.get("quality_audit")
                if audit:
                    st.markdown("**🛡️ Adversarial Quality Audit:**")
                    audit_col1, audit_col2 = st.columns([3, 1])
                    with audit_col1:
                        st.caption(f"**Critique:** {audit.get('critique', '')}")
                    with audit_col2:
                        risks = audit.get("risks", [])
                        if risks:
                            st.caption(f"⚠️ **Risks:** {', '.join(risks)}")
                        else:
                            st.caption("✅ No critical failure flags")

with tab_table:
    if filtered_promos:
        table_rows = []
        for p in filtered_promos:
            table_rows.append({
                "Rank": p.get("rank"),
                "Score": p.get("scores", {}).get("composite_score"),
                "Type": p.get("promo_type"),
                "Episodes": ", ".join(str(e) for e in p.get("episodes", [])),
                "Duration (s)": round(p.get("total_duration", 0), 1),
                "Hook Type": p.get("hook", {}).get("type"),
                "Hook Quote": p.get("hook", {}).get("quote", "")[:50] + "...",
                "Cliffhanger Quote": p.get("cliffhanger", {}).get("quote", "")[:50] + "...",
                "Payoff Withheld": p.get("scores", {}).get("payoff_withheld"),
            })
        df = pd.DataFrame(table_rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

with tab_taxonomy:
    st.subheader("Configurable Hook Taxonomy (The 'Blood Boils' Family)")
    st.markdown("The pipeline maps moments to psychological triggers rather than fragile keywords:")
    for h in taxonomy.get("hooks", []):
        with st.expander(f"{h['name']} (Weight: {h['weight']})"):
            st.markdown(f"- **ID:** `{h['id']}`")
            st.markdown(f"- **Category:** {h.get('category', 'injustice')}")
            st.markdown(f"- **Psychological Driver:** {h['psychological_driver']}")
            st.markdown(f"- **Cues:** {', '.join(h.get('example_cues', []))}")

    st.subheader("Configurable Cliffhanger Taxonomy (Withheld Payoffs)")
    for c in taxonomy.get("cliffhangers", []):
        with st.expander(f"{c['name']} (Weight: {c['weight']})"):
            st.markdown(f"- **ID:** `{c['id']}`")
            st.markdown(f"- **Category:** {c.get('category', 'payoff_withheld')}")
            st.markdown(f"- **Psychological Driver:** {c['psychological_driver']}")
            st.markdown(f"- **Cues:** {', '.join(c.get('example_cues', []))}")
