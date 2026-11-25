"""Unit tests for next-best-skill recommendation and ranking determinism."""

import networkx as nx
import pytest
from src.recommend import (
    compute_ease_score,
    compute_shortest_path_distance,
    recommend_next_skills,
)
from src.skill_extract import SkillExtractor


@pytest.fixture(scope="module")
def extractor():
    return SkillExtractor()


@pytest.fixture
def sample_graph():
    """Creates a deterministic synthetic test graph."""
    G = nx.Graph()
    # User knows: Python, Git
    # Missing candidates: Docker, PyTorch, C++
    G.add_node("Python", demand=0.9, est_weeks_to_learn=4)
    G.add_node("Git", demand=0.7, est_weeks_to_learn=1)
    G.add_node("Docker", demand=0.8, est_weeks_to_learn=2)
    G.add_node("PyTorch", demand=0.6, est_weeks_to_learn=5)
    G.add_node("C++", demand=0.4, est_weeks_to_learn=8)

    # Edge weights
    # Python - Docker: 10
    # Git - Docker: 8  => Docker total connectivity = 18
    # Python - PyTorch: 6 => PyTorch total connectivity = 6
    # Python - C++: 1 => C++ total connectivity = 1
    G.add_edge("Python", "Docker", weight=10)
    G.add_edge("Git", "Docker", weight=8)
    G.add_edge("Python", "PyTorch", weight=6)
    G.add_edge("Python", "C++", weight=1)

    return G


def test_ease_score_monotonicity():
    """Verifies that fewer weeks to learn produces higher ease score."""
    ease_1_week = compute_ease_score(1)
    ease_4_weeks = compute_ease_score(4)
    ease_8_weeks = compute_ease_score(8)

    assert ease_1_week > ease_4_weeks > ease_8_weeks


def test_shortest_path_calculation(sample_graph):
    """Verifies shortest path distance logic."""
    user_skills = ["Python"]
    # Direct edge Python - PyTorch => distance 1
    dist_pytorch = compute_shortest_path_distance(sample_graph, user_skills, "PyTorch")
    assert dist_pytorch == 1.0


def test_recommendation_ranking_determinism(sample_graph, extractor):
    """Verifies that given a fixed user profile and graph, recommendations are 100% deterministic

    and Docker ranks #1 due to strong connectivity, high demand, and short learning time.
    """
    user_skills = ["Python", "Git"]
    missing_skills = ["Docker", "PyTorch", "C++"]
    demand_dict = {"Docker": 0.8, "PyTorch": 0.6, "C++": 0.4}

    # Run twice to test determinism
    rec1 = recommend_next_skills(
        user_skills, missing_skills, sample_graph, demand_dict, extractor, top_k=3
    )
    rec2 = recommend_next_skills(
        user_skills, missing_skills, sample_graph, demand_dict, extractor, top_k=3
    )

    assert len(rec1) == 3
    assert [r["skill"] for r in rec1] == [r["skill"] for r in rec2]

    # Docker must be #1
    top_skill = rec1[0]
    assert top_skill["skill"] == "Docker"
    assert top_skill["score"] >= rec1[1]["score"]

    # Reason string is populated with real numbers
    assert "Docker" in top_skill["skill"]
    assert "weeks" in top_skill["reason"]
    assert str(int(top_skill["demand"] * 100)) in top_skill["reason"]
