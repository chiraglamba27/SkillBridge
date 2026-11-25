"""Data ingestion, normalization, and skill extraction pipeline.

Loads job postings from raw datasets (e.g. Kaggle Job Description Dataset by Ravindra Singh Rana,
LinkedIn Postings by Arshkon), normalizes job titles to canonical target roles, extracts canonical
skills per posting via `SkillExtractor`, and saves `job_skills.parquet`.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from src.config import (
    JOB_SKILLS_CSV,
    JOB_SKILLS_PARQUET,
    RAW_DATA_DIR,
    ROLE_ALIASES,
    ROLE_DEMAND_CSV,
    TARGET_ROLES,
)
from src.skill_extract import SkillExtractor


def normalize_role(title: str) -> Optional[str]:
    """Normalizes raw job titles to a canonical target role using regex & alias mappings.

    Returns canonical role or None if the title does not map to a recognized target.
    """
    if not isinstance(title, str) or not title.strip():
        return None

    clean = title.strip().lower()
    
    # 1. Direct match with alias map
    if clean in ROLE_ALIASES:
        return ROLE_ALIASES[clean]

    # 2. Substring matching for common role patterns
    if "machine learning" in clean or "ml engineer" in clean or "deep learning" in clean:
        return "Machine Learning Engineer"
    if "data scientist" in clean or "data science" in clean:
        return "Data Scientist"
    if "frontend" in clean or "front end" in clean or "ui engineer" in clean:
        return "Frontend Developer"
    if "backend" in clean or "back end" in clean:
        return "Backend Developer"
    if "full stack" in clean or "fullstack" in clean:
        return "Full Stack Developer"
    if "devops" in clean or "site reliability" in clean or "sre" in clean:
        return "DevOps Engineer"
    if "cloud engineer" in clean or "cloud architect" in clean:
        return "Cloud Engineer"
    if "data engineer" in clean or "big data" in clean:
        return "Data Engineer"

    return None


def generate_benchmark_postings(num_postings_per_role: int = 40) -> pd.DataFrame:
    """Generates a rich, realistic benchmark job posting dataset representing authentic

    industry requirements across target roles. Used when raw Kaggle CSVs are not yet
    downloaded into `data/raw/` so the full application and graph pipeline run out-of-the-box.
    """
    role_skill_templates = {
        "Machine Learning Engineer": [
            "Seeking a Machine Learning Engineer proficient in Python, PyTorch, TensorFlow, Scikit-Learn, and Pandas. Experience with MLOps, Docker, AWS, Git, and Linux required. Knowledge of Computer Vision, Natural Language Processing, and Feature Engineering is a strong plus. Strong foundation in Algorithms, Data Structures, and Model Evaluation.",
            "ML Engineer to build predictive models and neural networks using Python, Scikit-Learn, NumPy, and PyTorch. Must know SQL, Git, CI/CD, and Docker. Experience with Hugging Face, LLM Integration, and Prompt Engineering is desirable.",
            "Senior Machine Learning Engineer with expertise in Python, TensorFlow, Deep Learning, MLOps, Kubernetes, AWS, and REST APIs. Strong communication and problem solving skills required.",
            "Join our AI team! Looking for an ML Engineer skilled in Python, Scikit-Learn, PyTorch, Pandas, SQL, Docker, and Linux. Familiarity with MLflow, Weights & Biases, and Unit Testing.",
        ],
        "Data Scientist": [
            "Data Scientist wanted to conduct statistical analysis and build predictive models using Python, R, Pandas, NumPy, Scikit-Learn, and SQL. Experience with Data Visualization, Tableau, Matplotlib, and A/B Testing required. Strong Communication and Critical Thinking.",
            "Looking for a Data Scientist with expertise in SQL, Python, Pandas, Feature Engineering, Machine Learning, and Power BI. Experience with BigQuery, Snowflake, and statistical hypothesis testing.",
            "Data Scientist position requiring strong analytical skills, Python, R, Scikit-Learn, Statistical Analysis, Data Modeling, and Git. Experience in Time Series Analysis and presentation skills.",
            "Junior Data Scientist proficient in Python, SQL, Pandas, NumPy, Scikit-Learn, Data Visualization, and Excel. Excellent teamwork and problem solving abilities.",
        ],
        "Frontend Developer": [
            "Frontend Developer skilled in JavaScript, TypeScript, React, HTML, CSS, and Tailwind CSS. Experience with Next.js, Redux, REST APIs, Git, and Responsive Design. Strong focus on User Experience Design and Unit Testing with Jest.",
            "Senior Frontend Engineer proficient in TypeScript, React, Vue.js, HTML, CSS, Webpack, and Vite. Familiar with GraphQL, WebSockets, and Figma. Agile team environment.",
            "Frontend Web Developer with deep knowledge of JavaScript, HTML, CSS, React, Next.js, Bootstrap, and Git. Experience building accessible, responsive web interfaces.",
            "UI / Frontend Developer to craft interactive web applications using JavaScript, React, Redux, Tailwind CSS, REST APIs, and Postman. Strong collaboration and communication.",
        ],
        "Backend Developer": [
            "Backend Developer proficient in Python, Django, FastAPI, PostgreSQL, and Redis. Strong understanding of REST APIs, System Design, Microservices, Docker, and Git. Experience with CI/CD and Linux.",
            "Backend Software Engineer skilled in Java, Spring Boot, MySQL, MongoDB, and Apache Kafka. Deep knowledge of Object-Oriented Programming, Data Structures, Algorithms, and Docker.",
            "Node.js Backend Developer with TypeScript, Express, PostgreSQL, MongoDB, Redis, and REST APIs. Familiarity with AWS, Docker, Unit Testing, and Git.",
            "Backend Engineer focusing on high-concurrency distributed systems using Go, PostgreSQL, gRPC, Docker, Kubernetes, and Linux. Strong problem solving and system design skills.",
        ],
        "Full Stack Developer": [
            "Full Stack Developer proficient in React, Node.js, Express, JavaScript, TypeScript, and MongoDB. Strong understanding of HTML, CSS, REST APIs, Git, and Docker. Agile and teamwork oriented.",
            "Looking for a Full Stack Engineer with expertise in Python, Django, React, PostgreSQL, Docker, and AWS. Experience building end-to-end web applications and CI/CD pipelines.",
            "Full Stack Developer skilled in Next.js, TypeScript, Tailwind CSS, PostgreSQL, Supabase, and GraphQL. Strong communication and problem solving.",
            "Senior Full Stack Developer with Java, Spring Boot, React, MySQL, Docker, Kubernetes, and Git. System design and unit testing experience required.",
        ],
        "DevOps Engineer": [
            "DevOps Engineer with deep experience in Linux, Docker, Kubernetes, Terraform, AWS, and CI/CD pipelines (GitHub Actions, Jenkins). Strong Bash scripting and Python automation skills.",
            "Seeking a Cloud / DevOps Engineer proficient in Azure, Kubernetes, Docker, Ansible, Terraform, and Git. Experience with Prometheus, Grafana, and Nginx for monitoring and proxying.",
            "DevOps / Site Reliability Engineer (SRE) skilled in Linux, Bash, Docker, Kubernetes, GCP, Terraform, Helm, and CI/CD. Strong troubleshooting and system reliability background.",
            "Infrastructure DevOps Engineer with AWS, Terraform, Docker, Kubernetes, CI/CD, Linux, Python, and Prometheus. Security and cost optimization mindset.",
        ],
        "Cloud Engineer": [
            "Cloud Engineer specializing in AWS, CloudFormation, Terraform, Docker, and Linux. Strong experience in Cloud Security, IAM, VPC, and Serverless architectures. Python or Bash scripting.",
            "Cloud Solutions Engineer with hands-on expertise in Microsoft Azure, Kubernetes, Terraform, CI/CD, and PowerShell / Bash. Strong understanding of Disaster Recovery and High Availability.",
            "GCP Cloud Engineer skilled in Google Cloud Platform, BigQuery, Kubernetes, Docker, Terraform, and Python. Experience migrating on-premise workloads to the cloud.",
            "Cloud Infrastructure Engineer with multi-cloud experience across AWS, Azure, Terraform, Linux, Microservices, and Docker. Excellent documentation and presentation skills.",
        ],
        "Data Engineer": [
            "Data Engineer proficient in Python, SQL, Apache Spark, Apache Kafka, and PostgreSQL. Experience building ETL pipelines, Data Warehousing with Snowflake or BigQuery, and Airflow orchestration.",
            "Big Data Engineer with expertise in Java, Scala, Apache Spark, Hadoop, Apache Kafka, and AWS. Deep understanding of distributed systems, data modeling, and data pipelines.",
            "Data Engineer skilled in Python, SQL, dbt, Apache Airflow, PostgreSQL, Docker, and Git. Experience with data lakehouse architectures and data quality testing.",
            "Looking for a Data Pipeline Engineer with Python, SQL, Apache Spark, Redis, MongoDB, Linux, and CI/CD. Strong analytical and problem-solving skills.",
        ],
    }

    records = []
    job_counter = 1
    for role, templates in role_skill_templates.items():
        for i in range(num_postings_per_role):
            template_idx = i % len(templates)
            description = templates[template_idx]
            records.append({
                "job_id": f"benchmark_{job_counter:04d}",
                "job_title": role,
                "job_description": description,
            })
            job_counter += 1

    return pd.DataFrame(records)


def load_raw_postings(raw_dir: Optional[Path] = None) -> pd.DataFrame:
    """Discovers and loads raw job postings from CSV or JSON files inside `data/raw/`.

    Falls back to benchmark generator if no raw files exist.
    """
    raw_dir = raw_dir or RAW_DATA_DIR
    csv_files = list(raw_dir.glob("*.csv")) + list(raw_dir.glob("*.json"))

    if not csv_files:
        print(f"[Ingest] No raw job dataset files found in {raw_dir}. Generating benchmark dataset...")
        return generate_benchmark_postings(num_postings_per_role=50)

    frames = []
    for f in csv_files:
        print(f"[Ingest] Reading {f.name}...")
        try:
            if f.suffix == ".csv":
                df = pd.read_csv(f, low_memory=False)
            else:
                df = pd.read_json(f)
            
            # Identify title and description columns across different schemas
            # (Ravindra Singh Rana Kaggle schema: Job Title, Job Description)
            # (LinkedIn / Arshkon schema: title, description)
            title_col = None
            desc_col = None

            for col in df.columns:
                lower_col = col.lower().replace("_", " ").strip()
                if lower_col in ["job title", "title", "role", "position"]:
                    title_col = col
                if lower_col in ["job description", "description", "job details", "summary"]:
                    desc_col = col

            if title_col and desc_col:
                subset = df[[title_col, desc_col]].dropna()
                subset = subset.rename(columns={title_col: "job_title", desc_col: "job_description"})
                subset["job_id"] = [f"{f.stem}_{i}" for i in range(len(subset))]
                frames.append(subset)
            else:
                print(f"[Ingest] Warning: Could not find title/description columns in {f.name}")
        except Exception as e:
            print(f"[Ingest] Error loading {f.name}: {e}")

    if not frames:
        print("[Ingest] No valid rows parsed from raw files. Falling back to benchmark dataset.")
        return generate_benchmark_postings(num_postings_per_role=50)

    combined = pd.concat(frames, ignore_index=True)
    return combined


def process_and_extract_skills(raw_df: pd.DataFrame, extractor: SkillExtractor) -> pd.DataFrame:
    """Normalizes titles, drops invalid records, and extracts canonical skills per posting."""
    # 1. Normalize titles
    raw_df["role"] = raw_df["job_title"].apply(normalize_role)
    valid_df = raw_df.dropna(subset=["role", "job_description"]).copy()
    valid_df = valid_df[valid_df["role"].isin(TARGET_ROLES)]

    # 2. Extract skills per posting
    print(f"[Ingest] Extracting skills for {len(valid_df)} job postings...")
    extracted_skills_list = []
    for desc in valid_df["job_description"]:
        skills = extractor.extract_skills(desc)
        extracted_skills_list.append(skills)

    valid_df["skills"] = extracted_skills_list

    # Filter out postings where no skills were identified
    valid_df = valid_df[valid_df["skills"].apply(len) > 0].copy()

    return valid_df[["role", "job_id", "skills", "job_description"]]


def save_processed_data(processed_df: pd.DataFrame) -> None:
    """Saves processed dataset to Parquet and CSV."""
    # Parquet format requires pyarrow
    try:
        processed_df.to_parquet(JOB_SKILLS_PARQUET, index=False)
        print(f"[Ingest] Saved Parquet output to: {JOB_SKILLS_PARQUET}")
    except Exception as e:
        print(f"[Ingest] Parquet write error: {e}. Writing CSV backup.")

    # Always write CSV backup with JSON-encoded skills list for compatibility
    csv_df = processed_df.copy()
    csv_df["skills"] = csv_df["skills"].apply(json.dumps)
    csv_df.to_csv(JOB_SKILLS_CSV, index=False)
    print(f"[Ingest] Saved CSV output to: {JOB_SKILLS_CSV}")


def run_phase1_ingestion() -> Tuple[pd.DataFrame, Dict[str, List[Tuple[str, int]]]]:
    """Runs Phase 1 end-to-end: loads postings, extracts skills, saves output,

    and prints acceptance metrics (top 20 skills per role & total processed).
    """
    extractor = SkillExtractor()
    raw_df = load_raw_postings()
    processed_df = process_and_extract_skills(raw_df, extractor)
    save_processed_data(processed_df)

    # Acceptance calculations: top 20 skills per role
    top_skills_per_role = {}
    print("\n" + "=" * 60)
    print("PHASE 1 ACCEPTANCE: TOP 20 SKILLS PER ROLE")
    print(f"Total Postings Processed: {len(processed_df)}")
    print("=" * 60)

    for role in TARGET_ROLES:
        role_df = processed_df[processed_df["role"] == role]
        postings_count = len(role_df)
        all_skills = [skill for skills_list in role_df["skills"] for skill in skills_list]
        skill_counts = pd.Series(all_skills).value_counts().head(20)
        top_skills_per_role[role] = list(skill_counts.items())

        print(f"\n[Role: {role} (N={postings_count} postings)]")
        for rank, (skill, count) in enumerate(skill_counts.items(), 1):
            pct = (count / postings_count) * 100 if postings_count > 0 else 0
            print(f"  {rank:2d}. {skill:<25} : {count:3d} postings ({pct:5.1f}%)")

    return processed_df, top_skills_per_role


if __name__ == "__main__":
    run_phase1_ingestion()
