"""End-to-end pipeline orchestrator for SkillBridge.

Coordinates skill extraction, gap analysis, next-best-skill recommendation,
readability evaluation, resource retrieval, peer percentile benchmarking,
12-week sequential roadmap generation, bullet rewriting, and PyVis graph generation.
Acts as the single point of entry for the Streamlit user interface.
"""

from datetime import datetime
import json
from pathlib import Path
import tempfile
from typing import Dict, List, Optional, Tuple, Union

import networkx as nx
import pandas as pd
from pyvis.network import Network

from src.bullet_rewriter import analyze_and_rewrite_bullets
from src.config import (
    DEMAND_THRESHOLD,
    JOB_SKILLS_PARQUET,
    PROCESSED_DATA_DIR,
    ROLE_DEMAND_CSV,
    TARGET_ROLES,
    WEIGHT_CONNECTIVITY,
    WEIGHT_DEMAND,
    WEIGHT_EASE,
)
from src.demand import compute_role_demand, get_high_demand_skills, get_role_demand_dict
from src.gap import analyze_custom_job_gap, analyze_resume_gap, extract_text_from_file
from src.graph_builder import build_and_save_all_graphs, load_graph
from src.peer_benchmark import compute_peer_percentile
from src.readability import score_resume_readability
from src.recommend import recommend_next_skills
from src.resources import detect_career_archetypes, get_learning_resources_for_skills
from src.roadmap import generate_12_week_roadmap
from src.skill_extract import SkillExtractor


