"""Rule-based Resume Bullet Rewriter Assistant for SkillBridge.

Transforms weak, passive resume bullet points into high-impact engineering statements
using Google's 'XYZ Formula': Accomplished [X], as measured by [Y], by doing [Z].
"""

import re
from typing import Dict, List, Optional

from src.config import ACTION_VERBS
from src.readability import extract_bullets_and_lines

# Patterns indicating passive or weak opening phrases
WEAK_OPENERS = [
    r"^(responsible for|was responsible for)\s+",
    r"^(worked on|helped with|helped to|assisted in|assisted with)\s+",
    r"^(involved in|participated in|tasked with|assigned to)\s+",
    r"^(handled|did|made|managed)\s+",
    r"^(had to|tried to|supported)\s+",
]


def identify_weak_bullets(bullets: List[str]) -> List[Dict[str, object]]:
    """Identifies bullet points that lack strong action verbs or quantitative metrics."""
    weak_records = []

    for b in bullets:
        clean = b.strip()
        if len(clean.split()) < 4:
            continue

        is_weak = False
        reasons = []

        # Check weak opening phrases
        for pat in WEAK_OPENERS:
            if re.search(pat, clean, re.IGNORECASE):
                is_weak = True
                reasons.append("Starts with passive/weak responsibility phrase.")
                break

        # Check if first word is an action verb
        tokens = re.findall(r"\b[A-Za-z]+\b", clean.lower())
        if tokens and tokens[0] not in ACTION_VERBS and not is_weak:
            reasons.append(f"Opening word '{tokens[0]}' is not an active past-tense engineering verb.")
            is_weak = True

        # Check for numbers or metrics
        has_metrics = bool(re.search(r"(\d+%|\d+x|\$\d+|\d+\+|\b\d{2,}\b)", clean))
        if not has_metrics:
            reasons.append("Lacks quantified results or measurable engineering metrics.")
            is_weak = True

        if is_weak:
            weak_records.append({
                "original_bullet": clean,
                "reasons": reasons,
                "has_metrics": has_metrics,
            })

    return weak_records


def generate_xyz_rewrites(bullet_text: str) -> List[str]:
    """Generates 3 tailored Google XYZ rewrite templates for a weak bullet."""
    # Strip common weak prefixes
    cleaned_clause = bullet_text
    for pat in WEAK_OPENERS:
        cleaned_clause = re.sub(pat, "", cleaned_clause, flags=re.IGNORECASE)

    cleaned_clause = cleaned_clause.rstrip(". ")
    first_char_lower = cleaned_clause[0].lower() + cleaned_clause[1:] if cleaned_clause else ""

    rewrites = [
        f"Engineered and deployed {first_char_lower}, improving system throughput by 25% and reducing processing turnaround.",
        f"Architected {first_char_lower} utilizing industry best practices, achieving a 30% reduction in latency and zero downtime.",
        f"Automated {first_char_lower}, eliminating repetitive manual tasks and accelerating workflow execution by 2.5x.",
    ]
    return rewrites


def analyze_and_rewrite_bullets(resume_text: str, max_suggestions: int = 4) -> List[Dict[str, object]]:
    """Finds weak bullets in a resume and generates high-impact action-oriented rewrites."""
    bullets = extract_bullets_and_lines(resume_text)
    weak_bullets = identify_weak_bullets(bullets)

    suggestions = []
    for item in weak_bullets[:max_suggestions]:
        original = item["original_bullet"]
        rewrites = generate_xyz_rewrites(original)
        suggestions.append({
            "original": original,
            "reasons": item["reasons"],
            "improved_options": rewrites,
        })

    return suggestions
