"""Co-occurrence graph builder for SkillBridge.

Constructs an undirected NetworkX graph per target role where:
- Nodes represent canonical skills.
- Node attributes include demand fraction, category, estimated weeks to learn, and centrality.
- Edges represent skill co-occurrence across job postings with edge weights = co-occurrence count.
- Edges below MIN_EDGE_WEIGHT are pruned to eliminate noise.
"""

from collections import defaultdict
import itertools
from pathlib import Path
import pickle
from typing import Dict, List, Optional, Tuple

import networkx as nx
import pandas as pd

from src.config import (
    GRAPH_FILE_TEMPLATE,
    JOB_SKILLS_PARQUET,
    MIN_EDGE_WEIGHT,
    PROCESSED_DATA_DIR,
    TARGET_ROLES,
)
from src.demand import compute_role_demand, get_role_demand_dict
from src.skill_extract import SkillExtractor


def build_role_graph(
    role: str,
    job_skills_df: pd.DataFrame,
    demand_dict: Dict[str, float],
    extractor: SkillExtractor,
    min_edge_weight: int = MIN_EDGE_WEIGHT,
) -> nx.Graph:
    """Constructs an undirected NetworkX co-occurrence graph for a given role.

    Args:
        role: Target role name.
        job_skills_df: Processed DataFrame containing 'role' and 'skills' (list of str).
        demand_dict: Mapping of skill -> demand fraction for this role.
        extractor: SkillExtractor instance for metadata lookup.
        min_edge_weight: Minimum co-occurrences required to include an edge.

    Returns:
        nx.Graph with node & edge attributes.
    """
    G = nx.Graph(role=role)
    role_df = job_skills_df[job_skills_df["role"] == role]
    total_postings = len(role_df)

    if total_postings == 0:
        return G

    # 1. Count co-occurrences
    co_occurrences: Dict[Tuple[str, str], int] = defaultdict(int)
    skill_counts: Dict[str, int] = defaultdict(int)

    for skills in role_df["skills"]:
        unique_skills = sorted(list(set(skills)))
        for s in unique_skills:
            skill_counts[s] += 1
        for s1, s2 in itertools.combinations(unique_skills, 2):
            co_occurrences[(s1, s2)] += 1

    # 2. Add nodes with metadata
    for skill, count in skill_counts.items():
        meta = extractor.get_skill_metadata(skill)
        demand = demand_dict.get(skill, count / total_postings)
        G.add_node(
            skill,
            demand=round(demand, 4),
            count=count,
            category=meta.get("category", "Other"),
            est_weeks_to_learn=int(meta.get("est_weeks_to_learn", 3)),
            resource_url=str(meta.get("resource_url", "")),
            resource_title=str(meta.get("resource_title", "")),
        )

    # 3. Add edges with weights above threshold
    for (s1, s2), weight in co_occurrences.items():
        if weight >= min_edge_weight:
            G.add_edge(s1, s2, weight=weight)

    # 4. Compute graph centralities
    if len(G) > 0:
        deg_centrality = nx.degree_centrality(G)
        bet_centrality = nx.betweenness_centrality(G, weight="weight")
        for node in G.nodes():
            G.nodes[node]["degree_centrality"] = round(deg_centrality.get(node, 0.0), 4)
            G.nodes[node]["betweenness_centrality"] = round(bet_centrality.get(node, 0.0), 4)

    return G


def save_graph(G: nx.Graph, role: str) -> Path:
    """Saves a NetworkX graph to pickle format."""
    clean_role = role.lower().replace(" ", "_")
    output_path = PROCESSED_DATA_DIR / f"graph_{clean_role}.gpickle"
    with open(output_path, "wb") as f:
        pickle.dump(G, f)
    return output_path


def load_graph(role: str) -> Optional[nx.Graph]:
    """Loads a saved NetworkX graph for a given role."""
    clean_role = role.lower().replace(" ", "_")
    graph_path = PROCESSED_DATA_DIR / f"graph_{clean_role}.gpickle"
    if not graph_path.exists():
        return None
    with open(graph_path, "rb") as f:
        return pickle.load(f)


