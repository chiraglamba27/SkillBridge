"""Learning resource lookup and graph community detection module for SkillBridge.

Provides:
1. Free, verified learning resources and documentation for recommended skills.
2. Louvain / modularity community detection to discover 'career archetypes' on skill graphs.
"""

from pathlib import Path
from typing import Dict, List, Optional

import networkx as nx
import pandas as pd

from src.config import SKILL_META_PATH
from src.skill_extract import SkillExtractor

# Additional verified free platforms mapping
COMPANION_RESOURCES = {
    "Python": [
        {"title": "Automate the Boring Stuff with Python", "url": "https://automatetheboringstuff.com/"},
        {"title": "FreeCodeCamp Scientific Computing with Python", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/"},
    ],
    "SQL": [
        {"title": "Select Star SQL Interactive Course", "url": "https://selectstarsql.com/"},
        {"title": "Mode Analytics SQL Tutorial", "url": "https://mode.com/sql-tutorial/"},
    ],
    "Docker": [
        {"title": "Docker Labs Beginners Guide", "url": "https://docker-curriculum.com/"},
        {"title": "Play with Docker Interactive Classroom", "url": "https://labs.play-with-docker.com/"},
    ],
    "Kubernetes": [
        {"title": "Kubernetes The Hard Way by Kelsey Hightower", "url": "https://github.com/kelseyhightower/kubernetes-the-hard-way"},
        {"title": "Kubernetes Official Interactive Tutorials", "url": "https://kubernetes.io/docs/tutorials/"},
    ],
    "React": [
        {"title": "FreeCodeCamp Front End Development Libraries", "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/"},
        {"title": "Scrimba Free React Course", "url": "https://scrimba.com/learn/learnreact"},
    ],
    "Machine Learning": [
        {"title": "Google Machine Learning Crash Course", "url": "https://developers.google.com/machine-learning/crash-course"},
        {"title": "Fast.ai Practical Deep Learning for Coders", "url": "https://course.fast.ai/"},
    ],
    "Git": [
        {"title": "Learn Git Branching Interactive Game", "url": "https://learngitbranching.js.org/"},
        {"title": "GitHub Skills Interactive Modules", "url": "https://skills.github.com/"},
    ],
    "Linux": [
        {"title": "OverTheWire Bandit Wargame for Linux CLI", "url": "https://overthewire.org/wargames/bandit/"},
        {"title": "The Linux Command Line Free Book", "url": "https://linuxcommand.org/tlcl.php"},
    ],
}


def get_skill_resources(skill: str, extractor: Optional[SkillExtractor] = None) -> List[Dict[str, str]]:
    """Returns 2-3 verified free learning resource links for a canonical skill.

    Only verified, working documentation links are returned (never synthetic URLs).
    """
    extractor = extractor or SkillExtractor()
    meta = extractor.get_skill_metadata(skill)
    resources = []

    primary_url = meta.get("resource_url", "")
    primary_title = meta.get("resource_title", "")

    if primary_url and primary_title:
        resources.append({"title": primary_title, "url": primary_url})

    # Add companion verified links if available
    if skill in COMPANION_RESOURCES:
        for comp in COMPANION_RESOURCES[skill]:
            if comp not in resources and len(resources) < 3:
                resources.append(comp)

    return resources


def get_learning_resources_for_skills(
    skills: List[str],
    extractor: Optional[SkillExtractor] = None,
) -> Dict[str, List[Dict[str, str]]]:
    """Returns resource lists for multiple skills."""
    extractor = extractor or SkillExtractor()
    return {s: get_skill_resources(s, extractor) for s in skills}


def detect_career_archetypes(G: nx.Graph) -> List[Dict[str, object]]:
    """Stretch Goal: Performs Louvain / Modularity Community Detection on the skill graph

    to discover natural skill clusters ('career archetypes').
    """
    if len(G) < 3:
        return []

    try:
        # Use NetworkX greedy modularity communities or louvain
        if hasattr(nx.community, "louvain_communities"):
            communities = nx.community.louvain_communities(G, weight="weight", seed=42)
        else:
            communities = nx.community.greedy_modularity_communities(G, weight="weight")
    except Exception:
        return []

    archetypes = []
    for idx, comm in enumerate(communities, 1):
        comm_nodes = list(comm)
        # Sort nodes by degree within community
        comm_nodes.sort(key=lambda n: G.degree(n, weight="weight"), reverse=True)
        top_skills = comm_nodes[:6]
        archetypes.append({
            "archetype_id": idx,
            "core_skills": top_skills,
            "total_skills_count": len(comm_nodes),
            "label": f"Cluster {idx}: {', '.join(top_skills[:3])}",
        })

    return archetypes
