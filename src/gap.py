"""Gap analysis and match scoring module for SkillBridge.

Computes:
1. TF-IDF cosine similarity between resume text and role skill corpus.
2. Set-based coverage percentage against role's high-demand skills.
3. Category breakdown (% match per category: Languages, Frameworks, Databases, etc.).
4. Missing skills gap list sorted by market demand.
Also provides resume text extraction from plain text, PDF, and DOCX.
"""

import io
from pathlib import Path
import re
from typing import BinaryIO, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import DEMAND_THRESHOLD, JOB_SKILLS_PARQUET
from src.demand import get_high_demand_skills, get_role_demand_dict
from src.skill_extract import SkillExtractor


def extract_text_from_file(file_obj: Union[BinaryIO, bytes, str, Path], filename: str) -> str:
    """Extracts raw text from uploaded resume files (.txt, .pdf, .docx)."""
    ext = Path(filename).suffix.lower()

    if isinstance(file_obj, str):
        if "\n" in file_obj or len(file_obj) > 255:
            return file_obj
        try:
            p = Path(file_obj)
            if p.is_file():
                content_bytes = p.read_bytes()
            else:
                return file_obj
        except OSError:
            return file_obj
    elif isinstance(file_obj, Path):
        content_bytes = file_obj.read_bytes()
    elif isinstance(file_obj, bytes):
        content_bytes = file_obj
    else:
        content_bytes = file_obj.read()

    if ext in [".txt", ".md"]:
        return content_bytes.decode("utf-8", errors="ignore")

    if ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content_bytes))
            text_pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(text_pages)
        except Exception as e:
            return f"Error extracting PDF: {e}"

    if ext in [".docx", ".doc"]:
        try:
            import docx
            doc = docx.Document(io.BytesIO(content_bytes))
            text_paragraphs = [p.text for p in doc.paragraphs]
            return "\n".join(text_paragraphs)
        except Exception as e:
            return f"Error extracting DOCX: {e}"

    return content_bytes.decode("utf-8", errors="ignore")


def build_role_skill_corpus(job_skills_df: pd.DataFrame, role: str) -> str:
    """Aggregates all job descriptions and skills for a target role into a single document."""
    role_df = job_skills_df[job_skills_df["role"] == role]
    if role_df.empty:
        return ""
    
    texts = []
    for _, row in role_df.iterrows():
        skills_str = " ".join(row["skills"])
        desc_str = row.get("job_description", "")
        texts.append(f"{skills_str} {desc_str}")
        
    return " ".join(texts)


def compute_tfidf_match_score(resume_text: str, role_corpus: str) -> float:
    """Computes cosine similarity between resume text and role corpus using TF-IDF."""
    if not resume_text.strip() or not role_corpus.strip():
        return 0.0

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=2000,
        sublinear_tf=True,
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, role_corpus])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(np.clip(round(sim * 100, 2), 0.0, 100.0))
    except Exception:
        return 0.0


def compute_set_coverage_score(user_skills: List[str], role_high_demand_skills: List[str]) -> float:
    """Computes set-based coverage percentage."""
    if not role_high_demand_skills:
        return 0.0

    user_set = set(user_skills)
    role_set = set(role_high_demand_skills)
    matched = user_set.intersection(role_set)
    
    score = (len(matched) / len(role_set)) * 100.0
    return round(score, 2)


def compute_category_breakdown(
    user_skills: List[str],
    role_high_demand_skills: List[str],
    extractor: SkillExtractor,
) -> Dict[str, Dict[str, object]]:
    """Groups high-demand skills by category and computes match % per category."""
    user_set = set(user_skills)
    categories: Dict[str, Dict[str, object]] = {}

    for skill in role_high_demand_skills:
        cat = extractor.get_skill_category(skill)
        if cat not in categories:
            categories[cat] = {
                "matched_count": 0,
                "total_required": 0,
                "match_pct": 0.0,
                "matched_skills": [],
                "missing_skills": [],
            }
        
        categories[cat]["total_required"] += 1
        if skill in user_set:
            categories[cat]["matched_count"] += 1
            categories[cat]["matched_skills"].append(skill)
        else:
            categories[cat]["missing_skills"].append(skill)

    for cat, data in categories.items():
        total = data["total_required"]
        matched = data["matched_count"]
        data["match_pct"] = round((matched / total) * 100.0, 1) if total > 0 else 0.0

    return categories


def compute_gap_list(
    user_skills: List[str],
    role_high_demand_skills: List[str],
    demand_dict: Dict[str, float],
    extractor: SkillExtractor,
) -> List[Dict[str, object]]:
    """Calculates missing skills from the role's high-demand list sorted by demand descending."""
    user_set = set(user_skills)
    missing_skills = [s for s in role_high_demand_skills if s not in user_set]

    gap_records = []
    for skill in missing_skills:
        meta = extractor.get_skill_metadata(skill)
        demand = demand_dict.get(skill, 0.0)
        gap_records.append({
            "skill": skill,
            "category": meta.get("category", "Other"),
            "demand": round(demand, 4),
            "est_weeks_to_learn": int(meta.get("est_weeks_to_learn", 3)),
            "resource_url": str(meta.get("resource_url", "")),
            "resource_title": str(meta.get("resource_title", "")),
        })

    gap_records.sort(key=lambda x: x["demand"], reverse=True)
    return gap_records


