"""Executive Report Generator for SkillBridge.

Generates both clean Markdown and self-contained, publication-quality printable HTML
audit reports with embedded styling, charts summary, and career action plans.
"""

from datetime import datetime
from typing import Dict, List, Optional


def generate_html_report(
    target_role: str,
    gap_results: Dict[str, object],
    recommendations: List[Dict[str, object]],
    readability: Dict[str, object],
    peer_benchmark: Dict[str, object],
    roadmap: Dict[str, object],
    leaderboard: List[Dict[str, object]],
) -> str:
    """Generates a standalone, beautiful HTML report with print-optimized CSS

    allowing one-click 'Print to PDF' directly from any web browser.
    """
    timestamp = datetime.now().strftime("%B %d, %Y - %H:%M")
    top_rec = recommendations[0] if recommendations else None

    # Rows for leaderboard
    leaderboard_rows = ""
    for rank, item in enumerate(leaderboard[:5], 1):
        bg = "#F8FAFC" if rank % 2 == 0 else "#FFFFFF"
        skills_str = ", ".join(item.get("matched_skills", [])[:4]) or "None"
        leaderboard_rows += f"""
        <tr style="background-color: {bg}; border-bottom: 1px solid #E2E8F0;">
            <td style="padding: 10px 14px; font-weight: bold; color: #1E293B;">#{rank}</td>
            <td style="padding: 10px 14px; font-weight: 600; color: #0F172A;">{item['role']}</td>
            <td style="padding: 10px 14px; text-align: center; font-weight: bold; color: #2563EB;">{item['overall_fit']}%</td>
            <td style="padding: 10px 14px; text-align: center; color: #475569;">{item['coverage_score']}%</td>
            <td style="padding: 10px 14px; color: #64748B; font-size: 0.9em;">{skills_str}</td>
        </tr>
        """

    # Rows for gap table
    gap_rows = ""
    for gap in gap_results.get("gap_list", []):
        gap_rows += f"""
        <tr style="border-bottom: 1px solid #E2E8F0;">
            <td style="padding: 10px 14px; font-weight: 600; color: #DC2626;">{gap['skill']}</td>
            <td style="padding: 10px 14px; color: #475569;">{gap['category']}</td>
            <td style="padding: 10px 14px; text-align: center; font-weight: 600; color: #1E293B;">{gap['demand']*100:.1f}%</td>
            <td style="padding: 10px 14px; text-align: center; color: #64748B;">~{gap['est_weeks_to_learn']} weeks</td>
        </tr>
        """

    # Phases for roadmap
    roadmap_cards = ""
    for p in roadmap.get("phases", []):
        milestone_items = "".join([f"<li style='margin-bottom: 4px;'>{m}</li>" for m in p.get("milestones", [])])
        res_link = f"<div style='margin-top: 8px;'><a href='{p['resource_url']}' target='_blank' style='color: #2563EB; font-weight: 600; font-size: 0.9em;'>🔗 Verified Resource: {p['resource_title']}</a></div>" if p.get("resource_url") else ""
        roadmap_cards += f"""
        <div style="background: #F8FAFC; border-left: 4px solid #10B981; border-radius: 8px; padding: 16px; margin-bottom: 14px; border: 1px solid #E2E8F0;">
            <div style="font-weight: 700; color: #065F46; font-size: 1.05em;">{p['phase_title']}: {p['skill']} ({p['week_span']})</div>
            <div style="font-size: 0.9em; color: #047857; margin: 4px 0 8px 0;"><b>Objective:</b> {p['objective']} | Category: <code>{p['category']}</code></div>
            <ul style="margin: 0; padding-left: 20px; font-size: 0.88em; color: #334155;">
                {milestone_items}
            </ul>
            {res_link}
        </div>
        """

    # Readability tips
    tips_html = "".join([f"<li style='margin-bottom: 6px; color: #334155;'>{t}</li>" for t in readability.get("tips", [])])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SkillBridge Career Audit Report - {target_role}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #0F172A;
            background: #FFFFFF;
            line-height: 1.6;
            margin: 0;
            padding: 30px;
        }}
        .report-container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        .header {{
            border-bottom: 2px solid #E2E8F0;
            padding-bottom: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }}
        .title {{
            font-size: 26px;
            font-weight: 800;
            color: #1E3A8A;
            margin: 0;
        }}
        .subtitle {{
            color: #64748B;
            font-size: 14px;
            margin-top: 4px;
        }}
        .meta {{
            text-align: right;
            font-size: 13px;
            color: #94A3B8;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 30px;
        }}
        .kpi-box {{
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 16px;
            text-align: center;
        }}
        .kpi-label {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            color: #64748B;
            letter-spacing: 0.5px;
        }}
        .kpi-val {{
            font-size: 28px;
            font-weight: 800;
            color: #0F172A;
            margin: 4px 0;
        }}
        .kpi-sub {{
            font-size: 11px;
            color: #94A3B8;
        }}
        .rec-banner {{
            background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
            border-left: 5px solid #F59E0B;
            border-radius: 8px;
            padding: 18px 22px;
            margin-bottom: 30px;
        }}
        h2 {{
            font-size: 18px;
            font-weight: 700;
            color: #1E293B;
            border-bottom: 1px solid #E2E8F0;
            padding-bottom: 8px;
            margin-top: 30px;
            margin-bottom: 16px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 24px;
            font-size: 14px;
        }}
        th {{
            background: #F1F5F9;
            color: #475569;
            font-weight: 700;
            text-align: left;
            padding: 10px 14px;
            border-bottom: 2px solid #CBD5E1;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #E2E8F0;
            font-size: 12px;
            color: #94A3B8;
            text-align: center;
        }}
        @media print {{
            body {{ padding: 0; }}
            .report-container {{ max-width: 100%; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="header">
            <div>
                <h1 class="title">SkillBridge Career & Skill-Gap Audit</h1>
                <div class="subtitle">Interpretable Graph-Theoretic Benchmark & Career Path Recommendations</div>
            </div>
            <div class="meta">
                <div><b>Date:</b> {timestamp}</div>
                <div><b>Role:</b> {target_role}</div>
            </div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-box">
                <div class="kpi-label">Overall Fit Score</div>
                <div class="kpi-val" style="color: #2563EB;">{gap_results['overall_match_score']}%</div>
                <div class="kpi-sub">Blended Coverage & TF-IDF</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-label">Skill Coverage</div>
                <div class="kpi-val">{gap_results['set_coverage_score']}%</div>
                <div class="kpi-sub">{len(gap_results['matched_skills'])} of {gap_results['total_role_skills']} core skills</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-label">Peer Standing</div>
                <div class="kpi-val" style="color: {peer_benchmark['color']};">{peer_benchmark['percentile']}%</div>
                <div class="kpi-sub">54k Resume Applicant Pool</div>
            </div>
            <div class="kpi-box">
                <div class="kpi-label">ATS Readability</div>
                <div class="kpi-val" style="color: #10B981;">{readability['readability_score']}/100</div>
                <div class="kpi-sub">Formatting & Active Voice</div>
            </div>
        </div>

        {f'''
        <div class="rec-banner">
            <div style="font-weight: 700; color: #92400E; font-size: 16px;">🎯 Primary Recommended Next Skill: {top_rec['skill']} ({top_rec['category']})</div>
            <div style="color: #78350F; font-size: 14px; margin-top: 4px;">{top_rec['reason']}</div>
            <div style="font-size: 12px; color: #B45309; margin-top: 6px;">
                Score: <b>{top_rec['score']}</b> | Graph Bridge: <b>{top_rec['norm_connectivity']}</b> | Demand: <b>{top_rec['demand']*100:.1f}%</b> | Est. Study: <b>~{top_rec['est_weeks_to_learn']} weeks</b>
            </div>
        </div>
        ''' if top_rec else ''}

        <h2>1. All-Roles Career Readiness Leaderboard</h2>
        <table>
            <thead>
                <tr>
                    <th style="width: 10%;">Rank</th>
                    <th style="width: 30%;">Career Track</th>
                    <th style="text-align: center; width: 15%;">Overall Fit</th>
                    <th style="text-align: center; width: 15%;">Skill Coverage</th>
                    <th style="width: 30%;">Key Matched Tools</th>
                </tr>
            </thead>
            <tbody>
                {leaderboard_rows}
            </tbody>
        </table>

        <h2>2. Target Role Skill Gap Analysis: {target_role}</h2>
        <table>
            <thead>
                <tr>
                    <th>Missing Skill Requirement</th>
                    <th>Category</th>
                    <th style="text-align: center;">Employer Demand</th>
                    <th style="text-align: center;">Estimated Learning Time</th>
                </tr>
            </thead>
            <tbody>
                {gap_rows}
            </tbody>
        </table>

        <h2>3. Directed 12-Week Chronological Roadmap</h2>
        {roadmap_cards}

        <h2>4. ATS Resume Optimization & Readability Feedback</h2>
        <ul style="padding-left: 20px; font-size: 14px;">
            {tips_html}
        </ul>

        <div class="footer">
            Generated autonomously by <b>SkillBridge</b> • Explainable Machine Learning & Graph Recommender System for CSE Undergraduates
        </div>
    </div>
</body>
</html>
"""
    return html_content
