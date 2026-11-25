"""Next-best-skill recommender module for SkillBridge.

Calculates multi-criteria ranking for missing skills using:
score = w1 * graph_connectivity + w2 * demand + w3 * ease

Where:
- graph_connectivity: sum of edge weights to skills the student already possesses (normalized to [0, 1])
- demand: fraction of postings requiring the skill (normalized to [0, 1])
- ease: 1 / (1 + est_weeks_to_learn / 4.0)

Generates explainable, deterministic natural language reasons for viva examination defense.
"""

from typing import Dict, List, Optional, Set, Tuple

import networkx as nx
import numpy as np

from src.config import (
    EASE_WEEKS_SCALE,
    WEIGHT_CONNECTIVITY,
    WEIGHT_DEMAND,
    WEIGHT_EASE,
)
from src.skill_extract import SkillExtractor


def compute_ease_score(est_weeks: float, scale: float = EASE_WEEKS_SCALE) -> float:
    """Computes ease-of-acquisition score: ease = 1 / (1 + est_weeks / scale).

    Lower estimated weeks yields a higher ease score in (0, 1].
    """
    weeks = max(1.0, float(est_weeks))
    return round(1.0 / (1.0 + (weeks / scale)), 4)


def compute_shortest_path_distance(G: nx.Graph, user_skills: List[str], target_skill: str) -> float:
    """Computes minimum unweighted shortest path distance from any user skill to target skill.

    Used as an objective tiebreaker for graph proximity.
    """
    if target_skill not in G:
        return 999.0

    valid_user_nodes = [s for s in user_skills if s in G]
    if not valid_user_nodes:
        return 999.0

    min_dist = 999.0
    for u in valid_user_nodes:
        try:
            dist = nx.shortest_path_length(G, source=u, target=target_skill)
            if dist < min_dist:
                min_dist = dist
        except nx.NetworkXNoPath:
            continue

    return float(min_dist)


def recommend_next_skills(
    user_skills: List[str],
    missing_skills: List[str],
    G: nx.Graph,
    demand_dict: Dict[str, float],
    extractor: SkillExtractor,
    w1: float = WEIGHT_CONNECTIVITY,
    w2: float = WEIGHT_DEMAND,
    w3: float = WEIGHT_EASE,
    top_k: int = 3,
) -> List[Dict[str, object]]:
    """Ranks missing skills and returns top recommendations with mathematical justification.

    Args:
        user_skills: Canonical skills the student already has.
        missing_skills: Gaps identified for the target role.
        G: NetworkX co-occurrence graph for the target role.
        demand_dict: Mapping of skill -> demand fraction.
        extractor: SkillExtractor instance.
        w1, w2, w3: Configurable weights (connectivity, demand, ease).
        top_k: Number of recommendations to return.

    Returns:
        List of ranked recommendation dicts.
    """
    if not missing_skills:
        return []

    user_skills_set = set(user_skills)
    user_nodes_in_graph = [s for s in user_skills if s in G]

    # 1. Compute raw values for all candidates
    raw_connectivity: Dict[str, float] = {}
    connected_known_skills: Dict[str, List[Tuple[str, int]]] = {}
    raw_demand: Dict[str, float] = {}
    raw_ease: Dict[str, float] = {}
    shortest_paths: Dict[str, float] = {}

    for skill in missing_skills:
        # Connectivity: sum of edge weights to student's known skills
        conn = 0
        connected = []
        if skill in G:
            for u in user_nodes_in_graph:
                if G.has_edge(skill, u):
                    weight = G[skill][u].get("weight", 1)
                    conn += weight
                    connected.append((u, weight))
            connected.sort(key=lambda x: x[1], reverse=True)
            sp_dist = compute_shortest_path_distance(G, user_skills, skill)
        else:
            sp_dist = 999.0

        raw_connectivity[skill] = float(conn)
        connected_known_skills[skill] = connected
        shortest_paths[skill] = sp_dist

        # Demand
        d = demand_dict.get(skill, 0.0)
        raw_demand[skill] = float(d)

        # Ease
        meta = extractor.get_skill_metadata(skill)
        est_weeks = meta.get("est_weeks_to_learn", 3)
        raw_ease[skill] = compute_ease_score(est_weeks)

    # 2. Normalize components to [0, 1]
    max_conn = max(raw_connectivity.values()) if raw_connectivity and max(raw_connectivity.values()) > 0 else 1.0
    max_dem = max(raw_demand.values()) if raw_demand and max(raw_demand.values()) > 0 else 1.0

    scored_candidates = []
    for skill in missing_skills:
        norm_conn = raw_connectivity[skill] / max_conn if max_conn > 0 else 0.0
        norm_dem = raw_demand[skill] / max_dem if max_dem > 0 else 0.0
        ease_val = raw_ease[skill]  # ease is already in (0, 1]

        final_score = (w1 * norm_conn) + (w2 * norm_dem) + (w3 * ease_val)
        meta = extractor.get_skill_metadata(skill)

        # Build natural language reason
        connected_list = connected_known_skills[skill]
        if connected_list:
            top_conn_names = [f"{name} ({wt})" for name, wt in connected_list[:2]]
            conn_phrase = f"Strongly bridges with your {', '.join(top_conn_names)}"
        else:
            conn_phrase = "Expands your core foundation"

        dem_pct = round(raw_demand[skill] * 100, 1)
        weeks = int(meta.get("est_weeks_to_learn", 3))
        reason = f"{conn_phrase}; appears in {dem_pct}% of postings; estimated {weeks} week{'s' if weeks > 1 else ''} to master."

        scored_candidates.append({
            "skill": skill,
            "category": meta.get("category", "Other"),
            "score": round(final_score, 4),
            "norm_connectivity": round(norm_conn, 3),
            "norm_demand": round(norm_dem, 3),
            "ease_score": round(ease_val, 3),
            "raw_connectivity": int(raw_connectivity[skill]),
            "demand": round(raw_demand[skill], 4),
            "est_weeks_to_learn": weeks,
            "shortest_path_dist": shortest_paths[skill],
            "connected_skills": connected_list,
            "reason": reason,
            "resource_url": str(meta.get("resource_url", "")),
            "resource_title": str(meta.get("resource_title", "")),
        })

    # Sort primarily by final score descending, secondarily by shortest path distance ascending (tiebreaker)
    scored_candidates.sort(key=lambda x: (x["score"], -x["shortest_path_dist"]), reverse=True)

    return scored_candidates[:top_k]
