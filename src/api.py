"""FastAPI REST API Backend for SkillBridge.

Exposes SkillBridgePipeline as clean, high-performance JSON endpoints
for the bespoke React / Vite web application.
"""

from pathlib import Path
import sys
from typing import Dict, List, Optional, Union

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel

from src.config import TARGET_ROLES, WEIGHT_CONNECTIVITY, WEIGHT_DEMAND, WEIGHT_EASE
from src.pipeline import SkillBridgePipeline

app = FastAPI(
    title="SkillBridge API",
    description="Interpretable Graph-Theoretic Career Fit & Skill-Gap Analysis Engine",
    version="2.0.0",
)

# Enable CORS for local Vite development and custom frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton pipeline instance initialized at startup
_pipeline: Optional[SkillBridgePipeline] = None


def get_pipeline() -> SkillBridgePipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = SkillBridgePipeline()
    return _pipeline


# Sample Resumes for quick-start testing
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


class AnalyzeRequestJSON(BaseModel):
    resume_text: str
    target_role: str = "Machine Learning Engineer"
    custom_job_description: Optional[str] = None
    w1: float = WEIGHT_CONNECTIVITY
    w2: float = WEIGHT_DEMAND
    w3: float = WEIGHT_EASE


@app.on_event("startup")
def startup_event():
    """Pre-loads spaCy, dataset models, and graphs into memory."""
    get_pipeline()


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "SkillBridge API", "version": "2.0.0"}


@app.get("/api/roles")
def get_roles():
    """Returns available target benchmark roles, objective weights, and sample presets."""
    return {
        "roles": TARGET_ROLES,
        "default_weights": {
            "w1_connectivity": WEIGHT_CONNECTIVITY,
            "w2_demand": WEIGHT_DEMAND,
            "w3_ease": WEIGHT_EASE,
        },
        "sample_resumes": {
            "machine_learning": SAMPLE_ML_RESUME,
            "frontend": SAMPLE_FRONTEND_RESUME,
        },
    }


def _extract_graph_json(pipeline: SkillBridgePipeline, role: str, user_skills: List[str], rec_skills: List[str], custom_jd: Optional[str] = None, gap_results: Optional[Dict] = None):
    """Formats NetworkX knowledge graph into pure JSON for client-side Vis.js rendering."""
    if custom_jd and custom_jd.strip() and gap_results:
        G = pipeline.get_role_graph(role)
        all_skills = set(gap_results.get("matched_skills", []) + gap_results.get("missing_skills", []))
    else:
        G = pipeline.get_role_graph(role)
        all_skills = set(G.nodes())

    user_set = set(user_skills)
    rec_set = set(rec_skills)
    top_rec = rec_skills[0] if rec_skills else None

    nodes = []
    for node in all_skills:
        meta = pipeline.extractor.get_skill_metadata(node)
        demand_val = G.nodes[node].get("demand", 0.5) if G.has_node(node) else 0.5
        category = meta.get("category", "Other")
        weeks = int(meta.get("est_weeks_to_learn", 3))
        res_url = str(meta.get("resource_url", ""))
        res_title = str(meta.get("resource_title", f"{node} Reference"))
        node_size = int(18 + (demand_val * 24))

        # Node classification: known (green filled), missing (vermilion hollow), recommended (saffron filled ring)
        if node == top_rec:
            bg_color = "#D99A1E"  # Saffron
            border_color = "#14130F"
            status = "Recommended"
            node_type = "recommended"
            border_width = 3.5
        elif node in rec_set:
            bg_color = "#D99A1E"
            border_color = "#D99A1E"
            status = "Secondary Recommendation"
            node_type = "secondary"
            border_width = 2
        elif node in user_set:
            bg_color = "#1F6B4F"  # Deep green filled
            border_color = "#1F6B4F"
            status = "Verified"
            node_type = "known"
            border_width = 2
        else:
            bg_color = "#14130F"  # Hollow center matching dark canvas
            border_color = "#C8412B"  # Vermilion ring
            status = "Missing"
            node_type = "missing"
            border_width = 2.5

        # Connections to the user's known skills
        connections = []
        if G.has_node(node):
            for nbr in G.neighbors(node):
                if nbr in user_set and nbr != node:
                    w = G[node][nbr].get("weight", 1)
                    connections.append({"skill": nbr, "weight": int(w)})
        connections.sort(key=lambda x: x["weight"], reverse=True)

        nodes.append({
            "id": node,
            "label": node,
            "category": category,
            "demand": round(demand_val * 100, 1),
            "est_weeks": weeks,
            "status": status,
            "node_type": node_type,
            "resource_url": res_url,
            "resource_title": res_title,
            "connections_to_user_skills": connections,
            "color": {
                "background": bg_color,
                "border": border_color,
                "highlight": {"background": bg_color, "border": "#2B4C9B"},
                "hover": {"background": bg_color, "border": "#2B4C9B"},
            },
            "size": node_size,
            "borderWidth": border_width,
        })

    edges = []
    nodes_set = {n["id"] for n in nodes}
    for u in nodes_set:
        for v in nodes_set:
            if u < v and G.has_edge(u, v):
                w = G[u][v].get("weight", 1)
                edges.append({
                    "from": u,
                    "to": v,
                    "value": w,
                    "title": f"Co-occurrences: {w}",
                })

    return {"nodes": nodes, "edges": edges}


