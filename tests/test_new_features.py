"""Unit tests for advanced features:

- All-roles career leaderboard
- Peer percentile benchmarking (54k resume model)
- 12-week directed roadmap generator
- Action-verb bullet rewriter assistant (Google XYZ formula)
- Downloadable Markdown audit report generator
"""

import pytest
from src.bullet_rewriter import analyze_and_rewrite_bullets, identify_weak_bullets
from src.peer_benchmark import compute_peer_percentile
from src.pipeline import SkillBridgePipeline
from src.roadmap import generate_12_week_roadmap


@pytest.fixture(scope="module")
def pipeline():
    return SkillBridgePipeline()


def test_peer_percentile_calculation():
    """Verifies that peer percentile correctly scales with matched skill count."""
    low_match = compute_peer_percentile(matched_skills_count=2, role="Machine Learning Engineer")
    avg_match = compute_peer_percentile(matched_skills_count=5, role="Machine Learning Engineer")
    high_match = compute_peer_percentile(matched_skills_count=9, role="Machine Learning Engineer")

    assert low_match["percentile"] < avg_match["percentile"] < high_match["percentile"]
    assert 1.0 <= low_match["percentile"] <= 99.0
    assert 1.0 <= high_match["percentile"] <= 99.0
    assert "percentile" in high_match
    assert "standing" in high_match


def test_12_week_roadmap_generation():
    """Verifies that the sequential roadmap divides study into chronological phases."""
    sample_recs = [
        {"skill": "Docker", "category": "Cloud/DevOps", "est_weeks_to_learn": 2},
        {"skill": "AWS", "category": "Cloud/DevOps", "est_weeks_to_learn": 4},
        {"skill": "Kubernetes", "category": "Cloud/DevOps", "est_weeks_to_learn": 5},
    ]

    roadmap = generate_12_week_roadmap(sample_recs, "DevOps Engineer")

    assert len(roadmap["phases"]) == 3
    assert roadmap["phases"][0]["skill"] == "Docker"
    assert roadmap["phases"][1]["skill"] == "AWS"
    assert roadmap["phases"][2]["skill"] == "Kubernetes"
    assert "Weeks 1 - 2" in roadmap["phases"][0]["week_span"]
    assert len(roadmap["phases"][0]["milestones"]) >= 2


def test_bullet_rewriter_weak_detection_and_xyz_generation():
    """Verifies that passive bullets are flagged and XYZ rewrites are created."""
    sample_bullets = [
        "Responsible for handling customer database queries.",
        "Worked on machine learning model for prediction.",
        "Engineered REST APIs using FastAPI reducing latency by 30%.",  # Strong bullet
    ]

    weak = identify_weak_bullets(sample_bullets)
    # The first two are weak, the third is strong
    assert len(weak) == 2
    assert "Responsible for" in weak[0]["original_bullet"]

    rewrites = analyze_and_rewrite_bullets("\n".join(sample_bullets))
    assert len(rewrites) >= 1
    assert len(rewrites[0]["improved_options"]) == 3
    # Check that improved options start with an action verb
    assert any("Engineered" in opt or "Architected" in opt or "Automated" in opt for opt in rewrites[0]["improved_options"])


def test_multi_role_leaderboard_computation(pipeline):
    """Verifies that all 8 canonical roles are evaluated and sorted descending."""
    resume_text = "Proficient in JavaScript, TypeScript, React, HTML, CSS, Next.js, and Redux."
    leaderboard = pipeline.compute_all_roles_leaderboard(resume_text)

    assert len(leaderboard) == 8
    # Scores must be sorted descending
    for i in range(len(leaderboard) - 1):
        assert leaderboard[i]["overall_fit"] >= leaderboard[i + 1]["overall_fit"]

    # Frontend Developer should rank at or near the top
    top_role = leaderboard[0]["role"]
    assert top_role in ["Frontend Developer", "Full Stack Developer"]


def test_markdown_report_generation(pipeline):
    """Verifies that full analysis generates a valid non-empty markdown report."""
    resume_text = "Proficient in Python, SQL, Git, Linux, Pandas, and Scikit-Learn."
    res = pipeline.run_full_analysis(resume_text, target_role="Data Scientist")

    report = res["markdown_report"]
    assert isinstance(report, str)
    assert "# SkillBridge Career & Skill-Gap Audit Report" in report
    assert "Executive Summary" in report
    assert "Multi-Role Career Readiness Leaderboard" in report
    assert "12-Week Sequential Learning Roadmap" in report
