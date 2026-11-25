"""Streamlit Web Dashboard for SkillBridge.

Interactive Skill-Gap Graph, Career Path Recommender, and Career Advising Suite.
Professional engineering UI with Plotly analytics and interactive PyVis network.
Contains ONLY presentation logic; all business logic is delegated to `src.pipeline`.
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import streamlit as st
import streamlit.components.v1 as components

from src.config import TARGET_ROLES, WEIGHT_CONNECTIVITY, WEIGHT_DEMAND, WEIGHT_EASE
from src.pipeline import SkillBridgePipeline

# ==========================================
# Page Configuration
# ==========================================
st.set_page_config(
    page_title="SkillBridge • Graph-Theoretic Career Recommender",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional Developer-Grade Dark Theme Styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1360px;
    }

    /* Hero Banner Header */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 60%, #172554 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.8rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #F8FAFC;
        margin: 0 0 0.35rem 0;
    }
    .hero-subtitle {
        font-size: 0.98rem;
        color: #94A3B8;
        font-weight: 400;
        max-width: 860px;
        line-height: 1.55;
        margin: 0;
    }

    /* Modern Metric Cards */
    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem 1rem;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        transition: transform 0.15s ease, border-color 0.15s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #475569;
    }
    .metric-card-title {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94A3B8;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .metric-card-val {
        font-size: 2rem;
        font-weight: 800;
        color: #F8FAFC;
        line-height: 1.1;
        margin: 0.15rem 0;
    }
    .metric-card-sub {
        font-size: 0.78rem;
        color: #64748B;
        font-weight: 500;
    }

    /* Recommendation Highlight Banner */
    .rec-highlight-card {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.14) 0%, rgba(180, 83, 9, 0.08) 100%);
        border: 1px solid rgba(245, 158, 11, 0.45);
        border-left: 5px solid #F59E0B;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    /* Skill Badge Chips */
    .skill-chip {
        display: inline-flex;
        align-items: center;
        padding: 0.32rem 0.7rem;
        border-radius: 9999px;
        font-size: 0.84rem;
        font-weight: 600;
        margin: 0.2rem 0.2rem;
        transition: all 0.15s ease;
    }
    .skill-chip-acquired {
        background: rgba(16, 185, 129, 0.18);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .skill-chip-missing {
        background: rgba(239, 68, 68, 0.18);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .skill-chip-rec {
        background: rgba(245, 158, 11, 0.22);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.5);
    }

    /* Phase Timeline Card */
    .phase-timeline-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-left: 4px solid #10B981;
        border-radius: 10px;
        padding: 1.1rem;
        margin-bottom: 0.9rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    /* Bullet Rewrite Card */
    .bullet-diff-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    /* Tab Navigation */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: #1E293B;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 7px;
        padding: 7px 14px;
        font-weight: 600;
        font-size: 0.9rem;
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0F172A !important;
        color: #38BDF8 !important;
        border: 1px solid #38BDF8 !important;
    }

    /* PyVis Frame Container */
    .pyvis-container {
        border: 1px solid #334155;
        border-radius: 12px;
        overflow: hidden;
        background: #0B0F19;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }

    /* Learning Resource Card */
    .resource-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Initializing SkillBridge pipeline and knowledge graphs...")
def get_pipeline() -> SkillBridgePipeline:
    """Caches pipeline instance and graph models across user interactions."""
    return SkillBridgePipeline()


pipeline = get_pipeline()

# ==========================================
# Sample Resumes for 1-Click Evaluation
# ==========================================
SAMPLE_ML_RESUME = """John Doe
Email: john.doe@email.com | Phone: +1-555-0199 | GitHub: github.com/johndoe | LinkedIn: linkedin.com/in/johndoe

EDUCATION
Bachelor of Technology in Computer Science and Engineering
State University, 2021 - 2025 | GPA: 8.9/10

SKILLS
Programming Languages: Python, C++, SQL
Frameworks & Libraries: Scikit-Learn, Pandas, NumPy, OpenCV
Tools & Platforms: Git, Linux, Jupyter Notebooks, VS Code
Core Competencies: Machine Learning, Data Structures, Algorithms, Unit Testing

PROJECTS
Predictive Customer Churn Analysis
- Developed a machine learning classification pipeline using Python, Pandas, and Scikit-Learn to predict customer churn.
- Engineered 14 statistical features and optimized hyperparameters using GridSearchCV, achieving an 88% ROC-AUC score.
- Evaluated models using cross-validation and visualized feature importance to identify primary churn drivers.

