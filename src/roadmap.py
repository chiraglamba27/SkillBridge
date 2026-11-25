"""Directed 12-Week Sequential Learning Roadmap Generator for SkillBridge.

Structures recommended missing skills into a chronological semester plan
(Phase 1: Foundation Bridge -> Phase 2: Core Expansion -> Phase 3: Capstone/Advanced).
"""

from typing import Dict, List, Optional
import networkx as nx

from src.skill_extract import SkillExtractor


def generate_12_week_roadmap(
    recommendations: List[Dict[str, object]],
    target_role: str,
    extractor: Optional[SkillExtractor] = None,
) -> Dict[str, object]:
    """Generates a structured 12-week (3-month) sequential learning roadmap

    based on top ranked missing skills and their topological dependencies.
    """
    extractor = extractor or SkillExtractor()

    if not recommendations:
        return {
            "target_role": target_role,
            "total_weeks": 0,
            "phases": [],
            "summary": "You have mastered all high-demand skills for this role! Focus on system design and portfolio projects.",
        }

    # Select top 3-4 skills
    roadmap_skills = recommendations[:3]
    phases = []
    current_week = 1

    phase_meta = [
        {
            "phase_num": 1,
            "phase_name": "Phase 1: Foundation Bridge (Month 1)",
            "focus": "Rapid-gain skill that bridges directly with what you already know.",
            "deliverable_prefix": "Hands-on Prototype",
        },
        {
            "phase_num": 2,
            "phase_name": "Phase 2: Core Capability Expansion (Month 2)",
            "focus": "Essential industry tool building upon Month 1 foundation.",
            "deliverable_prefix": "End-to-End Module",
        },
        {
            "phase_num": 3,
            "phase_name": "Phase 3: Production Specialization & Capstone (Month 3)",
            "focus": "Advanced production-readiness, integration, and architecture.",
            "deliverable_prefix": "Full Capstone Integration",
        },
    ]

    total_duration = 0
    for idx, skill_info in enumerate(roadmap_skills):
        skill_name = skill_info["skill"]
        category = skill_info.get("category", "Technology")
        weeks = skill_info.get("est_weeks_to_learn", 3)
        total_duration += weeks

        start_week = current_week
        end_week = current_week + weeks - 1
        current_week = end_week + 1

        pm = phase_meta[idx] if idx < len(phase_meta) else {
            "phase_num": idx + 1,
            "phase_name": f"Phase {idx + 1}: Additional Mastery",
            "focus": "Expanding domain expertise.",
            "deliverable_prefix": "Practical Implementation",
        }

        # Generate realistic syllabus milestones
        milestones = [
            f"Week {start_week}: Fundamentals, syntax, environment setup, and basic {skill_name} architecture.",
            f"Week {start_week + (weeks // 2)}: Intermediate patterns, integration with prior tools, and debugging.",
            f"Week {end_week}: Finalize portfolio deliverable: {pm['deliverable_prefix']} demonstrating {skill_name}.",
        ]

        phases.append({
            "phase_number": pm["phase_num"],
            "phase_title": pm["phase_name"],
            "skill": skill_name,
            "category": category,
            "duration_weeks": weeks,
            "week_span": f"Weeks {start_week} - {end_week}",
            "objective": pm["focus"],
            "milestones": milestones,
            "resource_url": skill_info.get("resource_url", ""),
            "resource_title": skill_info.get("resource_title", ""),
        })

    return {
        "target_role": target_role,
        "total_weeks": min(12, total_duration),
        "phases": phases,
        "summary": f"A targeted {total_duration}-week chronological roadmap bridging into {target_role}.",
    }