class SkillBridgePipeline:
    """Orchestrates end-to-end SkillBridge analysis with advanced career advising features."""

    def __init__(self):
        self.extractor = SkillExtractor()
        self.job_skills_df = self._load_or_build_job_skills()
        self.demand_df = self._load_or_build_demand()
        self.graphs: Dict[str, nx.Graph] = {}
        self._ensure_graphs()

    def _load_or_build_job_skills(self) -> pd.DataFrame:
        """Loads processed job skills or runs initial ingestion."""
        if JOB_SKILLS_PARQUET.exists():
            try:
                return pd.read_parquet(JOB_SKILLS_PARQUET)
            except Exception:
                pass
        if JOB_SKILLS_CSV.exists():
            df = pd.read_csv(JOB_SKILLS_CSV)
            if "skills" in df.columns and len(df) > 0 and isinstance(df["skills"].iloc[0], str):
                import json
                def safe_parse_skills(x):
                    if isinstance(x, list):
                        return x
                    try:
                        return json.loads(x)
                    except Exception:
                        return []
                df["skills"] = df["skills"].apply(safe_parse_skills)
            return df
        from src.ingest import run_phase1_ingestion
        df, _ = run_phase1_ingestion()
        return df

    def _load_or_build_demand(self) -> pd.DataFrame:
        """Loads demand table or computes from job_skills."""
        if ROLE_DEMAND_CSV.exists():
            return pd.read_csv(ROLE_DEMAND_CSV)
        return compute_role_demand(self.job_skills_df)

    def _ensure_graphs(self) -> None:
        """Ensures graphs exist on disk for all target roles."""
        for role in TARGET_ROLES:
            G = load_graph(role)
            if G is None:
                build_and_save_all_graphs(self.job_skills_df)
                break

    def get_role_graph(self, role: str) -> nx.Graph:
        """Returns the NetworkX graph for a target role."""
        if role not in self.graphs:
            G = load_graph(role)
            if G is None:
                build_and_save_all_graphs(self.job_skills_df)
                G = load_graph(role) or nx.Graph()
            self.graphs[role] = G
        return self.graphs[role]

    def compute_all_roles_leaderboard(self, resume_text: str) -> List[Dict[str, object]]:
        """Feature 1: Evaluates resume against ALL 8 canonical roles to determine best current fit."""
        leaderboard = []
        for role in TARGET_ROLES:
            demand_dict = get_role_demand_dict(self.demand_df, role)
            gap_res = analyze_resume_gap(
                resume_text=resume_text,
                target_role=role,
                job_skills_df=self.job_skills_df,
                demand_dict=demand_dict,
                extractor=self.extractor,
            )
            leaderboard.append({
                "role": role,
                "overall_fit": gap_res["overall_match_score"],
                "coverage_score": gap_res["set_coverage_score"],
                "tfidf_score": gap_res["tfidf_score"],
                "matched_count": len(gap_res["matched_skills"]),
                "required_count": gap_res["total_role_skills"],
                "matched_skills": gap_res["matched_skills"],
                "missing_count": len(gap_res["missing_skills"]),
            })

        # Sort descending by overall fit
        leaderboard.sort(key=lambda x: x["overall_fit"], reverse=True)
        return leaderboard

    def generate_markdown_report(
        self,
        resume_text: str,
        target_role: str,
        gap_results: Dict[str, object],
        recommendations: List[Dict[str, object]],
        readability: Dict[str, object],
        peer_benchmark: Dict[str, object],
        roadmap: Dict[str, object],
        leaderboard: List[Dict[str, object]],
    ) -> str:
        """Feature 5: Generates a complete downloadable Markdown career audit report."""
        top_rec = recommendations[0] if recommendations else None
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        report_lines = [
            f"# SkillBridge Career & Skill-Gap Audit Report",
            f"*Generated on: {timestamp}*",
            f"",
            f"---",
            f"## 1. Executive Summary",
            f"- **Target Role**: {target_role}",
            f"- **Overall Fit Score**: {gap_results['overall_match_score']}%",
            f"- **Role Skill Coverage**: {gap_results['set_coverage_score']}% ({len(gap_results['matched_skills'])} of {gap_results['total_role_skills']} core skills)",
            f"- **Resume Readability / ATS Score**: {readability['readability_score']}/100",
            f"- **Peer Benchmark Standing**: {peer_benchmark['standing']} ({peer_benchmark['percentile']}th percentile)",
            f"- **Top Recommended Next Skill**: {top_rec['skill'] if top_rec else 'None'} ({top_rec['category'] if top_rec else ''})",
            f"",
            f"---",
            f"## 2. Multi-Role Career Readiness Leaderboard",
            f"| Rank | Career Role | Overall Fit | Skill Coverage | Matched Skills |",
            f"| :--- | :--- | :---: | :---: | :--- |",
        ]

        for rank, item in enumerate(leaderboard, 1):
            report_lines.append(
                f"| #{rank} | **{item['role']}** | {item['overall_fit']}% | {item['coverage_score']}% | {', '.join(item['matched_skills'][:4])} |"
            )

        report_lines.extend([
            f"",
            f"---",
            f"## 3. Skill Gap Breakdown for {target_role}",
            f"### A. Missing Skills by Employer Demand",
            f"| Missing Skill | Category | Role Demand | Est. Weeks to Learn |",
            f"| :--- | :--- | :---: | :---: |",
        ])

        for gap in gap_results.get("gap_list", []):
            report_lines.append(
                f"| **{gap['skill']}** | {gap['category']} | {gap['demand']*100:.1f}% | ~{gap['est_weeks_to_learn']} weeks |"
            )

        report_lines.extend([
            f"",
            f"---",
            f"## 4. Directed 12-Week Sequential Learning Roadmap",
        ])

        for p in roadmap.get("phases", []):
            report_lines.extend([
                f"### {p['phase_title']}: **{p['skill']}** ({p['week_span']})",
                f"- **Category**: {p['category']} (~{p['duration_weeks']} weeks)",
                f"- **Focus**: {p['objective']}",
                f"- **Milestones**:",
            ])
            for m in p.get("milestones", []):
                report_lines.append(f"  - {m}")
            if p.get("resource_url"):
                report_lines.append(f"- **Verified Resource**: [{p['resource_title']}]({p['resource_url']})")
            report_lines.append("")

        report_lines.extend([
            f"---",
            f"## 5. ATS Resume Readability Audit",
            f"- **Score**: {readability['readability_score']} / 100",
            f"- **Word Count**: {readability['word_count']} words",
            f"### Key Improvement Tips:",
        ])
        for tip in readability.get("tips", []):
            report_lines.append(f"- {tip}")

        return "\n".join(report_lines)

    def generate_pyvis_html(
        self,
        G: nx.Graph,
        user_skills: List[str],
        recommended_skills: List[str],
        role: str,
        height: str = "580px",
        width: str = "100%",
    ) -> str:
        """Generates an interactive PyVis HTML network graph with color coding and high-visibility node labels."""
        user_set = set(user_skills)
        rec_set = set(recommended_skills)
        top_rec = recommended_skills[0] if recommended_skills else None

        net = Network(height=height, width=width, bgcolor="#0B0F19", font_color="#FFFFFF")

        for node in G.nodes():
            meta = G.nodes[node]
            demand_val = meta.get("demand", 0.0)
            category = meta.get("category", "Other")
            weeks = meta.get("est_weeks_to_learn", 3)

            # Node size proportional to market demand
            node_size = int(20 + (demand_val * 26))

            if node == top_rec:
                bg_color = "#F59E0B"  # Amber: Top Recommendation
                border_color = "#FDE68A"
                status = "Top Recommended Next Step"
            elif node in rec_set:
                bg_color = "#FB923C"  # Tangerine: Secondary Recommendation
                border_color = "#FED7AA"
                status = "Secondary Recommendation"
            elif node in user_set:
                bg_color = "#10B981"  # Emerald: Known Skill
                border_color = "#A7F3D0"
                status = "Verified on Resume"
            else:
                bg_color = "#EF4444"  # Coral Red: Missing Skill
                border_color = "#FECACA"
                status = "Missing Role Requirement"

            title = (
                f"<div style='font-family:system-ui,sans-serif; padding:4px;'>"
                f"<b style='font-size:14px; color:#FFFFFF;'>{node}</b><br>"
                f"<span style='color:#94A3B8;'>Status:</span> <b style='color:#38BDF8;'>{status}</b><br>"
                f"<span style='color:#94A3B8;'>Category:</span> {category}<br>"
                f"<span style='color:#94A3B8;'>Role Demand:</span> {demand_val * 100:.1f}%<br>"
                f"<span style='color:#94A3B8;'>Est. Learning:</span> ~{weeks} weeks"
                f"</div>"
            )

            net.add_node(
                node,
                label=node,
                title=title,
                color={
                    "background": bg_color,
                    "border": border_color,
                    "highlight": {"background": bg_color, "border": "#38BDF8"},
                    "hover": {"background": bg_color, "border": "#38BDF8"},
                },
                size=node_size,
                borderWidth=2.5,
                font={
                    "color": "#FFFFFF",
                    "size": 16,
                    "face": "system-ui, -apple-system, sans-serif",
                    "strokeWidth": 4,
                    "strokeColor": "#090D16",
                    "bold": True,
                },
            )

        for u, v, data in G.edges(data=True):
            weight = data.get("weight", 1)
            net.add_edge(
                u,
                v,
                value=weight,
                title=f"Co-occurrences: {weight}",
                color={
                    "color": "rgba(148, 163, 184, 0.45)",
                    "highlight": "#38BDF8",
                    "hover": "#38BDF8",
                },
            )

        # High-performance physics & rendering options:
        # Ensures nodes spread across canvas cleanly and text labels are always crisp
        net.set_options("""
        var options = {
          "nodes": {
            "font": {
              "color": "#FFFFFF",
              "size": 16,
              "strokeWidth": 4,
              "strokeColor": "#090D16",
              "face": "system-ui, -apple-system, sans-serif"
            },
            "borderWidth": 2.5,
            "shadow": {
              "enabled": true,
              "color": "rgba(0,0,0,0.6)",
              "size": 10
            }
          },
          "edges": {
            "color": {
              "color": "rgba(148, 163, 184, 0.45)",
              "highlight": "#38BDF8",
              "hover": "#38BDF8"
            },
            "width": 1.8,
            "smooth": {
              "type": "continuous"
            }
          },
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -4500,
              "centralGravity": 0.22,
              "springLength": 170,
              "springConstant": 0.04,
              "damping": 0.12
            },
            "stabilization": {
              "enabled": true,
              "iterations": 180
            }
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 80,
            "zoomView": true,
            "dragView": true
          }
        }
        """)

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
            net.save_graph(tmp.name)
            html_content = Path(tmp.name).read_text(encoding="utf-8")

        return html_content

    def run_full_analysis(
        self,
        resume_input: Union[str, bytes],
        filename: Optional[str] = None,
        target_role: str = "Machine Learning Engineer",
        custom_job_description: Optional[str] = None,
        w1: float = WEIGHT_CONNECTIVITY,
        w2: float = WEIGHT_DEMAND,
        w3: float = WEIGHT_EASE,
    ) -> Dict[str, object]:
        """Runs the complete SkillBridge pipeline including advanced features."""
        # 1. Parse text from file or raw string
        if filename and filename.endswith((".pdf", ".docx")):
            resume_text = extract_text_from_file(resume_input, filename)
        elif filename and filename.endswith((".txt", ".md")) and isinstance(resume_input, (bytes, bytearray)):
            resume_text = extract_text_from_file(resume_input, filename)
        else:
            resume_text = str(resume_input)

        # 2. Get role data & graph
        demand_dict = get_role_demand_dict(self.demand_df, target_role)
        G = self.get_role_graph(target_role)

        # 3. Gap Analysis
        if custom_job_description and custom_job_description.strip():
            gap_results = analyze_custom_job_gap(
                resume_text=resume_text,
                job_description_text=custom_job_description,
                extractor=self.extractor,
            )
            # Build custom graph containing exactly the skills required in this real posting
            custom_G = nx.Graph(role="Custom Job Posting")
            all_job_skills = set(gap_results["matched_skills"] + gap_results["missing_skills"])
            for skill in all_job_skills:
                meta = self.extractor.get_skill_metadata(skill)
                custom_G.add_node(
                    skill,
                    demand=1.0,
                    category=meta.get("category", "Other"),
                    est_weeks_to_learn=int(meta.get("est_weeks_to_learn", 3)),
                    resource_url=str(meta.get("resource_url", "")),
                    resource_title=str(meta.get("resource_title", "")),
                )
            for s1 in all_job_skills:
                for s2 in all_job_skills:
                    if s1 != s2 and G.has_edge(s1, s2):
                        custom_G.add_edge(s1, s2, weight=G[s1][s2].get("weight", 2))

            if custom_G.number_of_edges() == 0 and len(all_job_skills) > 1:
                skills_list = list(all_job_skills)
                for i in range(len(skills_list) - 1):
                    custom_G.add_edge(skills_list[i], skills_list[i+1], weight=1)

            G_to_render = custom_G
            job_demand_dict = gap_results.get("demand_dict", {s: 1.0 for s in gap_results["missing_skills"]})
        else:
            gap_results = analyze_resume_gap(
                resume_text=resume_text,
                target_role=target_role,
                job_skills_df=self.job_skills_df,
                demand_dict=demand_dict,
                extractor=self.extractor,
                demand_threshold=DEMAND_THRESHOLD,
            )
            G_to_render = G
            job_demand_dict = demand_dict

        user_skills = gap_results["user_skills"]
        missing_skills = gap_results["missing_skills"]

        # 4. Next-Best-Skill Recommendations
        recommendations = recommend_next_skills(
            user_skills=user_skills,
            missing_skills=missing_skills,
            G=G,
            demand_dict=job_demand_dict,
            extractor=self.extractor,
            w1=w1,
            w2=w2,
            w3=w3,
            top_k=3,
        )

        recommended_skill_names = [r["skill"] for r in recommendations]

        # 5. Readability & ATS Scoring
        readability_results = score_resume_readability(resume_text)

        # 6. Feature 1: Multi-Role Career Readiness Leaderboard
        leaderboard = self.compute_all_roles_leaderboard(resume_text)

        # 7. Feature 2: Directed 12-Week Roadmap
        roadmap = generate_12_week_roadmap(recommendations, target_role, self.extractor)

        # 8. Feature 3: Peer Percentile Benchmark (54k dataset model)
        peer_benchmark = compute_peer_percentile(len(gap_results["matched_skills"]), target_role)

        # 9. Feature 4: Action-Verb Bullet Rewrites
        bullet_rewrites = analyze_and_rewrite_bullets(resume_text)

        # 10. Free Learning Resources
        resources = get_learning_resources_for_skills(recommended_skill_names, self.extractor)

        # 11. Interactive PyVis Graph HTML
        graph_html = self.generate_pyvis_html(
            G=G_to_render,
            user_skills=user_skills,
            recommended_skills=recommended_skill_names,
            role=target_role if not custom_job_description else "Custom Job Posting",
        )

        # 12. Career Archetypes (Stretch)
        archetypes = detect_career_archetypes(G)

        # Separate Technical vs Soft Skill Coverage
        cat_breakdown = gap_results.get("category_breakdown", {})
        tech_matched, tech_total = 0, 0
        soft_matched, soft_total = 0, 0

        for cat_name, cat_data in cat_breakdown.items():
            if cat_name == "Soft Skills":
                soft_matched += cat_data.get("matched_count", 0)
                soft_total += cat_data.get("total_required", 0)
            else:
                tech_matched += cat_data.get("matched_count", 0)
                tech_total += cat_data.get("total_required", 0)

        gap_results["tech_coverage_pct"] = round((tech_matched / tech_total) * 100, 1) if tech_total > 0 else 0.0
        gap_results["soft_coverage_pct"] = round((soft_matched / soft_total) * 100, 1) if soft_total > 0 else 0.0

        # 13. Feature 5: Downloadable Reports (Markdown + Printable Executive HTML)
        markdown_report = self.generate_markdown_report(
            resume_text=resume_text,
            target_role=target_role,
            gap_results=gap_results,
            recommendations=recommendations,
            readability=readability_results,
            peer_benchmark=peer_benchmark,
            roadmap=roadmap,
            leaderboard=leaderboard,
        )

        from src.report_generator import generate_html_report
        html_report = generate_html_report(
            target_role=target_role,
            gap_results=gap_results,
            recommendations=recommendations,
            readability=readability_results,
            peer_benchmark=peer_benchmark,
            roadmap=roadmap,
            leaderboard=leaderboard,
        )

        return {
            "target_role": target_role,
            "resume_text": resume_text,
            "user_skills": user_skills,
            "gap_results": gap_results,
            "recommendations": recommendations,
            "readability": readability_results,
            "resources": resources,
            "graph_html": graph_html,
            "archetypes": archetypes,
            "leaderboard": leaderboard,
            "roadmap": roadmap,
            "peer_benchmark": peer_benchmark,
            "bullet_rewrites": bullet_rewrites,
            "markdown_report": markdown_report,
            "html_report": html_report,
            "graph_stats": {
                "nodes_count": G.number_of_nodes(),
                "edges_count": G.number_of_edges(),
            },
        }
