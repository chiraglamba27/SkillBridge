"""Rule-based resume readability and ATS checker for SkillBridge.

Computes a deterministic score out of 100 with actionable feedback tips based on:
1. Standard CSE undergraduate section headers (Education, Skills, Projects, Experience).
2. Bullet length and density (flags overly verbose bullets > 25 words).
3. Action verb ratio (checks first word against 100+ curated engineering verbs).
4. Quantified metric density (numbers, %, latency, multipliers, financial values).
5. Passive voice detection (flags passive constructions like 'was developed by').
6. Page length and word count (flags resumes over standard single-page limit).
7. Contact info completeness (Email, Phone, LinkedIn/GitHub).
8. Buzzword & cliché detection (flags non-technical filler words).
"""

import re
from typing import Dict, List, Tuple

from src.config import (
    ACTION_VERBS,
    MAX_BULLET_WORDS,
    MAX_RESUME_WORDS,
    MIN_RESUME_WORDS,
    STANDARD_SECTIONS,
    TARGET_ACTION_VERB_RATIO,
    TARGET_QUANTIFIED_RATIO,
)

# Common filler buzzwords and clichés that weaken engineering resumes
RESUME_CLICHES = [
    "hard worker", "team player", "go-getter", "go getter", "detail oriented",
    "detail-oriented", "fast learner", "self-starter", "self starter",
    "think outside the box", "synergy", "results-driven", "results driven",
    "hard-working", "hardworking", "motivated individual", "passionate developer",
    "dynamic problem solver"
]


def extract_bullets_and_lines(text: str) -> List[str]:
    """Extracts bullet points or sentence-level achievement statements from resume text."""
    lines = text.splitlines()
    bullets = []
    
    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        # Check if line starts with common bullet markers
        bullet_match = re.match(r"^[\s*•\-\+>\u2022\u25E6\u2043\u2219]\s*(.+)$", clean)
        if bullet_match:
            bullets.append(bullet_match.group(1).strip())
        elif re.match(r"^\d+[\.\)]\s*(.+)$", clean):
            num_match = re.match(r"^\d+[\.\)]\s*(.+)$", clean)
            bullets.append(num_match.group(1).strip())
        elif len(clean.split()) >= 4 and not clean.endswith(":"):
            bullets.append(clean)
            
    return bullets


def check_standard_headers(text: str) -> Dict[str, object]:
    """Rule 1: Checks for standard undergraduate resume section headers. Worth 20 points."""
    lower_text = text.lower()
    found_sections = []
    missing_sections = []

    for section in STANDARD_SECTIONS:
        pattern = rf"(^|\n|\r)[#\*\s]*{re.escape(section)}[:\s]*(\n|\r|$)"
        if re.search(pattern, lower_text) or section in lower_text:
            found_sections.append(section.capitalize())
        else:
            missing_sections.append(section.capitalize())

    score = (len(found_sections) / len(STANDARD_SECTIONS)) * 20.0
    tips = []
    if missing_sections:
        tips.append(f"Add missing standard sections: {', '.join(missing_sections)}.")

    return {
        "rule": "Standard Section Headers",
        "score": round(score, 1),
        "max_score": 20.0,
        "found_sections": found_sections,
        "missing_sections": missing_sections,
        "tips": tips,
    }


def check_bullet_length(bullets: List[str]) -> Dict[str, object]:
    """Rule 2: Checks bullet density and flags overly long bullets (> 25 words). Worth 15 points."""
    if not bullets:
        return {
            "rule": "Bullet Length & Density",
            "score": 0.0,
            "max_score": 15.0,
            "long_bullets_count": 0,
            "total_bullets": 0,
            "avg_words_per_bullet": 0.0,
            "tips": ["Format your project and experience achievements into clear bullet points."],
        }

    word_counts = [len(b.split()) for b in bullets]
    avg_words = sum(word_counts) / len(word_counts)
    long_bullets = [b for b in bullets if len(b.split()) > MAX_BULLET_WORDS]

    long_fraction = len(long_bullets) / len(bullets)
    score = max(0.0, (1.0 - (long_fraction * 1.5)) * 15.0)

    tips = []
    if long_bullets:
        tips.append(
            f"{len(long_bullets)} bullet(s) exceed {MAX_BULLET_WORDS} words. Condense them to keep them punchy and scannable."
        )

    return {
        "rule": "Bullet Length & Density",
        "score": round(score, 1),
        "max_score": 15.0,
        "long_bullets_count": len(long_bullets),
        "total_bullets": len(bullets),
        "avg_words_per_bullet": round(avg_words, 1),
        "tips": tips,
    }


