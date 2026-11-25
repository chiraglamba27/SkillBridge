"""Demand calculation module for SkillBridge.

Computes the frequency and demand (fraction of job postings mentioning each skill)
per canonical role and globally across all roles.
"""

from typing import Dict, List, Optional
import pandas as pd

from src.config import DEMAND_THRESHOLD, ROLE_DEMAND_CSV
from src.skill_extract import SkillExtractor


def compute_role_demand(job_skills_df: pd.DataFrame) -> pd.DataFrame:
    """Computes demand fraction for each skill per role.

    Demand = (Count of postings mentioning skill in role) / (Total postings for role)

    Returns:
        DataFrame with columns: [role, skill, count, total_postings, demand, category]
    """
    extractor = SkillExtractor()
    records = []

    for role, group in job_skills_df.groupby("role"):
        total_postings = len(group)
        if total_postings == 0:
            continue

        skill_counts: Dict[str, int] = {}
        for skills in group["skills"]:
            for skill in skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1

        for skill, count in skill_counts.items():
            demand = count / total_postings
            category = extractor.get_skill_category(skill)
            records.append({
                "role": role,
                "skill": skill,
                "count": count,
                "total_postings": total_postings,
                "demand": round(demand, 4),
                "category": category,
            })

    demand_df = pd.DataFrame(records)
    if not demand_df.empty:
        demand_df = demand_df.sort_values(by=["role", "demand"], ascending=[True, False])
        demand_df.to_csv(ROLE_DEMAND_CSV, index=False)
    return demand_df


def get_role_demand_dict(demand_df: pd.DataFrame, role: str) -> Dict[str, float]:
    """Returns a dictionary of {skill: demand_fraction} for a specific role."""
    role_df = demand_df[demand_df["role"] == role]
    return dict(zip(role_df["skill"], role_df["demand"]))


def get_high_demand_skills(demand_df: pd.DataFrame, role: str, threshold: float = DEMAND_THRESHOLD) -> List[str]:
    """Returns a list of skills for the role with demand >= threshold."""
    role_df = demand_df[(demand_df["role"] == role) & (demand_df["demand"] >= threshold)]
    return role_df.sort_values(by="demand", ascending=False)["skill"].tolist()
