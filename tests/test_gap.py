"""Unit tests for match score, set coverage, and category breakdown."""

import pytest
from src.gap import (
    compute_category_breakdown,
    compute_gap_list,
    compute_set_coverage_score,
    compute_tfidf_match_score,
)
from src.skill_extract import SkillExtractor


@pytest.fixture(scope="module")
def extractor():
    return SkillExtractor()


def test_set_coverage_score_calculation():
    """Verifies deterministic set coverage computation."""
    user_skills = ["Python", "Scikit-Learn", "Docker"]
    role_high_demand = ["Python", "Scikit-Learn", "Docker", "PyTorch"]
    
    # 3 matched out of 4 = 75.0%
    score = compute_set_coverage_score(user_skills, role_high_demand)
    assert score == 75.0


def test_set_coverage_empty_cases():
    """Verifies edge cases with zero matches or empty lists."""
    assert compute_set_coverage_score([], ["Python", "Docker"]) == 0.0
    assert compute_set_coverage_score(["Python"], []) == 0.0


def test_tfidf_match_score_behavior():
    """Verifies TF-IDF similarity between text and corpus."""
    resume_text = "Proficient in Python machine learning model development and PyTorch neural networks."
    role_corpus = "Python Machine Learning PyTorch Scikit-Learn Docker AWS predictive modeling."
    unrelated_corpus = "Chef cooking gourmet culinary recipes food preparation dining."

    sim_high = compute_tfidf_match_score(resume_text, role_corpus)
    sim_low = compute_tfidf_match_score(resume_text, unrelated_corpus)

    assert sim_high > sim_low
    assert 0.0 <= sim_high <= 100.0


def test_category_breakdown_computation(extractor):
    """Verifies category breakdown math and grouping on a fixed sample."""
    user_skills = ["Python", "Docker"]
    role_high_demand = ["Python", "C++", "Docker", "Kubernetes"]

    breakdown = compute_category_breakdown(user_skills, role_high_demand, extractor)

    # In our skill_meta.csv:
    # Python, C++ are Languages
    # Docker, Kubernetes are Cloud/DevOps
    assert "Languages" in breakdown
    assert breakdown["Languages"]["total_required"] == 2
    assert breakdown["Languages"]["matched_count"] == 1
    assert breakdown["Languages"]["match_pct"] == 50.0

    assert "Cloud/DevOps" in breakdown
    assert breakdown["Cloud/DevOps"]["total_required"] == 2
    assert breakdown["Cloud/DevOps"]["matched_count"] == 1
    assert breakdown["Cloud/DevOps"]["match_pct"] == 50.0


def test_gap_list_sorting_by_demand(extractor):
    """Verifies that missing skills are ordered by demand descending."""
    user_skills = ["Python"]
    role_high_demand = ["Python", "Docker", "Kubernetes"]
    demand_dict = {"Python": 0.9, "Docker": 0.75, "Kubernetes": 0.50}

    gap_list = compute_gap_list(user_skills, role_high_demand, demand_dict, extractor)

    assert len(gap_list) == 2
    assert gap_list[0]["skill"] == "Docker"
    assert gap_list[1]["skill"] == "Kubernetes"
    assert gap_list[0]["demand"] >= gap_list[1]["demand"]