Automated Defect Detection System
- Architected a computer vision model with Python and OpenCV that processed 500+ manufacturing images per hour.
- Implemented automated preprocessing and bounding box detection, reducing inspection errors by 22%.
- Integrated Git version control and wrote comprehensive unit tests with PyTest to maintain code quality.

EXPERIENCE
Machine Learning Intern | TechCorp Solutions (May 2024 - July 2024)
- Automated data preprocessing pipelines for 2.5GB structured datasets using Python and SQL.
- Built exploratory data analysis dashboards and collaborated with senior engineers in an Agile sprint environment.
- Documented model evaluation results and presented findings to cross-functional stakeholders.
"""

SAMPLE_FRONTEND_RESUME = """Jane Smith
Email: jane.smith@email.com | Phone: +1-555-0144 | GitHub: github.com/janesmith | LinkedIn: linkedin.com/in/janesmith

EDUCATION
B.E. in Information Technology
National Institute of Technology, 2021 - 2025

SKILLS
Languages: JavaScript, TypeScript, HTML, CSS
Frameworks: React, Next.js, Redux, Tailwind CSS
Tools: Git, GitHub, Postman, Figma, Jest

PROJECTS
E-Commerce Web Application
- Built a responsive single-page store using React, TypeScript, and Tailwind CSS serving 1,200 monthly active users.
- Integrated REST APIs for inventory and authentication with JSON Web Tokens (JWT).
- Decreased page load latency by 35% through code-splitting and asset optimization.