def check_action_verbs(bullets: List[str]) -> Dict[str, object]:
    """Rule 3: Checks share of bullets starting with a strong action verb. Worth 20 points."""
    if not bullets:
        return {
            "rule": "Action Verb Openers",
            "score": 0.0,
            "max_score": 20.0,
            "action_verb_bullets": 0,
            "action_verb_ratio": 0.0,
            "tips": ["Start each bullet with an active past-tense engineering verb (e.g., 'Engineered', 'Optimized')."],
        }

    action_bullet_count = 0
    for bullet in bullets:
        tokens = re.findall(r"\b[A-Za-z]+\b", bullet.lower())
        if tokens and tokens[0] in ACTION_VERBS:
            action_bullet_count += 1

    ratio = action_bullet_count / len(bullets)
    score = min(20.0, (ratio / TARGET_ACTION_VERB_RATIO) * 20.0)

    tips = []
    if ratio < TARGET_ACTION_VERB_RATIO:
        pct = round(ratio * 100, 1)
        tips.append(
            f"Only {pct}% of bullets start with a strong action verb. Aim for at least {int(TARGET_ACTION_VERB_RATIO*100)}% (e.g., 'Built', 'Deployed', 'Refactored')."
        )

    return {
        "rule": "Action Verb Openers",
        "score": round(score, 1),
        "max_score": 20.0,
        "action_verb_bullets": action_bullet_count,
        "action_verb_ratio": round(ratio, 2),
        "tips": tips,
    }


def check_quantified_results(bullets: List[str]) -> Dict[str, object]:
    """Rule 4: Detects quantified metrics and tangible impact results in bullets. Worth 20 points."""
    if not bullets:
        return {
            "rule": "Quantified Impact",
            "score": 0.0,
            "max_score": 20.0,
            "quantified_bullets": 0,
            "quantified_ratio": 0.0,
            "tips": ["Include quantitative metrics (e.g., 'reduced latency by 35%', 'served 10k+ requests')."],
        }

    metric_pattern = re.compile(
        r"(\b\d+(\.\d+)?%|\b\d+x\b|\$\d+[\d,]*|\b\d+\+?\s*(users|requests|queries|ms|seconds|fps|gb|mb|tb|stars)\b|\b\d{2,}\b)",
        re.IGNORECASE,
    )

    quantified_count = 0
    for bullet in bullets:
        if metric_pattern.search(bullet):
            quantified_count += 1

    ratio = quantified_count / len(bullets)
    score = min(20.0, (ratio / TARGET_QUANTIFIED_RATIO) * 20.0)

    tips = []
    if ratio < TARGET_QUANTIFIED_RATIO:
        pct = round(ratio * 100, 1)
        tips.append(
            f"Only {pct}% of bullets contain quantified metrics. Back up achievements with data (e.g., '% improvement', 'response times', 'data volume')."
        )

    return {
        "rule": "Quantified Impact",
        "score": round(score, 1),
        "max_score": 20.0,
        "quantified_bullets": quantified_count,
        "quantified_ratio": round(ratio, 2),
        "tips": tips,
    }


def check_passive_voice(text: str) -> Dict[str, object]:
    """Rule 5: Detects passive voice constructions (e.g. 'was developed by'). Worth 15 points."""
    passive_patterns = [
        r"\b(was|were|is|are|been|being)\s+([a-z]+ed)\s+(by|for)\b",
        r"\bwas\s+(responsible\s+for|assigned\s+to|tasked\s+with)\b",
        r"\bwere\s+(implemented|handled|managed|used)\s+by\b",
    ]

    found_instances = []
    for pat in passive_patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        for m in matches:
            if isinstance(m, tuple):
                found_instances.append(" ".join(m))
            else:
                found_instances.append(m)

    penalty = min(15.0, len(found_instances) * 3.0)
    score = 15.0 - penalty

    tips = []
    if found_instances:
        sample = found_instances[0]
        tips.append(
            f"Detected {len(found_instances)} passive voice phrase(s) (e.g., '{sample}'). Rewrite in active voice: 'I engineered X' instead of 'X was engineered by me'."
        )

    return {
        "rule": "Active Voice vs Passive Voice",
        "score": round(score, 1),
        "max_score": 15.0,
        "passive_instances_count": len(found_instances),
        "tips": tips,
    }