@app.post("/api/analyze")
async def analyze_career(
    resume_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
    target_role: str = Form("Machine Learning Engineer"),
    custom_job_description: Optional[str] = Form(None),
    w1: float = Form(WEIGHT_CONNECTIVITY),
    w2: float = Form(WEIGHT_DEMAND),
    w3: float = Form(WEIGHT_EASE),
):
    """Performs full end-to-end career gap, readability, and graph recommendation audit."""
    pipeline = get_pipeline()

    if target_role not in TARGET_ROLES and not (custom_job_description and custom_job_description.strip()):
        target_role = TARGET_ROLES[0]

    resume_input_data: Union[str, bytes] = ""
    filename = None

    if resume_file is not None and resume_file.filename:
        resume_input_data = await resume_file.read()
        filename = resume_file.filename
    elif resume_text and resume_text.strip():
        resume_input_data = resume_text.strip()
    else:
        resume_input_data = SAMPLE_ML_RESUME

    total_w = w1 + w2 + w3
    if total_w > 0:
        w1, w2, w3 = w1 / total_w, w2 / total_w, w3 / total_w

    results = pipeline.run_full_analysis(
        resume_input=resume_input_data,
        filename=filename,
        target_role=target_role,
        custom_job_description=custom_job_description if custom_job_description and custom_job_description.strip() else None,
        w1=w1,
        w2=w2,
        w3=w3,
    )

    rec_skill_names = [r["skill"] for r in results["recommendations"]]
    graph_data = _extract_graph_json(
        pipeline=pipeline,
        role=target_role,
        user_skills=results["gap_results"]["matched_skills"],
        rec_skills=rec_skill_names,
        custom_jd=custom_job_description,
        gap_results=results["gap_results"],
    )
    results["graph_data"] = graph_data
    results["meta"] = {
        "data_source": "Industry benchmark co-occurrence network (400 validated role profiles) and Kaggle 54k resume Gaussian distribution model",
        "is_custom_job": bool(custom_job_description and custom_job_description.strip()),
    }

    return JSONResponse(content=results)


@app.post("/api/export/html")
async def export_html_report(
    resume_text: Optional[str] = Form(None),
    target_role: str = Form("Machine Learning Engineer"),
    custom_job_description: Optional[str] = Form(None),
):
    """Returns standalone printable HTML executive report."""
    pipeline = get_pipeline()
    text = resume_text or SAMPLE_ML_RESUME
    results = pipeline.run_full_analysis(
        resume_input=text,
        target_role=target_role,
        custom_job_description=custom_job_description,
    )
    return HTMLResponse(content=results.get("html_report", "<h1>Report Generation Failed</h1>"))


@app.post("/api/export/markdown")
async def export_markdown_report(
    resume_text: Optional[str] = Form(None),
    target_role: str = Form("Machine Learning Engineer"),
    custom_job_description: Optional[str] = Form(None),
):
    """Returns raw markdown audit report."""
    pipeline = get_pipeline()
    text = resume_text or SAMPLE_ML_RESUME
    results = pipeline.run_full_analysis(
        resume_input=text,
        target_role=target_role,
        custom_job_description=custom_job_description,
    )
    return PlainTextResponse(content=results.get("markdown_report", "# Report Generation Failed"))


# Mount compiled frontend static build if available
from fastapi.staticfiles import StaticFiles

frontend_dist = ROOT_DIR / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

