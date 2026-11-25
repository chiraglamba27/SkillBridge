"""Configuration module for SkillBridge.

Contains directory paths, model constants, default weights, and threshold values.
Designed to be easily explainable for viva examinations with no magic numbers.
"""

from pathlib import Path

# ==========================================
# 1. Project Directory Paths
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SKILL_META_PATH = DATA_DIR / "skill_meta.csv"

# Output files
JOB_SKILLS_PARQUET = PROCESSED_DATA_DIR / "job_skills.parquet"
JOB_SKILLS_CSV = PROCESSED_DATA_DIR / "job_skills.csv"
GRAPH_FILE_TEMPLATE = PROCESSED_DATA_DIR / "graph_{role}.gpickle"
ROLE_DEMAND_CSV = PROCESSED_DATA_DIR / "role_demand.csv"

# Ensure output directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. Canonical Target Roles
# ==========================================
TARGET_ROLES = [
    "Machine Learning Engineer",
    "Data Scientist",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Data Engineer",
]

# Role mapping aliases to standardize raw job posting titles
ROLE_ALIASES = {
    "ml engineer": "Machine Learning Engineer",
    "machine learning engineer": "Machine Learning Engineer",
    "ai engineer": "Machine Learning Engineer",
    "deep learning engineer": "Machine Learning Engineer",
    "data scientist": "Data Scientist",
    "data science specialist": "Data Scientist",
    "frontend developer": "Frontend Developer",
    "frontend engineer": "Frontend Developer",
    "front end developer": "Frontend Developer",
    "ui developer": "Frontend Developer",
    "backend developer": "Backend Developer",
    "backend engineer": "Backend Developer",
    "back end developer": "Backend Developer",
    "full stack developer": "Full Stack Developer",
    "full stack engineer": "Full Stack Developer",
    "fullstack engineer": "Full Stack Developer",
    "fullstack developer": "Full Stack Developer",
    "devops engineer": "DevOps Engineer",
    "site reliability engineer": "DevOps Engineer",
    "sre": "DevOps Engineer",
    "cloud engineer": "Cloud Engineer",
    "cloud architect": "Cloud Engineer",
    "data engineer": "Data Engineer",
    "big data engineer": "Data Engineer",
}

# ==========================================
# 3. Graph & Demand Thresholds
# ==========================================
# Minimum number of co-occurrences required to draw an edge between two skills.
# This prevents noisy one-off associations from cluttering the graph.
MIN_EDGE_WEIGHT = 2

# Demand threshold: minimum fraction of postings in a role that must mention
# a skill for it to be considered a 'core / high-demand' skill (15% by default).
DEMAND_THRESHOLD = 0.15

# ==========================================
# 4. Next-Best-Skill Recommendation Weights
# ==========================================
# Objective function: score = w1 * connectivity + w2 * demand + w3 * ease
# Default weights:
# w1 (0.50): Bridge effect - prior skills make learning adjacent skills easier
# w2 (0.30): Market demand - employer relevance
# w3 (0.20): Ease of acquisition - lower estimated weeks to learn
WEIGHT_CONNECTIVITY = 0.50
WEIGHT_DEMAND = 0.30
WEIGHT_EASE = 0.20

# Constant used in ease function: ease = 1 / (1 + est_weeks / EASE_WEEKS_SCALE)
# A 4-week benchmark represents an average single academic month / module.
EASE_WEEKS_SCALE = 4.0

# ==========================================
# 5. Resume Readability Checker Constants
# ==========================================
MIN_RESUME_WORDS = 150
MAX_RESUME_WORDS = 800
MAX_BULLET_WORDS = 25
TARGET_ACTION_VERB_RATIO = 0.60
TARGET_QUANTIFIED_RATIO = 0.30

# Standard required resume sections for CSE undergraduates
STANDARD_SECTIONS = [
    "education",
    "skills",
    "projects",
    "experience",
]

# Action verbs list (100+ strong engineering action verbs)
ACTION_VERBS = {
    "accelerated", "achieved", "acquired", "adapted", "administered", "advanced",
    "advised", "allocated", "analyzed", "architected", "automated", "boosted",
    "built", "calculated", "centralized", "championed", "collaborated", "compiled",
    "composed", "computed", "configured", "consolidated", "constructed", "containerized",
    "converted", "coordinated", "created", "customized", "debugged", "decreased",
    "defined", "delivered", "deployed", "designed", "developed", "devised",
    "diagnosed", "directed", "discovered", "documented", "drafted", "eliminated",
    "enabled", "engineered", "enhanced", "established", "evaluated", "executed",
    "expanded", "expedited", "fabricated", "facilitated", "formulated", "founded",
    "generated", "governed", "guided", "halved", "harnessed", "headed",
    "identified", "implemented", "improved", "increased", "indexed", "initiated",
    "innovated", "inspected", "installed", "integrated", "investigated", "launched",
    "lead", "led", "maintained", "managed", "maximized", "measured",
    "mentored", "migrated", "minimized", "modeled", "modernized", "monitored",
    "negotiated", "operated", "optimized", "orchestrated", "organized", "overhauled",
    "performed", "pioneered", "planned", "prepared", "programmed", "published",
    "reduced", "refactored", "refined", "remodeled", "reorganized", "resolved",
    "restructured", "revamped", "reviewed", "scaled", "scheduled", "secured",
    "simplified", "solved", "spearheaded", "standardized", "streamlined", "strengthened",
    "structured", "supervised", "synthesized", "tested", "tracked", "trained",
    "transformed", "troubleshot", "unified", "upgraded", "validated", "verified"
}