def get_top_neighbors(G: nx.Graph, skill: str, top_n: int = 10) -> List[Tuple[str, int]]:
    """Returns top co-occurring neighbor skills sorted by edge weight descending."""
    if skill not in G:
        return []
    neighbors = []
    for neighbor in G.neighbors(skill):
        weight = G[skill][neighbor].get("weight", 1)
        neighbors.append((neighbor, weight))
    return sorted(neighbors, key=lambda x: x[1], reverse=True)[:top_n]


def build_and_save_all_graphs(job_skills_df: Optional[pd.DataFrame] = None) -> Dict[str, nx.Graph]:
    """Builds and serializes co-occurrence graphs for all target roles."""
    if job_skills_df is None:
        if JOB_SKILLS_PARQUET.exists():
            try:
                job_skills_df = pd.read_parquet(JOB_SKILLS_PARQUET)
            except Exception:
                job_skills_df = None
        if job_skills_df is None and JOB_SKILLS_CSV.exists():
            job_skills_df = pd.read_csv(JOB_SKILLS_CSV)
            if "skills" in job_skills_df.columns and len(job_skills_df) > 0 and isinstance(job_skills_df["skills"].iloc[0], str):
                import json
                job_skills_df["skills"] = job_skills_df["skills"].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
        if job_skills_df is None:
            raise FileNotFoundError(f"Missing {JOB_SKILLS_CSV}. Run ingest.py first.")

    extractor = SkillExtractor()
    demand_df = compute_role_demand(job_skills_df)
    graphs: Dict[str, nx.Graph] = {}

    print("\n[GraphBuilder] Building co-occurrence graphs...")
    for role in TARGET_ROLES:
        demand_dict = get_role_demand_dict(demand_df, role)
        G = build_role_graph(role, job_skills_df, demand_dict, extractor)
        save_graph(G, role)
        graphs[role] = G
        print(f"  - {role:<26}: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    return graphs


def run_phase2_acceptance() -> None:
    """Phase 2 Acceptance Verification:

    Prints top co-occurring neighbors for 'React' (e.g. in Frontend Developer role)
    and 'Docker' (e.g. in DevOps / Backend / Machine Learning roles).
    """
    graphs = build_and_save_all_graphs()

    print("\n" + "=" * 60)
    print("PHASE 2 ACCEPTANCE: CO-OCCURRENCE NEIGHBORS")
    print("=" * 60)

    # 1. Top neighbors for React in Frontend Developer
    frontend_g = graphs.get("Frontend Developer")
    if frontend_g and "React" in frontend_g:
        print("\nTop Co-occurring Neighbors for 'React' (Frontend Developer):")
        for neighbor, weight in get_top_neighbors(frontend_g, "React", top_n=10):
            print(f"  - {neighbor:<22} : {weight} co-occurrences")
    else:
        print("React not present in Frontend graph.")

    # 2. Top neighbors for Docker in DevOps Engineer
    devops_g = graphs.get("DevOps Engineer")
    if devops_g and "Docker" in devops_g:
        print("\nTop Co-occurring Neighbors for 'Docker' (DevOps Engineer):")
        for neighbor, weight in get_top_neighbors(devops_g, "Docker", top_n=10):
            print(f"  - {neighbor:<22} : {weight} co-occurrences")

    # 3. Top neighbors for Docker in Machine Learning Engineer
    ml_g = graphs.get("Machine Learning Engineer")
    if ml_g and "Docker" in ml_g:
        print("\nTop Co-occurring Neighbors for 'Docker' (Machine Learning Engineer):")
        for neighbor, weight in get_top_neighbors(ml_g, "Docker", top_n=10):
            print(f"  - {neighbor:<22} : {weight} co-occurrences")


if __name__ == "__main__":
    run_phase2_acceptance()