Developer Collaboration Board
- Engineered a real-time Kanban project dashboard using Next.js, Redux, and WebSockets.
- Created reusable UI components adhering to accessibility (a11y) standards and tested with Jest.
"""

# ==========================================
# Sidebar Controls
# ==========================================
st.sidebar.markdown("### SkillBridge Studio")

target_role = st.sidebar.selectbox(
    "Target Career Benchmark:",
    TARGET_ROLES,
    index=0,
    help="Target career knowledge graph to benchmark your skills against.",
)

# Custom Job Posting Option
use_custom_jd = st.sidebar.checkbox(
    "Paste Specific Job Posting",
    value=False,
    help="Benchmark directly against a live job description copied from LinkedIn, Indeed, or career portals.",
)

custom_jd_text = ""
if use_custom_jd:
    custom_jd_text = st.sidebar.text_area(
        "Job Description Text:",
        height=180,
        placeholder="Paste full job posting requirements here...",
        help="Paste a live job description to dynamically construct an ad-hoc requirement graph.",
    )

st.sidebar.markdown("---")
st.sidebar.markdown("#### Candidate Resume Input")

input_mode = st.sidebar.radio("Input Format:", ["Paste Plain Text", "Upload File (.pdf, .docx, .txt)"])

resume_text_input = ""
uploaded_file_bytes = None
uploaded_filename = None

if input_mode == "Paste Plain Text":
    col_btn1, col_btn2 = st.sidebar.columns(2)
    sample_to_load = None
    if col_btn1.button("ML Preset", help="Load ML Engineer sample resume", use_container_width=True):
        sample_to_load = SAMPLE_ML_RESUME
    if col_btn2.button("Frontend", help="Load Frontend sample resume", use_container_width=True):
        sample_to_load = SAMPLE_FRONTEND_RESUME

    default_val = sample_to_load if sample_to_load else SAMPLE_ML_RESUME
    resume_text_input = st.sidebar.text_area(
        "Resume Text Editor:",
        value=default_val,
        height=240,
        help="Paste complete resume or skills and projects sections.",
    )
else:
    uploaded_file = st.sidebar.file_uploader(
        "Upload Resume Document:",
        type=["pdf", "docx", "txt"],
        help="Upload PDF, DOCX, or plain text resume.",
    )
    if uploaded_file is not None:
        uploaded_file_bytes = uploaded_file.read()
        uploaded_filename = uploaded_file.name
        st.sidebar.success(f"Loaded: {uploaded_filename}")

# Recommender Weights Configuration
with st.sidebar.expander("Recommendation Objective Weights", expanded=False):
    st.caption("Score = w1·Connectivity + w2·Demand + w3·Ease")
    w1 = st.slider("w1: Graph Bridge Effect (Connectivity)", 0.0, 1.0, WEIGHT_CONNECTIVITY, 0.05)
    w2 = st.slider("w2: Employer Demand Frequency", 0.0, 1.0, WEIGHT_DEMAND, 0.05)
    w3 = st.slider("w3: Learning Ease (1 / Weeks)", 0.0, 1.0, WEIGHT_EASE, 0.05)
    total_w = w1 + w2 + w3
    if total_w > 0:
        w1, w2, w3 = w1 / total_w, w2 / total_w, w3 / total_w

analyze_button = st.sidebar.button("Run Career Audit", type="primary", use_container_width=True)

# ==========================================
# Main Dashboard Header Banner
# ==========================================
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">SkillBridge: Skill-Gap Graph & Career Recommender</div>
        <p class="hero-subtitle">
            Interpretable graph-theoretic skill gap analysis, explainable next-best-skill recommendations, peer benchmarking, and ATS readability audits for computer science engineering students.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if analyze_button or "results" in st.session_state:
    if analyze_button:
        with st.spinner("Analyzing resume against industry knowledge graph, all roles, and peer distributions..."):
            if input_mode == "Upload File (.pdf, .docx, .txt)" and uploaded_file_bytes is not None:
                results = pipeline.run_full_analysis(
                    resume_input=uploaded_file_bytes,
                    filename=uploaded_filename,
                    target_role=target_role,
                    custom_job_description=custom_jd_text if use_custom_jd else None,
                    w1=w1,
                    w2=w2,
                    w3=w3,
                )
            else:
                results = pipeline.run_full_analysis(
                    resume_input=resume_text_input,
                    filename=None,
                    target_role=target_role,
                    custom_job_description=custom_jd_text if use_custom_jd else None,
                    w1=w1,
                    w2=w2,
                    w3=w3,
                )
            st.session_state["results"] = results
            st.session_state["analyzed_role"] = target_role
    else:
        results = st.session_state["results"]

    gap_data = results["gap_results"]
    recommendations = results["recommendations"]
    readability = results["readability"]
    resources = results["resources"]
    leaderboard = results["leaderboard"]
    roadmap = results["roadmap"]
    peer = results["peer_benchmark"]
    bullet_rewrites = results["bullet_rewrites"]
    markdown_report = results["markdown_report"]
    html_report = results.get("html_report", "")
    top_rec = recommendations[0] if recommendations else None

    # ----------------------------------------------------
    # ROW 1: METRIC CARDS WITH RADIAL GAUGES
    # ----------------------------------------------------
    col1, col2, col3, col4, col5 = st.columns([1.1, 1, 1, 1, 1.2])

    with col1:
        # Radial Gauge for Overall Fit Score
        fit_score = gap_data["overall_match_score"]
        gauge_color = "#10B981" if fit_score >= 60 else "#38BDF8" if fit_score >= 40 else "#F59E0B"

        fig_fit = go.Figure(go.Indicator(
            mode="gauge+number",
            value=fit_score,
            number={"suffix": "%", "font": {"size": 26, "color": "#F8FAFC", "family": "Plus Jakarta Sans"}},
            title={"text": "Overall Fit", "font": {"size": 12, "color": "#94A3B8", "family": "Plus Jakarta Sans"}},
            gauge={
                "axis": {"range": [0, 100], "visible": False},
                "bar": {"color": gauge_color, "thickness": 0.28},
                "bgcolor": "#334155",
                "borderwidth": 0,
            }
        ))
        fig_fit.update_layout(height=130, margin=dict(l=10, r=10, t=25, b=5), paper_bgcolor="rgba(0,0,0,0)")
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.plotly_chart(fig_fit, use_container_width=True, config={"displayModeBar": False})
        st.caption("Blended Coverage & TF-IDF")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        cov_val = gap_data.get("tech_coverage_pct", gap_data["set_coverage_score"])
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-title">Technical Coverage</div>
                <div class="metric-card-val" style="color: #38BDF8;">{cov_val}%</div>
                <div class="metric-card-sub">{len(gap_data['matched_skills'])} of {gap_data['total_role_skills']} Core Skills</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        p_pct = peer["percentile"]
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-title">Peer Percentile</div>
                <div class="metric-card-val" style="color: {peer['color']};">{p_pct}%</div>
                <div class="metric-card-sub">54k Applicant Pool</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        read_score = readability["readability_score"]
        read_color = "#10B981" if read_score >= 75 else "#F59E0B" if read_score >= 50 else "#EF4444"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-title">ATS Readability</div>
                <div class="metric-card-val" style="color: {read_color};">{read_score}<span style="font-size:1.1rem; color:#64748B;">/100</span></div>
                <div class="metric-card-sub">Rubric & Active Verbs</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col5:
        rec_name = top_rec["skill"] if top_rec else "Complete"
        st.markdown(
            f"""
            <div class="metric-card" style="border: 2px solid #F59E0B; background: #1E293B;">
                <div class="metric-card-title" style="color: #FBBF24;">Top Next Skill</div>
                <div class="metric-card-val" style="color: #F59E0B; font-size: 1.55rem;">{rec_name}</div>
                <div class="metric-card-sub" style="color: #FDE68A;">Highest Bridge & Demand Rank</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # RECOMMENDATION BANNER & EXPORT BUTTONS
    # ----------------------------------------------------
    col_rec_card, col_dl1, col_dl2 = st.columns([2.8, 0.85, 0.85])
    with col_rec_card:
        if top_rec:
            st.markdown(
                f"""
                <div class="rec-highlight-card">
                    <div style="font-weight: 800; color: #FBBF24; font-size: 1.12rem; margin-bottom: 4px;">
                        First Recommended Step: <b>{top_rec['skill']}</b> <span style="font-size:0.82rem; background:rgba(245,158,11,0.25); color:#FDE68A; border:1px solid rgba(245,158,11,0.4); padding:2px 8px; border-radius:12px; margin-left:6px;">{top_rec['category']}</span>
                    </div>
                    <div style="color: #F1F5F9; font-size: 0.93rem; line-height: 1.5;">{top_rec['reason']}</div>
                    <div style="margin-top: 8px; font-size: 0.85rem; color: #FCD34D; font-family: 'JetBrains Mono', monospace;">
                        Combined Score: <b>{top_rec['score']}</b> • Bridge Index: <b>{top_rec['norm_connectivity']}</b> • Role Demand: <b>{top_rec['demand']*100:.1f}%</b> • Est. Study: <b>~{top_rec['est_weeks_to_learn']} wks</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with col_dl1:
        st.download_button(
            label="Executive Report (HTML)",
            data=html_report,
            file_name=f"SkillBridge_Executive_Report_{target_role.replace(' ', '_')}.html",
            mime="text/html",
            use_container_width=True,
            help="Download a formatted printable HTML report with print-optimized CSS for PDF export.",
        )
    with col_dl2:
        st.download_button(
            label="Audit Report (Markdown)",
            data=markdown_report,
            file_name=f"SkillBridge_Report_{target_role.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
            help="Download raw Markdown report containing complete metrics and tables.",
        )

    # ----------------------------------------------------
    # REAL-WORLD COMPATIBILITY MATRIX: COVERED vs PENDING vs WHAT TO COVER
    # ----------------------------------------------------
    st.markdown("### Job Compatibility Matrix")
    c_cov, c_pend, c_action = st.columns([1, 1, 1])

    with c_cov:
        matched_list = gap_data.get("matched_skills", [])
        matched_chips = "".join([f'<span class="skill-chip skill-chip-acquired">✓ {s}</span>' for s in matched_list]) or '<span style="color:#64748B;">None detected</span>'
        st.markdown(
            f"""
            <div class="metric-card" style="text-align:left; border-top: 4px solid #10B981;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <div style="font-weight:800; color:#34D399; font-size:1.02rem;">What Is Matching</div>
                    <span style="font-size:0.8rem; background:rgba(16,185,129,0.2); color:#34D399; border:1px solid rgba(16,185,129,0.4); padding:2px 8px; border-radius:10px; font-weight:700;">{len(matched_list)} Covered</span>
                </div>
                <div style="font-size:0.84rem; color:#94A3B8; margin-bottom:8px;">
                    Skills verified on your resume matching requirements:
                </div>
                <div style="max-height: 140px; overflow-y: auto;">
                    {matched_chips}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_pend:
        missing_list = gap_data.get("missing_skills", [])
        total_weeks = sum(g.get("est_weeks_to_learn", 3) for g in gap_data.get("gap_list", []))
        missing_chips = "".join([f'<span class="skill-chip skill-chip-missing">+ {s}</span>' for s in missing_list[:12]]) or '<span style="color:#34D399; font-weight:600;">All skills covered</span>'
        st.markdown(
            f"""
            <div class="metric-card" style="text-align:left; border-top: 4px solid #EF4444;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <div style="font-weight:800; color:#F87171; font-size:1.02rem;">What Is Pending</div>
                    <span style="font-size:0.8rem; background:rgba(239,68,68,0.2); color:#F87171; border:1px solid rgba(239,68,68,0.4); padding:2px 8px; border-radius:10px; font-weight:700;">{len(missing_list)} Gaps (~{total_weeks} wks)</span>
                </div>
                <div style="font-size:0.84rem; color:#94A3B8; margin-bottom:8px;">
                    Requirements currently missing from your resume:
                </div>
                <div style="max-height: 140px; overflow-y: auto;">
                    {missing_chips}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_action:
        if top_rec:
            res_links = resources.get(top_rec["skill"], [])
            direct_link_html = f'<a href="{res_links[0]["url"]}" target="_blank" style="text-decoration:none; color:#38BDF8; font-weight:700; font-size:0.82rem;">Learn Now: {res_links[0]["title"][:28]}...</a>' if res_links else ""
            st.markdown(
                f"""
                <div class="metric-card" style="text-align:left; border-top: 4px solid #F59E0B; background:#1E293B;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="font-weight:800; color:#FBBF24; font-size:1.02rem;">What To Cover First</div>
                        <span style="font-size:0.8rem; background:rgba(245,158,11,0.25); color:#FDE68A; border:1px solid rgba(245,158,11,0.4); padding:2px 8px; border-radius:10px; font-weight:700;">~{top_rec['est_weeks_to_learn']} Weeks</span>
                    </div>
                    <div style="font-size:1.25rem; font-weight:800; color:#F59E0B; margin-bottom:4px;">
                        {top_rec['skill']}
                    </div>
                    <div style="font-size:0.84rem; color:#94A3B8; margin-bottom:8px; line-height:1.4;">
                        Bridges directly with your existing tools with highest market demand.
                    </div>
                    <div>
                        {direct_link_html}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="metric-card" style="text-align:left; border-top: 4px solid #10B981; background:#1E293B;">
                    <div style="font-weight:800; color:#34D399; font-size:1.02rem;">Ready to Apply</div>
                    <p style="color:#94A3B8; font-size:0.88rem; margin-top:8px;">All core technical requirements are fulfilled.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # TABS: COMPREHENSIVE SUITE
    # ----------------------------------------------------
    t_gap, t_lead, t_road, t_graph, t_peer, t_rew, t_read = st.tabs([
        "Skill Gaps & Chips",
        "Career Leaderboard",
        "12-Week Roadmap",
        "Knowledge Graph",
        "Peer Distribution",
        "Bullet Rewriter",
        "ATS Audit & Links",
    ])

    # TAB 1: GAP ANALYSIS & VISUAL CHIPS
    with t_gap:
        col_cat, col_gap = st.columns([1, 1.1])

        with col_cat:
            st.subheader("Category Match Breakdown")
            cat_breakdown = gap_data["category_breakdown"]
            if cat_breakdown:
                cat_names = []
                cat_pcts = []
                cat_hover = []
                for cat, val in cat_breakdown.items():
                    cat_names.append(cat)
                    cat_pcts.append(val["match_pct"])
                    cat_hover.append(f"{val['matched_count']} matched of {val['total_required']} required")

                fig_cat = go.Figure(go.Bar(
                    x=cat_pcts,
                    y=cat_names,
                    orientation="h",
                    marker=dict(
                        color=cat_pcts,
                        colorscale=[[0, "#38BDF8"], [0.5, "#60A5FA"], [1, "#10B981"]],
                        line=dict(color="#1E293B", width=1),
                    ),
                    text=[f"{p}%" for p in cat_pcts],
                    textposition="auto",
                    textfont=dict(color="#F8FAFC", family="Plus Jakarta Sans"),
                    hoverinfo="text",
                    hovertext=cat_hover,
                ))
                fig_cat.update_layout(
                    height=280,
                    margin=dict(l=10, r=20, t=10, b=10),
                    xaxis=dict(title="Match %", range=[0, 100], showgrid=True, gridcolor="#334155", color="#94A3B8"),
                    yaxis=dict(autorange="reversed", color="#F8FAFC"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#F8FAFC", family="Plus Jakarta Sans"),
                )
                st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})

            # Skill Chips Visualizer
            st.markdown("#### Skills Verified on Your Resume")
            user_chips_html = "".join([f'<span class="skill-chip skill-chip-acquired">✓ {s}</span>' for s in gap_data["matched_skills"]])
            if user_chips_html:
                st.markdown(f'<div style="margin-bottom:12px;">{user_chips_html}</div>', unsafe_allow_html=True)
            else:
                st.caption("No core matching skills detected in resume.")

            st.markdown("#### Missing Role Requirements")
            missing_chips_html = "".join([f'<span class="skill-chip skill-chip-missing">+ {s}</span>' for s in gap_data["missing_skills"][:14]])
            if missing_chips_html:
                st.markdown(f'<div>{missing_chips_html}</div>', unsafe_allow_html=True)

        with col_gap:
            st.subheader(f"Missing Skills Ranked by Industry Demand ({len(gap_data['gap_list'])})")
            gap_records = gap_data["gap_list"]
            if gap_records:
                gap_table_data = []
                for g in gap_records:
                    gap_table_data.append({
                        "Missing Skill": g["skill"],
                        "Category": g["category"],
                        "Employer Demand": f"{g['demand']*100:.1f}%",
                        "Estimated Effort": f"~{g['est_weeks_to_learn']} weeks",
                    })
                gap_df = pd.DataFrame(gap_table_data)
                st.dataframe(gap_df, hide_index=True, use_container_width=True, height=380)
            else:
                st.success("All high-demand skills for this role are fulfilled.")

    # TAB 2: MULTI-ROLE LEADERBOARD & RADAR CHART
    with t_lead:
        st.subheader("Career Role Readiness Leaderboard")
        st.caption("Objective comparison of candidate readiness across all 8 target career paths.")

        best_role = leaderboard[0]["role"]
        best_score = leaderboard[0]["overall_fit"]
        second_role = leaderboard[1]["role"] if len(leaderboard) > 1 else ""
        second_score = leaderboard[1]["overall_fit"] if len(leaderboard) > 1 else 0
        st.info(f"Top Immediate Fit: Candidate is **{best_score}% qualified** for **{best_role}**, followed by **{second_role}** ({second_score}%).")

        col_radar, col_lead_tbl = st.columns([1, 1.2])

        with col_radar:
            roles_list = [item["role"] for item in leaderboard]
            scores_list = [item["overall_fit"] for item in leaderboard]

            fig_radar = go.Figure(data=go.Scatterpolar(
                r=scores_list + [scores_list[0]],
                theta=roles_list + [roles_list[0]],
                fill="toself",
                fillcolor="rgba(56, 189, 248, 0.2)",
                line=dict(color="#38BDF8", width=2),
                marker=dict(size=6, color="#0284C7"),
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], color="#94A3B8", gridcolor="#334155"),
                    angularaxis=dict(color="#F8FAFC", gridcolor="#334155"),
                    bgcolor="#1E293B",
                ),
                showlegend=False,
                height=340,
                margin=dict(l=40, r=40, t=20, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC", family="Plus Jakarta Sans"),
            )
            st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

        with col_lead_tbl:
            lead_df = pd.DataFrame([
                {
                    "Rank": f"#{idx}",
                    "Career Role": item["role"],
                    "Fit %": f"{item['overall_fit']}%",
                    "Coverage %": f"{item['coverage_score']}%",
                    "Matched Skills": ", ".join(item["matched_skills"][:3]) or "None",
                }
                for idx, item in enumerate(leaderboard, 1)
            ])
            st.dataframe(lead_df, hide_index=True, use_container_width=True, height=340)

    # TAB 3: 12-WEEK DIRECTED ROADMAP
    with t_road:
        st.subheader(f"12-Week Directed Learning Roadmap: {target_role}")
        st.caption(roadmap["summary"])

        if roadmap["phases"]:
            for p in roadmap["phases"]:
                milestone_items = "".join([f"<li style='margin-bottom:3px;'>{m}</li>" for m in p["milestones"]])
                st.markdown(
                    f"""
                    <div class="phase-timeline-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="font-weight: 800; color: #34D399; font-size: 1.05rem;">
                                {p['phase_title']}: <b style="color:#F8FAFC;">{p['skill']}</b>
                            </div>
                            <span style="font-size:0.8rem; background:rgba(16,185,129,0.2); color:#34D399; border:1px solid rgba(16,185,129,0.4); padding:3px 10px; border-radius:12px; font-weight:700;">
                                {p['week_span']} (~{p['duration_weeks']} weeks)
                            </span>
                        </div>
                        <p style="margin:6px 0 8px 0; color:#94A3B8; font-size:0.9rem;">
                            <b style="color:#F1F5F9;">Learning Objective:</b> {p['objective']} | Category: <code style="color:#38BDF8; background:#0F172A; padding:2px 6px; border-radius:4px;">{p['category']}</code>
                        </p>
                        <div style="font-size:0.88rem; color:#CBD5E1;">
                            <b style="color:#F1F5F9;">Milestones & Applied Outcomes:</b>
                            <ul style="margin: 4px 0 6px 18px; padding:0;">
                                {milestone_items}
                            </ul>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No gaps to sequence. All core technical requirements are fulfilled.")

    # TAB 4: INTERACTIVE KNOWLEDGE GRAPH
    with t_graph:
        st.subheader(f"Knowledge Graph Co-Occurrence Network: {target_role}")
        st.caption("Node size reflects market demand. Edge thickness represents empirical co-occurrence frequency across job postings.")

        # High-Contrast Legend with Explicit Font Colors
        st.markdown(
            """
            <div style="display:flex; flex-wrap:wrap; gap:18px; font-size:0.88rem; font-weight:600; margin-bottom:12px; padding:10px 16px; background:#1E293B; border:1px solid #334155; border-radius:10px; color:#F8FAFC;">
                <span style="display:inline-flex; align-items:center; gap:8px;">
                    <span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:#10B981; border:1px solid #A7F3D0;"></span>
                    <span style="color:#F1F5F9;">Acquired Skills (Resume)</span>
                </span>
                <span style="display:inline-flex; align-items:center; gap:8px;">
                    <span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:#EF4444; border:1px solid #FECACA;"></span>
                    <span style="color:#F1F5F9;">Missing Role Skills</span>
                </span>
                <span style="display:inline-flex; align-items:center; gap:8px;">
                    <span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:#F59E0B; border:1px solid #FDE68A;"></span>
                    <span style="color:#F1F5F9;">Top Recommended Step</span>
                </span>
                <span style="display:inline-flex; align-items:center; gap:8px;">
                    <span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:#FB923C; border:1px solid #FED7AA;"></span>
                    <span style="color:#F1F5F9;">Secondary Recommendations</span>
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="pyvis-container">', unsafe_allow_html=True)
        components.html(results["graph_html"], height=580, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)

    # TAB 5: PEER PERCENTILE BELL CURVE
    with t_peer:
        st.subheader("Applicant Pool Distribution (54k Resumes Model)")
        st.caption(f"Statistical benchmark comparing candidate skill counts against peers targeting {target_role}.")

        col_bell, col_stat = st.columns([1.3, 1])

        with col_bell:
            mean = peer["peer_mean_skills"]
            user_val = peer["user_skill_count"]
            x = np.linspace(0, 12, 200)
            y = stats.norm.pdf(x, mean, 1.8)

            fig_bell = go.Figure()
            fig_bell.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color="#64748B", width=2), name="Applicant Pool"))

            x_fill = np.linspace(0, min(12, user_val), 100)
            y_fill = stats.norm.pdf(x_fill, mean, 1.8)
            fig_bell.add_trace(go.Scatter(x=x_fill, y=y_fill, fill="tozeroy", fillcolor="rgba(56, 189, 248, 0.25)", line=dict(color="rgba(0,0,0,0)"), name="Candidate Area"))

            fig_bell.add_vline(x=user_val, line_width=2.5, line_dash="dash", line_color="#38BDF8", annotation_text=f"Candidate ({user_val} skills)", annotation_position="top right", annotation_font_color="#38BDF8")

            fig_bell.update_layout(
                title=dict(text=f"Applicant Skill Count Gaussian Curve (Mean = {mean})", font=dict(color="#F8FAFC", family="Plus Jakarta Sans")),
                xaxis=dict(title="Number of Core Relevant Skills", showgrid=True, gridcolor="#334155", color="#94A3B8"),
                yaxis=dict(title="Probability Density", showgrid=True, gridcolor="#334155", color="#94A3B8"),
                height=320,
                margin=dict(l=20, r=20, t=40, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                font=dict(color="#F8FAFC", family="Plus Jakarta Sans"),
            )
            st.plotly_chart(fig_bell, use_container_width=True, config={"displayModeBar": False})

        with col_stat:
            st.markdown(
                f"""
                <div class="metric-card" style="text-align:left; padding:1.5rem;">
                    <div style="font-weight:700; color:#F8FAFC; font-size:1.1rem; margin-bottom:8px;">
                        Candidate Standing: <span style="color:{peer['color']};">{peer['standing']}</span>
                    </div>
                    <ul style="font-size:0.92rem; color:#94A3B8; padding-left:18px; line-height:1.7;">
                        <li>Candidate Relevant Core Skills: <b style="color:#F8FAFC;">{user_val}</b></li>
                        <li>Applicant Average (μ): <b style="color:#F8FAFC;">{mean} skills</b></li>
                        <li>Standard Deviation (σ): <b style="color:#F8FAFC;">1.8</b></li>
                        <li>Calculated Z-Score: <b style="color:#38BDF8;">{peer['z_score']}</b></li>
                        <li><b>Percentile Standing: <span style="color:#34D399;">{peer['percentile']}th percentile</span></b></li>
                    </ul>
                    <div style="font-size:0.84rem; color:#CBD5E1; background:#0F172A; border:1px solid #334155; padding:8px 12px; border-radius:6px;">
                        Candidate possesses more verified skills than <b>{peer['percentile']}%</b> of applicants in this empirical benchmark pool.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # TAB 6: RESUME BULLET REWRITER (XYZ Formula)
    with t_rew:
        st.subheader("Action-Verb Bullet Rewriter (Google XYZ Formula)")
        st.caption("Transforms weak or passive bullet points into quantified engineering statements: Accomplished [X], as measured by [Y], by doing [Z].")

        if bullet_rewrites:
            for idx, item in enumerate(bullet_rewrites, 1):
                reasons_str = " • ".join(item["reasons"])
                options_str = "".join([f"<li style='margin-bottom:6px;'>{opt}</li>" for opt in item["improved_options"]])
                st.markdown(
                    f"""
                    <div class="bullet-diff-card">
                        <span style="font-size:0.8rem; background:rgba(239,68,68,0.2); color:#F87171; border:1px solid rgba(239,68,68,0.4); padding:3px 10px; border-radius:12px; font-weight:700;">Original Bullet #{idx}</span>
                        <p style="margin:8px 0; color:#F8FAFC; font-style:italic; font-weight:500;">"{item['original']}"</p>
                        <div style="font-size:0.82rem; color:#F87171; margin-bottom:10px;">
                            {reasons_str}
                        </div>
                        <span style="font-size:0.8rem; background:rgba(16,185,129,0.2); color:#34D399; border:1px solid rgba(16,185,129,0.4); padding:3px 10px; border-radius:12px; font-weight:700;">Recommended Engineering Alternatives (XYZ)</span>
                        <ul style="margin:8px 0 0 16px; color:#E2E8F0; font-size:0.92rem; line-height:1.6;">
                            {options_str}
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("All bullet points in your resume start with active past-tense engineering verbs and contain quantified metrics.")

    # TAB 7: ATS AUDIT & VERIFIED LEARNING LINKS
    with t_read:
        col_audit, col_res = st.columns([1, 1])

        with col_audit:
            st.subheader("ATS Formatting & Readability Audit")
            rules = readability["rules"]

            for r_key, r_info in rules.items():
                rule_name = r_info.get("rule", r_key)
                score = r_info.get("score")
                max_s = r_info.get("max_score")
                if score is not None and max_s is not None:
                    pct = score / max_s if max_s > 0 else 0
                    st.write(f"**{rule_name}** ({score}/{max_s} pts)")
                    st.progress(pct)

            st.markdown("---")
            st.subheader("Actionable Optimization Tips")
            for tip in readability["tips"]:
                st.markdown(f"• {tip}")

        with col_res:
            st.subheader("Curated Learning Resources for Recommended Skills")
            for rec in recommendations:
                skill_name = rec["skill"]
                res_list = resources.get(skill_name, [])
                st.markdown(f"#### {skill_name} (`{rec['category']}`)")
                if res_list:
                    for item in res_list:
                        st.markdown(
                            f"""
                            <div class="resource-card">
                                <b><a href="{item['url']}" target="_blank" style="text-decoration:none; color:#38BDF8;">{item['title']}</a></b><br>
                                <span style="font-size:0.8rem; color:#94A3B8;">{item['url']}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

else:
    # Empty State Guidance
    st.info("Select your target role on the sidebar, review the sample resume or paste your own, and click 'Run Career Audit' to begin.")

    st.markdown("### Architectural Overview & Methodologies")
    st.markdown(
        """
        **SkillBridge** replaces black-box deep learning models with **interpretable, explainable graph algorithms**:

        1. **spaCy PhraseMatcher**: High-precision skill extraction with 120+ alias normalizations.
        2. **Dual-Fit Scoring**: Evaluates **Set Coverage** of core skills and **TF-IDF Cosine Similarity** against role requirements.
        3. **Co-Occurrence Knowledge Graph**: NetworkX graph modeling empirical industry skill pairings.
        4. **Multi-Criteria Optimization Algorithm**:
           $$\\text{Score}(M) = w_1 \\cdot \\text{Connectivity}(M) + w_2 \\cdot \\text{Demand}(M) + w_3 \\cdot \\text{Ease}(M)$$
        5. **All-Roles Career Leaderboard**: Compares student capabilities against all 8 target roles simultaneously.
        6. **12-Week Directed Learning Roadmap**: Chronological semester schedule for bridging identified gaps.
        7. **54k Resume Peer Benchmarking**: Statistical percentile ranking based on empirical applicant distributions.
        8. **Action-Verb Bullet Rewriter**: Google XYZ formula assistant transforming passive bullets into metrics.
        """
    )
