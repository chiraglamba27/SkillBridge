"""Unit tests for each individual resume readability rule."""

import pytest
from src.readability import (
    check_action_verbs,
    check_bullet_length,
    check_passive_voice,
    check_quantified_results,
    check_resume_length,
    check_standard_headers,
    score_resume_readability,
)


def test_standard_headers_detection():
    """Rule 1: Standard section headers detection."""
    text_complete = """
    EDUCATION
    B.Tech in Computer Science
    
    SKILLS
    Python, SQL, Docker
    
    PROJECTS
    Portfolio Website
    
    EXPERIENCE
    Software Engineering Intern
    """
    res = check_standard_headers(text_complete)
    assert res["score"] == 20.0
    assert len(res["missing_sections"]) == 0

    text_missing = "EDUCATION: B.Tech. SKILLS: Python."
    res_missing = check_standard_headers(text_missing)
    assert res_missing["score"] < 20.0
    assert "Projects" in res_missing["missing_sections"]


def test_bullet_length_rule():
    """Rule 2: Flagging bullets exceeding MAX_BULLET_WORDS."""
    short_bullets = [
        "Engineered RESTful microservices with FastAPI and Docker.",
        "Optimized PostgreSQL queries decreasing latency by 20%.",
    ]
    res_good = check_bullet_length(short_bullets)
    assert res_good["long_bullets_count"] == 0
    assert res_good["score"] == 15.0

    long_bullets = [
        "This is an extremely long, rambling, verbose bullet point that goes on and on without any punctuation or structure and continues to add more and more words beyond twenty-five words to deliberately test the length checker rule."
    ]
    res_bad = check_bullet_length(long_bullets)
    assert res_bad["long_bullets_count"] == 1
    assert res_bad["score"] < 15.0


def test_action_verbs_rule():
    """Rule 3: Action verb detection at start of bullets."""
    good_bullets = [
        "Built predictive machine learning models in Python.",
        "Engineered scalable data pipelines using Apache Kafka.",
        "Refactored legacy code reducing technical debt.",
    ]
    res = check_action_verbs(good_bullets)
    assert res["action_verb_ratio"] == 1.0
    assert res["score"] == 20.0

    passive_bullets = [
        "Responsible for handling customer database queries.",
        "Was part of a team working on web interfaces.",
    ]
    res_passive = check_action_verbs(passive_bullets)
    assert res_passive["action_verb_ratio"] == 0.0
    assert res_passive["score"] == 0.0


def test_quantified_results_rule():
    """Rule 4: Quantified results detection."""
    quantified_bullets = [
        "Increased inference throughput by 45% using PyTorch and TensorRT.",
        "Served 20k+ daily active users with 99.9% uptime.",
    ]
    res = check_quantified_results(quantified_bullets)
    assert res["quantified_bullets"] == 2
    assert res["score"] == 20.0

    unquantified_bullets = [
        "Worked on various database optimizations and helped improve things.",
    ]
    res_none = check_quantified_results(unquantified_bullets)
    assert res_none["quantified_bullets"] == 0
    assert res_none["score"] == 0.0


def test_passive_voice_rule():
    """Rule 5: Detection of passive voice constructions."""
    active_text = "I architected the backend and deployed containerized services."
    res_active = check_passive_voice(active_text)
    assert res_active["passive_instances_count"] == 0
    assert res_active["score"] == 15.0

    passive_text = "The application was developed by me and bugs were handled by the team."
    res_passive = check_passive_voice(passive_text)
    assert res_passive["passive_instances_count"] >= 2
    assert res_passive["score"] < 15.0


def test_resume_length_rule():
    """Rule 6: Word count economic scaling."""
    # Ideal length: 400 words
    ideal_text = " ".join(["word"] * 450)
    res_ideal = check_resume_length(ideal_text)
    assert res_ideal["score"] == 10.0

    # Too brief
    short_text = "A quick resume with ten words only."
    res_short = check_resume_length(short_text)
    assert res_short["score"] < 10.0

    # Too long (> 800 words)
    long_text = " ".join(["word"] * 950)
    res_long = check_resume_length(long_text)
    assert res_long["score"] < 10.0


def test_overall_readability_composite_score():
    """Verifies that composite score is bounded in [0, 100]."""
    sample_resume = """
    EDUCATION
    B.Tech Computer Science, 2021-2025

    SKILLS
    Python, SQL, Git, Linux

    PROJECTS
    - Engineered automated test suite achieving 92% coverage.
    - Built responsive web dashboard serving 500+ daily users.

    EXPERIENCE
    Software Engineering Intern
    - Refactored database schema reducing query latency by 30%.
    - Collaborated with 5 engineers in Agile sprints.
    """
    report = score_resume_readability(sample_resume)
    assert 0.0 <= report["readability_score"] <= 100.0
    assert isinstance(report["tips"], list)