def check_resume_length(text: str) -> Dict[str, object]:
    """Rule 6: Checks overall word count against standard 1-page undergraduate guidelines. Worth 10 points."""
    words = len(text.split())
    tips = []

    if words < MIN_RESUME_WORDS:
        score = max(2.0, (words / MIN_RESUME_WORDS) * 10.0)
        tips.append(
            f"Resume is very brief ({words} words). Add detailed project descriptions, tech stacks, and quantified outcomes to reach ~400-600 words."
        )
    elif words > MAX_RESUME_WORDS:
        excess = words - MAX_RESUME_WORDS
        score = max(3.0, 10.0 - (excess / 100.0) * 2.0)
        tips.append(
            f"Resume exceeds standard 1-page length ({words} words). Trim wordy descriptions down to under {MAX_RESUME_WORDS} words."
        )
    else:
        score = 10.0

    return {
        "rule": "Resume Length & Page Economy",
        "score": round(score, 1),
        "max_score": 10.0,
        "word_count": words,
        "tips": tips,
    }


def check_contact_info(text: str) -> Dict[str, object]:
    """Rule 7: Diagnostics for essential contact links (Email, Phone, GitHub/LinkedIn)."""
    has_email = bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text))
    has_phone = bool(re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text))
    has_github = bool(re.search(r"(github\.com/[A-Za-z0-9_-]+|github)", text, re.IGNORECASE))
    has_linkedin = bool(re.search(r"(linkedin\.com/in/[A-Za-z0-9_-]+|linkedin)", text, re.IGNORECASE))

    found = []
    missing = []
    if has_email: found.append("Email")
    else: missing.append("Email")

    if has_phone: found.append("Phone")
    else: missing.append("Phone Number")

    if has_github: found.append("GitHub")
    else: missing.append("GitHub Profile")

    if has_linkedin: found.append("LinkedIn")
    else: missing.append("LinkedIn Profile")

    tips = []
    if missing:
        tips.append(f"ATS Missing Contact Info: Add {', '.join(missing)} in the header so recruiters can reach you.")

    return {
        "rule": "Contact Info & Links",
        "found": found,
        "missing": missing,
        "complete": len(missing) == 0,
        "tips": tips,
    }


def check_cliches_and_buzzwords(text: str) -> Dict[str, object]:
    """Rule 8: Diagnostics for hollow non-technical buzzwords and clichés."""
    found_cliches = []
    lower_text = text.lower()
    for cliche in RESUME_CLICHES:
        if re.search(rf"\b{re.escape(cliche)}\b", lower_text):
            found_cliches.append(cliche)

    tips = []
    if found_cliches:
        tips.append(
            f"Remove generic buzzwords: '{', '.join(found_cliches[:3])}'. Replace with concrete technical achievements and metrics."
        )

    return {
        "rule": "Buzzword & Cliché Check",
        "found_cliches": found_cliches,
        "has_cliches": len(found_cliches) > 0,
        "tips": tips,
    }


def score_resume_readability(text: str) -> Dict[str, object]:
    """Computes overall resume readability score out of 100 with comprehensive breakdown."""
    bullets = extract_bullets_and_lines(text)

    r1 = check_standard_headers(text)
    r2 = check_bullet_length(bullets)
    r3 = check_action_verbs(bullets)
    r4 = check_quantified_results(bullets)
    r5 = check_passive_voice(text)
    r6 = check_resume_length(text)

    # Diagnostic rules
    r7 = check_contact_info(text)
    r8 = check_cliches_and_buzzwords(text)

    rule_results = [r1, r2, r3, r4, r5, r6]
    total_score = sum(r["score"] for r in rule_results)
    total_score = round(max(0.0, min(100.0, total_score)), 1)

    # Collect and prioritize tips
    all_tips = []
    for r in rule_results + [r7, r8]:
        all_tips.extend(r.get("tips", []))

    if not all_tips:
        all_tips.append("Excellent resume formatting! Clear sections, active verbs, and quantified outcomes.")

    return {
        "readability_score": total_score,
        "total_bullets": len(bullets),
        "word_count": r6["word_count"],
        "rules": {
            "headers": r1,
            "bullet_length": r2,
            "action_verbs": r3,
            "quantified_metrics": r4,
            "passive_voice": r5,
            "length": r6,
            "contact_info": r7,
            "buzzwords": r8,
        },
        "tips": all_tips,
    }
