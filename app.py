import streamlit as st
import plotly.express as px
import pandas as pd
import time

from agents.jd_parser import parse_job_description
from agents.candidate_discovery import discover_candidates
from agents.matching_engine import compute_match_score
from agents.outreach_agent import simulate_outreach_conversation
from agents.scorer import build_ranked_shortlist

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.2rem; }
    .sub-header  { font-size: 1rem; color: #666; margin-bottom: 2rem; }
    .stProgress > div > div { background-color: #6c63ff; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    top_n = st.slider("Candidates to shortlist", 3, 7, 5)
    run_outreach = st.toggle("Simulate outreach conversations", value=True)
    st.markdown("---")
    st.markdown("**Scoring Weights**")
    st.caption("Match: 60% | Interest: 40%")
    st.markdown("---")
    st.markdown("**Sample JDs**")
    if st.button("Load: Python Backend Engineer"):
        st.session_state["sample_jd"] = """We are looking for a Senior Backend Engineer with 4+ years 
of experience in Python, FastAPI, and PostgreSQL. You will build scalable microservices on AWS, 
write clean APIs, and mentor junior engineers. Experience with Docker and Kubernetes is a plus. 
We are a Series B fintech startup based in Bengaluru."""
    if st.button("Load: ML Engineer"):
        st.session_state["sample_jd"] = """Hiring an ML Engineer (3+ years) with hands-on PyTorch 
and HuggingFace experience to build and deploy NLP models in production. Strong Python skills required. 
MLflow for experiment tracking. FastAPI for model serving. Prior experience with LLMs is a big plus."""

# ── Main UI ───────────────────────────────────────────────
st.markdown('<div class="main-header">🎯 TalentScout AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Paste a job description → get a ranked, engagement-scored shortlist in minutes.</div>', unsafe_allow_html=True)

jd_placeholder = "Paste your job description here..."
default_val = st.session_state.get("sample_jd", "")
jd_text = st.text_area("Job Description", value=default_val, height=200, placeholder=jd_placeholder)

col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    run_button = st.button("🚀 Run Agent", type="primary", use_container_width=True)
with col2:
    if st.button("🔄 Clear", use_container_width=True):
        st.session_state.clear()
        st.rerun()

if run_button and jd_text and jd_text.strip() != "":

    # ── Step 1: Parse JD ──────────────────────────────────
    with st.status("🔍 Parsing job description with Claude...", expanded=True) as status:
        st.write("Extracting skills, experience requirements, seniority...")
        parsed_jd = parse_job_description(jd_text)
        st.write("✅ JD parsed successfully")
        status.update(label="JD parsed ✅", state="complete")

    with st.expander("📋 View Parsed JD Structure"):
        st.json(parsed_jd)

    # ── Step 2: Discover candidates ────────────────────────
    with st.status("👥 Discovering matching candidates...", expanded=True) as status:
        candidates = discover_candidates(parsed_jd)
        candidates = candidates[:top_n]
        st.write(f"✅ Found {len(candidates)} candidate profiles")
        status.update(label=f"Found {len(candidates)} candidates ✅", state="complete")

    # ── Step 3: Match scoring ─────────────────────────────
    with st.status("📊 Computing match scores...", expanded=True) as status:
        scored_candidates = []
        for c in candidates:
            result = compute_match_score(parsed_jd, c)
            c["match_score"] = result["match_score"]
            c["matched_skills"] = result["breakdown"]["matched_skills"]
            scored_candidates.append(c)
        st.write("✅ Semantic matching complete")
        status.update(label="Match scores ready ✅", state="complete")

    # ── Step 4: Outreach simulation ────────────────────────
    if run_outreach:
        with st.status("💬 Simulating outreach conversations...", expanded=True) as status:
            conversations = {}
            for c in scored_candidates:
                st.write(f"Engaging {c['name']}...")
                outreach = simulate_outreach_conversation(c, parsed_jd)
                c["interest_score"] = outreach["interest_score"]
                c["interest_level"] = outreach["interest_level"]
                conversations[c["id"]] = outreach["conversation"]
                time.sleep(0.3)
            status.update(label="Outreach simulated ✅", state="complete")
        st.session_state["conversations"] = conversations
    else:
        availability_map = {
            "actively_looking": 75,
            "open_to_opportunities": 50,
            "not_looking": 25
        }
        for c in scored_candidates:
            c["interest_score"] = availability_map.get(c.get("availability", "unknown"), 40)
            c["interest_level"] = "high" if c["interest_score"] >= 70 else "medium" if c["interest_score"] >= 40 else "low"

    # ── Step 5: Final ranking ─────────────────────────────
    df = build_ranked_shortlist(scored_candidates)
    st.session_state["df"] = df
    st.session_state["scored_candidates"] = scored_candidates
    st.session_state["parsed_jd"] = parsed_jd

# ── Results Display ────────────────────────────────────────
if "df" in st.session_state:
    df = st.session_state["df"]
    parsed_jd = st.session_state["parsed_jd"]

    st.markdown("---")
    st.markdown("## 📋 Ranked Shortlist")

    # Summary metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Candidates Ranked", len(df))
    m2.metric("Top Match Score", f"{df['Match Score'].max()}/100")
    m3.metric("Top Interest Score", f"{df['Interest Score'].max()}/100")
    m4.metric("Role", parsed_jd.get("title", "—"))

    # Color scoring function
    def color_score(val):
        if val >= 70:
            return 'color: #2ecc71; font-weight: bold'
        elif val >= 45:
            return 'color: #f39c12; font-weight: bold'
        return 'color: #e74c3c'

    st.dataframe(
        df.style.map(color_score, subset=["Match Score", "Interest Score", "Combined Score"]),
    )

    # Export button
    csv = df.to_csv()
    st.download_button("⬇️ Export to CSV", csv, "shortlist.csv", "text/csv")

    # ── Scatter plot ──────────────────────────────────────
    st.markdown("### 📈 Match vs Interest Matrix")
    fig = px.scatter(
        df.reset_index(),
        x="Match Score",
        y="Interest Score",
        text="Name",
        size="Combined Score",
        color="Interest Level",
        color_discrete_map={"high": "#2ecc71", "medium": "#f39c12", "low": "#e74c3c"},
        hover_data=["Title", "Combined Score", "Matched Skills"],
        title="Candidate Positioning: Match Score vs Interest Score"
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

    # ── Conversation transcripts ──────────────────────────
    if "conversations" in st.session_state:
        st.markdown("### 💬 Outreach Conversation Transcripts")
        conversations = st.session_state["conversations"]
        scored = st.session_state["scored_candidates"]

        for c in scored:
            conv = conversations.get(c["id"])
            if not conv:
                continue
            interest = c["interest_score"]
            level = c["interest_level"].upper()
            with st.expander(f"**{c['name']}** — {c['title']} | Interest: {interest}/100 ({level})"):
                for turn in conv:
                    role = turn["role"]
                    msg = turn["message"]
                    if role == "Recruiter":
                        st.markdown(f"**🧑‍💼 Recruiter:** {msg}")
                    else:
                        st.markdown(f"**👤 {role}:** {msg}")
                    st.markdown("---")