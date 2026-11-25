"""Skill extraction module using spaCy PhraseMatcher and canonical aliases.

This module maps variations, acronyms, and aliases in resume and job texts to
standardized canonical skills defined in `data/skill_meta.csv`.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
import spacy
from spacy.matcher import PhraseMatcher

from src.config import SKILL_META_PATH


# Hand-crafted alias map mapping common variants, abbreviations, and informal names
# to their canonical skill names.
COMMON_ALIASES: Dict[str, str] = {
    # Languages
    "python": "Python",
    "py": "Python",
    "python3": "Python",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c plus plus": "C++",
    "c#": "C#",
    "c sharp": "C#",
    "csharp": "C#",
    "golang": "Go",
    "go lang": "Go",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "rust": "Rust",
    "r-lang": "R",
    "r language": "R",
    "r programming": "R",
    "sql": "SQL",
    "structured query language": "SQL",
    "html": "HTML",
    "html5": "HTML",
    "css": "CSS",
    "css3": "CSS",
    "bash": "Bash",
    "shell": "Shell Scripting",
    "shell scripting": "Shell Scripting",
    "bash scripting": "Bash",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "scala": "Scala",
    "php": "PHP",
    "ruby": "Ruby",
    "matlab": "MATLAB",

    # Frameworks & Libraries
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "react native": "React Native",
    "angular": "Angular",
    "angular.js": "Angular",
    "angularjs": "Angular",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express",
    "express.js": "Express",
    "expressjs": "Express",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "django": "Django",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "flask": "Flask",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "spring": "Spring Framework",
    "asp.net": "ASP.NET Core",
    "asp.net core": "ASP.NET Core",
    "dotnet": "ASP.NET Core",
    ".net": "ASP.NET Core",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "keras": "Keras",
    "scikit-learn": "Scikit-Learn",
    "scikit learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "opencv": "OpenCV",
    "cv2": "OpenCV",
    "huggingface": "Hugging Face",
    "hugging face": "Hugging Face",
    "transformers": "Hugging Face",
    "nltk": "NLTK",
    "spacy": "spaCy",
    "apache spark": "Apache Spark",
    "spark": "Apache Spark",
    "pyspark": "Apache Spark",
    "apache kafka": "Apache Kafka",
    "kafka": "Apache Kafka",
    "tailwind": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "redux": "Redux",
    "graphql": "GraphQL",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "grpc": "gRPC",

    # Databases
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "sqlite": "SQLite",
    "cassandra": "Cassandra",
    "elasticsearch": "Elasticsearch",
    "elastic search": "Elasticsearch",
    "oracle": "Oracle DB",
    "oracle db": "Oracle DB",
    "sql server": "Microsoft SQL Server",
    "mssql": "Microsoft SQL Server",
    "neo4j": "Neo4j",
    "dynamodb": "DynamoDB",
    "dynamo": "DynamoDB",
    "firebase": "Firebase",
    "supabase": "Supabase",
    "snowflake": "Snowflake",
    "bigquery": "BigQuery",
    "google bigquery": "BigQuery",
    "redshift": "Amazon Redshift",

    # Cloud / DevOps
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "ci/cd": "CI/CD",
    "ci cd": "CI/CD",
    "continuous integration": "CI/CD",
    "github actions": "GitHub Actions",
    "jenkins": "Jenkins",
    "linux": "Linux",
    "nginx": "Nginx",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "helm": "Helm",
    "argocd": "ArgoCD",
    "argo cd": "ArgoCD",

    # Tools
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "bitbucket": "Bitbucket",
    "jira": "Jira",
    "postman": "Postman",
    "vs code": "VS Code",
    "vscode": "VS Code",
    "vim": "Vim",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "excel": "Excel",
    "figma": "Figma",
    "airflow": "Apache Airflow",
    "apache airflow": "Apache Airflow",
    "hadoop": "Apache Hadoop",
    "dbt": "dbt",
    "weights and biases": "Weights & Biases",
    "wandb": "Weights & Biases",
    "mlflow": "MLflow",
    "selenium": "Selenium",
    "pytest": "PyTest",
    "jest": "Jest",

    # Methodologies & Concepts
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "mlops": "MLOps",
    "system design": "System Design",
    "microservices": "Microservices",
    "distributed systems": "Distributed Systems",
    "agile": "Agile",
    "scrum": "Scrum",
    "oop": "Object-Oriented Programming",
    "object oriented programming": "Object-Oriented Programming",
    "data structures": "Data Structures",
    "algorithms": "Algorithms",
    "dsa": "Data Structures",
    "unit testing": "Unit Testing",
    "tdd": "Test-Driven Development",
    "test driven development": "Test-Driven Development",
    "cybersecurity": "Cybersecurity",
    "data modeling": "Data Modeling",
    "etl": "ETL",
    "websockets": "WebSockets",
    "oauth": "OAuth",
    "jwt": "JWT",
    "cloud security": "Cloud Security",
    "data visualization": "Data Visualization",
    "feature engineering": "Feature Engineering",
    "a/b testing": "A/B Testing",
    "ab testing": "A/B Testing",
    "reinforcement learning": "Reinforcement Learning",
    "rl": "Reinforcement Learning",
    "time series": "Time Series Analysis",
    "time series analysis": "Time Series Analysis",
    "web scraping": "Web Scraping",
    "api development": "API Development",
    "prompt engineering": "Prompt Engineering",
    "vector databases": "Vector Databases",
    "llm": "LLM Integration",
    "large language models": "LLM Integration",
    "llm integration": "LLM Integration",
    "semantic search": "Semantic Search",
    "ui/ux": "User Experience Design",
    "ux design": "User Experience Design",
    "responsive design": "Responsive Design",
    "rbac": "Role-Based Access Control",
    "data pipeline": "Data Pipeline Architecture",
    "data pipelines": "Data Pipeline Architecture",
    "query optimization": "Query Optimization",
    "load balancing": "Load Balancing",
    "cdn": "Content Delivery Networks",
    "clean architecture": "Clean Architecture",
    "design patterns": "Design Patterns",
    "devops": "CI/CD",
}

# Ambiguous short keywords that require exact casing or strict token patterns
# to prevent false positives (e.g. English "go" vs "Go" programming language).
AMBIGUOUS_SHORT_KEYWORDS = {
    "Go": r"\b(Go|Golang|go\s*lang)\b",
    "R": r"\b(R\s*language|R\s*programming|\b[R]\b(?=[\s,;]+(programming|analysis|stats|code|data)))",
    "C": r"\b(C\s*language|C\s*programming|\b[C]\b(?=[\s,;]+(programming|code|developer)))",
}


class SkillExtractor:
    """Extracts canonical skills from plain text using spaCy PhraseMatcher

    and aliases mapping table.
    """

    def __init__(self, meta_path: Optional[Path] = None):
        self.meta_path = meta_path or SKILL_META_PATH
        self.nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        
        # Load metadata
        self.skill_meta_df = self._load_skill_meta()
        self.canonical_skills: Set[str] = set(self.skill_meta_df["skill"].unique())
        
        # Build phrase patterns
        self.pattern_to_canonical: Dict[str, str] = {}
        self._build_matcher()

    def _load_skill_meta(self) -> pd.DataFrame:
        """Loads skill metadata CSV containing categories, weeks, and resource URLs."""
        if not self.meta_path.exists():
            raise FileNotFoundError(f"Skill metadata not found at {self.meta_path}")
        df = pd.read_csv(self.meta_path)
        return df.drop_duplicates(subset=["skill"])

    def _build_matcher(self) -> None:
        """Constructs PhraseMatcher patterns from canonical names and alias mappings."""
        # 1. Add canonical names
        for skill in self.canonical_skills:
            norm_phrase = skill.lower()
            self.pattern_to_canonical[norm_phrase] = skill

        # 2. Add common aliases
        for alias, canonical in COMMON_ALIASES.items():
            if canonical in self.canonical_skills:
                self.pattern_to_canonical[alias.lower()] = canonical

        # 3. Compile spaCy doc patterns
        # Filter out ambiguous single-letter or common-verb tokens from PhraseMatcher
        # which will be handled via dedicated boundary rules.
        phrases_for_spacy = []
        for phrase in self.pattern_to_canonical.keys():
            if phrase.lower() in {"go", "r", "c", "next", "it", "me", "as", "be", "do"}:
                continue
            phrases_for_spacy.append(phrase)

        patterns = [self.nlp.make_doc(text) for text in phrases_for_spacy]
        self.matcher.add("SKILL_MATCHER", patterns)

    def extract_skills(self, text: str) -> List[str]:
        """Extracts unique canonical skills from input text.

        Args:
            text: Resume text or job description string.

        Returns:
            Sorted list of matched canonical skill names.
        """
        if not text or not isinstance(text, str):
            return []

        doc = self.nlp(text)
        matches = self.matcher(doc)
        
        matched_skills: Set[str] = set()

        # 1. Matcher hits
        for _, start, end in matches:
            span = doc[start:end]
            phrase_text = span.text.lower()
            if phrase_text in self.pattern_to_canonical:
                matched_skills.add(self.pattern_to_canonical[phrase_text])

        # 2. Check ambiguous short keywords via contextual regex
        for skill, pattern in AMBIGUOUS_SHORT_KEYWORDS.items():
            if skill in self.canonical_skills:
                if re.search(pattern, text):
                    matched_skills.add(skill)

        # 3. Direct regex check for common symbols like C++ and C# which tokenizers
        # may split into separate punctuation tokens.
        if "C++" in self.canonical_skills and re.search(r"\b(c\+\+|cpp)\b", text, re.IGNORECASE):
            matched_skills.add("C++")
        if "C#" in self.canonical_skills and re.search(r"\b(c#|csharp)\b", text, re.IGNORECASE):
            matched_skills.add("C#")
        if "CI/CD" in self.canonical_skills and re.search(r"\bci\s*/\s*cd\b", text, re.IGNORECASE):
            matched_skills.add("CI/CD")

        return sorted(list(matched_skills))

    def get_skill_category(self, skill: str) -> str:
        """Returns the category for a given canonical skill."""
        row = self.skill_meta_df[self.skill_meta_df["skill"] == skill]
        if not row.empty:
            return row.iloc[0]["category"]
        return "Other"

    def get_skill_metadata(self, skill: str) -> Dict[str, object]:
        """Returns full metadata record for a skill."""
        row = self.skill_meta_df[self.skill_meta_df["skill"] == skill]
        if not row.empty:
            return row.iloc[0].to_dict()
        return {
            "skill": skill,
            "category": "Other",
            "est_weeks_to_learn": 3,
            "resource_url": "",
            "resource_title": "",
        }

    def get_vocabulary(self) -> List[str]:
        """Returns sorted list of all canonical skills in vocabulary."""
        return sorted(list(self.canonical_skills))

    def suggest_noun_phrases(self, texts: List[str], top_n: int = 20) -> List[Tuple[str, int]]:
        """Extracts frequent noun phrases from descriptions to discover emerging/missing skills.

        Helpful for Phase 1 acceptance and vocabulary expansion.
        """
        phrase_counts: Dict[str, int] = {}
        # Use full parser for noun chunk extraction
        full_nlp = spacy.load("en_core_web_sm", disable=["ner"])
        
        for doc in full_nlp.pipe(texts, batch_size=50):
            for chunk in doc.noun_chunks:
                clean_chunk = chunk.text.lower().strip()
                if len(clean_chunk) > 2 and clean_chunk not in self.pattern_to_canonical:
                    phrase_counts[clean_chunk] = phrase_counts.get(clean_chunk, 0) + 1

        sorted_phrases = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_phrases[:top_n]