def analyze_resume_gap(
    resume_text: str,
    target_role: str,
    job_skills_df: pd.DataFrame,
    demand_dict: Dict[str, float],
    extractor: Optional[SkillExtractor] = None,
    demand_threshold: float = DEMAND_THRESHOLD,
) -> Dict[str, object]:
    """Orchestrates end-to-end skill gap analysis for a resume and target role."""
    extractor = extractor or SkillExtractor()

    user_skills = extractor.extract_skills(resume_text)

    role_high_demand_skills = [
        skill for skill, demand in demand_dict.items() if demand >= demand_threshold
    ]
    role_high_demand_skills.sort(key=lambda s: demand_dict.get(s, 0.0), reverse=True)

    role_corpus = build_role_skill_corpus(job_skills_df, target_role)
    tfidf_score = compute_tfidf_match_score(resume_text, role_corpus)
    set_coverage_score = compute_set_coverage_score(user_skills, role_high_demand_skills)
    overall_match = round((0.60 * set_coverage_score) + (0.40 * tfidf_score), 1)
    category_breakdown = compute_category_breakdown(user_skills, role_high_demand_skills, extractor)
    gap_list = compute_gap_list(user_skills, role_high_demand_skills, demand_dict, extractor)
    matched_skills = [s for s in role_high_demand_skills if s in set(user_skills)]

    return {
        "target_role": target_role,
        "user_skills": user_skills,
        "matched_skills": matched_skills,
        "missing_skills": [g["skill"] for g in gap_list],
        "gap_list": gap_list,
        "tfidf_score": tfidf_score,
        "set_coverage_score": set_coverage_score,
        "overall_match_score": overall_match,
        "category_breakdown": category_breakdown,
        "total_role_skills": len(role_high_demand_skills),
    }


def analyze_custom_job_gap(
    resume_text: str,
    job_description_text: str,
    extractor: Optional[SkillExtractor] = None,
) -> Dict[str, object]:
    """Analyzes a resume directly against a specific custom real-world job description.

    Identifies:
    1. Exactly what is matching (covered).
    2. Exactly what is pending (gaps).
    3. Exactly what to cover first (prioritized by frequency and learning ease).
    """
    extractor = extractor or SkillExtractor()

    user_skills = extractor.extract_skills(resume_text)
    required_skills = extractor.extract_skills(job_description_text)

    # If no specific skills could be extracted from the custom text,
    # inform the candidate gracefully
    if not required_skills:
        return {
            "target_role": "Custom Job Posting",
            "user_skills": user_skills,
            "matched_skills": [],
            "missing_skills": [],
            "gap_list": [],
            "tfidf_score": 0.0,
            "set_coverage_score": 0.0,
            "overall_match_score": 0.0,
            "category_breakdown": {},
            "total_role_skills": 0,
            "warning": "No recognized technical or soft skills found in the pasted job description. Please ensure you paste the full 'Requirements' or 'Qualifications' section.",
        }

    # Count occurrences of each skill in the job description to establish internal demand
    lower_jd = job_description_text.lower()
    skill_weights = {}
    for s in required_skills:
        # Simple frequency heuristic within this specific job posting
        count = len(re.findall(rf"\b{re.escape(s.lower())}\b", lower_jd))
        skill_weights[s] = max(1, count)

    max_weight = max(skill_weights.values()) if skill_weights else 1

    tfidf_score = compute_tfidf_match_score(resume_text, job_description_text)
    set_coverage_score = compute_set_coverage_score(user_skills, required_skills)
    overall_match = round((0.60 * set_coverage_score) + (0.40 * tfidf_score), 1)

    user_set = set(user_skills)
    missing_skills = [s for s in required_skills if s not in user_set]
    matched_skills = [s for s in required_skills if s in user_set]
    category_breakdown = compute_category_breakdown(user_skills, required_skills, extractor)

    gap_records = []
    for skill in missing_skills:
        meta = extractor.get_skill_metadata(skill)
        # Normalized priority within this specific job posting
        rel_demand = round(skill_weights.get(skill, 1) / max_weight, 2)
        gap_records.append({
            "skill": skill,
            "category": meta.get("category", "Other"),
            "demand": rel_demand,
            "est_weeks_to_learn": int(meta.get("est_weeks_to_learn", 3)),
            "resource_url": str(meta.get("resource_url", "")),
            "resource_title": str(meta.get("resource_title", "")),
        })

    # Sort missing skills by internal job posting priority descending, then est_weeks ascending
    gap_records.sort(key=lambda x: (x["demand"], -x["est_weeks_to_learn"]), reverse=True)

    # Separate Technical vs Soft Skills for this custom job
    tech_matched = [s for s in matched_skills if extractor.get_skill_category(s) != "Soft Skills"]
    tech_total = [s for s in required_skills if extractor.get_skill_category(s) != "Soft Skills"]
    tech_cov = round((len(tech_matched) / len(tech_total)) * 100, 1) if tech_total else 0.0

    return {
        "target_role": "Custom Job Posting",
        "user_skills": user_skills,
        "matched_skills": matched_skills,
        "missing_skills": [g["skill"] for g in gap_records],
        "gap_list": gap_records,
        "tfidf_score": tfidf_score,
        "set_coverage_score": set_coverage_score,
        "overall_match_score": overall_match,
        "category_breakdown": category_breakdown,
        "total_role_skills": len(required_skills),
        "tech_coverage_pct": tech_cov,
        "demand_dict": skill_weights,
    }
