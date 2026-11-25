"""Unit tests for skill extraction, alias mapping, and boundary detection."""

import pytest
from src.skill_extract import SkillExtractor


@pytest.fixture(scope="module")
def extractor():
    return SkillExtractor()


def test_alias_resolution(extractor):
    """Verifies that common aliases map to canonical skill names."""
    text = "Proficient in nodejs, k8s, react.js, postgres, and sklearn."
    extracted = extractor.extract_skills(text)
    
    assert "Node.js" in extracted
    assert "Kubernetes" in extracted
    assert "React" in extracted
    assert "PostgreSQL" in extracted
    assert "Scikit-Learn" in extracted


def test_case_insensitivity(extractor):
    """Verifies case insensitivity across different casings."""
    text_upper = "EXPERIENCE WITH PYTHON, DOCKER, AND AWS."
    text_lower = "experience with python, docker, and aws."
    
    extracted_upper = extractor.extract_skills(text_upper)
    extracted_lower = extractor.extract_skills(text_lower)
    
    assert extracted_upper == extracted_lower
    assert "Python" in extracted_upper
    assert "Docker" in extracted_upper
    assert "AWS" in extracted_upper


def test_symbol_languages(extractor):
    """Verifies detection of symbols like C++ and C# without regex corruption."""
    text = "Developed low-latency services in C++ and desktop apps in C#."
    extracted = extractor.extract_skills(text)
    
    assert "C++" in extracted
    assert "C#" in extracted


def test_avoid_false_positive_common_words(extractor):
    """Ensures common conversational English words like 'go', 'next', 'it'

    do not trigger false skill matches when used in regular context.
    """
    text = "We will go to the office next week and do it carefully."
    extracted = extractor.extract_skills(text)
    
    # 'Go' language should not match lowercase conversational 'go to the office'
    assert "Go" not in extracted
    # 'Next.js' should not match standalone 'next week'
    assert "Next.js" not in extracted


def test_ambiguous_short_keywords_positive(extractor):
    """Verifies that Golang or explicit Go programming is detected accurately."""
    text = "Built backend microservices in Golang."
    extracted = extractor.extract_skills(text)
    assert "Go" in extracted
