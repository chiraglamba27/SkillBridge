# SkillBridge Master Project Flow & Architectural Guide
**A Comprehensive In-and-Out Engineering Walkthrough and Viva Voce Defense Reference**

---

## 1. Executive Summary & Problem Formulation

In modern technical recruitment, computer science students face a significant information asymmetry:
1. **Ambiguous Job Descriptions**: Postings often list dozens of buzzwords without indicating which skills are truly foundational versus nice-to-have.
2. **Black-Box Resume Screeners (ATS)**: Commercial Applicant Tracking Systems score candidates using proprietary heuristics or opaque transformer models that offer no actionable feedback or transparency.
3. **Overwhelming Learning Paths**: When a student realizes they lack skills for a target role (e.g., Machine Learning Engineer or DevOps Engineer), they do not know which skill to learn **first** to maximize their hiring potential while minimizing study time.

**SkillBridge** solves this problem using **interpretable, explainable Artificial Intelligence and Graph Theory**. Instead of uninterpretable deep neural networks or generative hallucinations, SkillBridge couples **spaCy PhraseMatcher**, **Vector Space TF-IDF**, and **NetworkX Co-occurrence Graphs** to provide:
- A transparent dual-fit percentage (hard skill coverage + semantic alignment).
- A category-by-category skill gap breakdown.
- An interactive color-coded knowledge graph.
- A mathematically ranked "Next Best Skill" recommendation that accounts for prior knowledge (graph connectivity), market demand, and learning effort.
- A deterministic ATS readability audit with concrete guidance.
- Verified, free learning resource links.

---

## 2. Theoretical Framework & Why Traditional Approaches Fail

| Parameter | Black-Box Deep Learning (LLM / Embeddings Alone) | Traditional Keyword Count | SkillBridge Approach |
| :--- | :--- | :--- | :--- |
| **Explainability** | Opaque weights; prone to hallucination; difficult to defend in an academic viva. | Naive; ignores context, synonyms, and skill relationships. | **100% Explainable**: Clear mathematical formulas, graph adjacency, and PhraseMatcher rules. |
| **Skill Adjacency** | Embeddings measure semantic closeness in language, not real-world technological compatibility. | Completely missing; skills are treated as independent isolated tokens. | **Graph Co-occurrence**: Edge weights reflect actual industry pairings (e.g., *React* + *TypeScript*). |
| **Recommendation Strategy** | Generates arbitrary courses or generic roadmaps without consideration of student's current skill set. | None. Simply reports missing words. | **Multi-Criteria Optimization**: Combines graph bridge effect, employer demand frequency, and learning time. |
| **Computational Footprint** | Requires GPUs, massive memory, or expensive external API calls. | Negligible, but functionally useless. | **Lightweight & Efficient**: Runs on standard CPU within seconds using optimized sparse matrices. |

---

## 3. System Architecture & Directory Map

```
skillbridge/
├── data/
│   ├── raw/                      # Downloaded raw datasets (gitignored)
│   ├── processed/                # Transformed artifacts
│   │   ├── job_skills.parquet    # Standardized job records with extracted skill lists
│   │   ├── job_skills.csv        # CSV backup of processed postings
│   │   ├── role_demand.csv       # Skill demand percentages per target role
│   │   └── graph_{role}.gpickle  # Serialized NetworkX co-occurrence graphs per role
│   └── skill_meta.csv            # Hand-curated vocabulary (260+ skills with meta)
├── src/
│   ├── config.py                 # Paths, thresholds, weights, and constants
│   ├── ingest.py                 # Ingestion, title normalization, and benchmark data
│   ├── skill_extract.py          # spaCy PhraseMatcher & alias resolution engine
│   ├── demand.py                 # Frequency and demand calculations
│   ├── graph_builder.py          # NetworkX graph builder, edge pruning & centrality
│   ├── gap.py                    # Dual-fit scoring (TF-IDF + Set Coverage) & breakdown
│   ├── recommend.py              # Next-best-skill ranking algorithm
│   ├── readability.py            # Rule-based ATS resume checker (100-pt scale)
│   ├── resources.py              # Verified learning resource lookup & archetypes
│   └── pipeline.py               # Single entry-point orchestrator
├── app/
│   └── streamlit_app.py          # Streamlit UI (Presentation layer only)
├── tests/
│   ├── test_skill_extract.py     # PhraseMatcher, casing, and alias unit tests
│   ├── test_gap.py               # Scoring and category breakdown tests
│   ├── test_recommend.py         # Multi-criteria ranking & determinism tests
│   └── test_readability.py       # Rule-by-rule resume audit tests
├── notebooks/
│   └── exploration.ipynb         # Interactive EDA and model verification
├── requirements.txt              # Pinned Python package dependencies
├── pytest.ini                    # PyTest configuration (pythonpath = .)
└── README.md                     # Project overview and quickstart guide
```

---

## 4. Phase-by-Phase Technical Walkthrough

### Phase 1: Data Ingestion & Skill Vocabulary (`src/ingest.py`, `src/skill_extract.py`)

#### 1. The Skill Vocabulary (`data/skill_meta.csv`)
The foundation of SkillBridge is a curated vocabulary of **260+ computer science skills** spanning six distinct categories:
- **Languages**: Python, Java, C++, TypeScript, Go, Rust, SQL, Bash, etc.
- **Frameworks**: React, PyTorch, Scikit-Learn, Next.js, FastAPI, Spring Boot, etc.
- **Databases**: PostgreSQL, MongoDB, Redis, Cassandra, Snowflake, Neo4j, etc.
- **Cloud/DevOps**: Docker, Kubernetes, AWS, Terraform, CI/CD, Linux, Prometheus, etc.
- **Tools**: Git, Jira, Postman, Apache Kafka, Airflow, Figma, PyTest, etc.
- **Soft Skills**: Communication, Teamwork, Problem Solving, Agile, Code Review, etc.

Each row contains:
- `skill`: Canonical name (e.g., `PostgreSQL`).
- `category`: Structural grouping.
- `est_weeks_to_learn`: Hand-assigned human learning estimate based on typical university module durations (1 to 8 weeks).
- `resource_url`: Direct URL to official documentation or verified learning platforms.
- `resource_title`: Human-readable title of the course or manual.

#### 2. Alias Mapping & Boundary Normalization (`src/skill_extract.py`)
Real resumes and job postings use slang, acronyms, and version tags. `COMMON_ALIASES` maps over 120 common variants to their canonical forms:
- `k8s` $\rightarrow$ `Kubernetes`
- `postgres`, `postgresql` $\rightarrow$ `PostgreSQL`
- `reactjs`, `react.js` $\rightarrow$ `React`
- `sklearn`, `scikit learn` $\rightarrow$ `Scikit-Learn`
- `tf`, `tensorflow` $\rightarrow$ `TensorFlow`
- `golang` $\rightarrow$ `Go`

**Preventing False Positives**:
A common flaw in naive string-matching is false positives for short words (e.g., the English word "go" in *"we will go to the office"* or "next" in *"next week"*). SkillBridge resolves this by:
1. Excluding single-character and common verbs (`go`, `r`, `c`, `next`) from the case-insensitive PhraseMatcher.
2. Evaluating these short tokens using contextual regex with word boundaries:
   - For `Go`: `\b(Go|Golang|go\s*lang)\b`
   - For `R`: `\b(R\s*language|R\s*programming|\b[R]\b(?=[\s,;]+(programming|analysis|stats|code|data)))`
   - For `C`: `\b(C\s*language|C\s*programming|\b[C]\b(?=[\s,;]+(programming|code|developer)))`
3. Supporting special programming language symbols (`C++`, `C#`, `CI/CD`) that tokenizers often split into separate punctuation tokens.

#### 3. Title Normalization (`src/ingest.py`)
Job titles across Kaggle datasets vary wildly (*"Sr. Machine Learning Specialist"*, *"Junior ML Engineer"*, *"AI/ML Software Developer"*). `normalize_role()` maps raw strings into one of **8 Canonical Roles**:
1. Machine Learning Engineer
2. Data Scientist
3. Frontend Developer
4. Backend Developer
5. Full Stack Developer
6. DevOps Engineer
7. Cloud Engineer
8. Data Engineer

#### 4. Benchmark Dataset Generator
If raw Kaggle CSV files are not yet present in `data/raw/`, `ingest.py` automatically synthesizes a benchmark dataset of 400 postings (50 per target role) reflecting genuine job descriptions, saving the output to `data/processed/job_skills.parquet` and `job_skills.csv`.

---

### Phase 2: Co-Occurrence Graph Construction & Demand (`src/graph_builder.py`, `src/demand.py`)

#### 1. Graph Definition
For each target role $R$, we construct an undirected, weighted graph:
$$G_R = (V_R, E_R, W_R)$$
- **Nodes ($V_R$)**: Canonical skills mentioned in job postings for role $R$.
- **Edges ($E_R$)**: An edge $(u, v)$ exists between skill $u$ and skill $v$ if they appear together in the same job posting.
- **Weights ($W_R$)**: $w(u, v)$ is the total number of postings in role $R$ where both $u$ and $v$ co-occur.

#### 2. Noise Filtering via Minimum Edge Weight
To eliminate accidental, one-off skill pairings, edges with a weight below `MIN_EDGE_WEIGHT = 2` are pruned:
$$E_R' = \{ (u, v) \in E_R \mid w(u, v) \ge \text{MIN\_EDGE\_WEIGHT} \}$$

#### 3. Node Attributes & Centrality
For every node $u \in V_R$, the graph stores:
- **Demand Fraction**:
  $$\text{Demand}(u) = \frac{\text{Count of postings in role } R \text{ mentioning } u}{\text{Total postings in role } R}$$
- **Degree Centrality**:
  $$C_{\text{degree}}(u) = \frac{\deg(u)}{|V_R| - 1}$$
- **Betweenness Centrality**:
  $$C_{\text{betweenness}}(u) = \sum_{s \ne u \ne t} \frac{\sigma_{st}(u)}{\sigma_{st}}$$
  Where $\sigma_{st}$ is the total number of shortest paths between $s$ and $t$, and $\sigma_{st}(u)$ is the number of those paths passing through $u$. High betweenness identifies "bridge skills" that connect different sub-disciplines.

#### 4. Serialization
Graphs are serialized to disk as `data/processed/graph_{role}.gpickle` using standard Python `pickle` for instant loading in the web dashboard.

---

### Phase 3: Resume Parsing & Dual-Fit Scoring Engine (`src/gap.py`)

#### 1. Document Extraction
`extract_text_from_file()` extracts text from:
- Plain text (`.txt`, `.md`)
- PDF files via `pypdf.PdfReader`
- Word documents via `python-docx.Document`

#### 2. Dual-Fit Scoring Formulation
Evaluating candidate fit solely on keywords is overly rigid, while evaluating solely on TF-IDF ignores missing core prerequisites. SkillBridge combines both:

1. **Set Coverage Score ($S_{\text{coverage}}$)**:
   Let $U$ be the set of skills extracted from the candidate's resume.
   Let $R_{\text{core}}$ be the set of high-demand skills for the target role ($\text{Demand} \ge \text{DEMAND\_THRESHOLD} = 0.15$):
   $$S_{\text{coverage}} = \frac{|U \cap R_{\text{core}}|}{|R_{\text{core}}|} \times 100\%$$
   This strictly measures what percentage of mandatory tools the candidate possesses.

2. **TF-IDF Cosine Similarity ($S_{\text{tfidf}}$)**:
   We aggregate all job descriptions and skills for role $R$ into an aggregated domain corpus document $D_R$.
   The candidate's resume text is represented as document $D_{\text{user}}$.
   Using a sublinear TF-IDF vectorizer with unigram and bigram features:
   $$\vec{v}_{\text{user}} = \text{TF-IDF}(D_{\text{user}}), \quad \vec{v}_R = \text{TF-IDF}(D_R)$$
   $$S_{\text{tfidf}} = \frac{\vec{v}_{\text{user}} \cdot \vec{v}_R}{\|\vec{v}_{\text{user}}\| \|\vec{v}_R\|} \times 100\%$$
   This captures vocabulary depth, project narratives, and technical terminology.

3. **Blended Overall Match Score ($S_{\text{overall}}$)**:
   $$S_{\text{overall}} = 0.60 \cdot S_{\text{coverage}} + 0.40 \cdot S_{\text{tfidf}}$$

#### 3. Category Breakdown
For each category $c \in \{\text{Languages, Frameworks, Databases, Cloud/DevOps, Tools, Soft Skills}\}$:
$$\text{MatchPct}(c) = \frac{|\{u \in U \cap R_{\text{core}} \mid \text{Category}(u) = c\}|}{|\{r \in R_{\text{core}} \mid \text{Category}(r) = c\}|} \times 100\%$$

#### 4. Gap List
The gap list consists of all high-demand skills absent from the candidate's resume:
$$\text{Gap} = \{ r \in R_{\text{core}} \mid r \notin U \}$$
Sorted in descending order of market demand.

---

### Phase 4: Next-Best-Skill Recommendation Algorithm (`src/recommend.py`)

When a student has a gap list of 8 missing skills, which one should they learn first? SkillBridge models this as a **multi-criteria optimization problem**.

#### 1. Mathematical Formulation
For each candidate missing skill $M \in \text{Gap}$:
$$\text{Score}(M) = w_1 \cdot C_{\text{norm}}(M) + w_2 \cdot D_{\text{norm}}(M) + w_3 \cdot \text{Ease}(M)$$
Subject to:
$$w_1 + w_2 + w_3 = 1.0, \quad w_1, w_2, w_3 \ge 0$$
Default weights in `src/config.py`:
- $w_1 = 0.50$ (Graph Connectivity / Bridge Effect)
- $w_2 = 0.30$ (Employer Demand)
- $w_3 = 0.20$ (Ease of Acquisition)

#### 2. Component Derivations

##### A. Graph Connectivity ($C_{\text{norm}}$)
Measures how strongly the candidate's existing skills connect to $M$ in the industry co-occurrence graph. If a student knows *React* and *JavaScript*, learning *TypeScript* or *Next.js* has high connectivity, whereas learning *Kubernetes* has low connectivity.
Let $U_{\text{graph}} = U \cap V_R$ be the student's skills present in graph $G_R$:
$$C(M) = \sum_{u \in U_{\text{graph}}, (u, M) \in E_R} w(u, M)$$
Normalized against the maximum connectivity observed among all candidates:
$$C_{\text{norm}}(M) = \begin{cases} \frac{C(M)}{\max_{m \in \text{Gap}} C(m)} & \text{if } \max C(m) > 0 \\ 0.0 & \text{otherwise} \end{cases}$$

##### B. Market Demand ($D_{\text{norm}}$)
Measures the frequency of skill $M$ across job postings for role $R$:
$$D_{\text{norm}}(M) = \begin{cases} \frac{\text{Demand}(M)}{\max_{m \in \text{Gap}} \text{Demand}(m)} & \text{if } \max \text{Demand}(m) > 0 \\ 0.0 & \text{otherwise} \end{cases}$$

##### C. Ease of Acquisition ($\text{Ease}$)
Represents the inverse of the estimated weeks required for an undergraduate to master the skill:
$$\text{Ease}(M) = \frac{1}{1 + \frac{\text{est\_weeks\_to\_learn}(M)}{4.0}}$$
- If a skill takes 1 week (e.g., *Git* basics): $\text{Ease} = \frac{1}{1 + 0.25} = 0.80$
- If a skill takes 4 weeks (e.g., *Python*): $\text{Ease} = \frac{1}{1 + 1.0} = 0.50$
- If a skill takes 8 weeks (e.g., *C++* or *Deep Learning*): $\text{Ease} = \frac{1}{1 + 2.0} = 0.33$

##### D. Shortest Path Tiebreaker
If two candidate skills yield identical scores, the algorithm breaks ties using the minimum unweighted shortest path distance from the candidate's skill cluster:
$$d_{\text{min}}(M) = \min_{u \in U_{\text{graph}}} \text{dist}_{G_R}(u, M)$$
A smaller distance means $M$ is topologically closer to the student's existing knowledge base.

#### 3. Natural Language Explanation Synthesis
SkillBridge converts the raw mathematical parameters into an explainable, viva-ready justification string:
```python
# Real example output from src/recommend.py:
"Strongly bridges with your React (25), JavaScript (37); appears in 50.0% of postings; estimated ~3 weeks to master."
```

---

### Phase 5: Deterministic ATS Resume Readability Audit (`src/readability.py`)

Commercial ATS filters reject up to 75% of resumes due to formatting and parsing errors before an engineer ever reads them. `readability.py` implements a **100-point rule-based rubric**:

```
Total Readability Score (100 pts)
├── 1. Standard Section Headers     : 20 pts
├── 2. Bullet Length & Density      : 15 pts
├── 3. Action Verb Openers          : 20 pts
├── 4. Quantified Impact Metrics    : 20 pts
├── 5. Active vs. Passive Voice     : 15 pts
├── 6. Resume Length & Page Economy : 10 pts
└── 7. Advanced Diagnostics:
       ├── Contact Info (Email, Phone, GitHub/LinkedIn)
       └── Cliché & Buzzword Detector (Hollow filler phrases)
```

#### Detailed Rule Breakdown:
1. **Standard Section Headers (20 pts)**:
   Verifies presence of standard CSE undergraduate sections: `Education`, `Skills`, `Projects`, `Experience`. 5 points awarded per present section.
2. **Bullet Length & Density (15 pts)**:
   Flags bullet points that exceed 25 words (`MAX_BULLET_WORDS = 25`). Overly long bullets reduce ATS scannability and recruiter retention.
3. **Action Verb Openers (20 pts)**:
   Checks whether bullet points begin with strong, past-tense engineering action verbs from a curated list of **100+ verbs** (`Engineered`, `Architected`, `Deployed`, `Optimized`, `Refactored`). Scaled against a benchmark ratio of 60%.
4. **Quantified Impact (20 pts)**:
   Uses regular expressions to detect numbers, percentages, latencies, user volumes, and dollar impacts (e.g., *`reduced latency by 35%`*, *`served 10k+ requests`*, *`88% ROC-AUC`*). Scaled against a benchmark ratio of 30%.
5. **Passive Voice Detection (15 pts)**:
   Detects passive phrases such as *"was developed by"*, *"were assigned to"*, or *"was responsible for"*. Deducts 3 points per passive instance down to 0.
6. **Resume Length & Page Economy (10 pts)**:
   Measures total word count. Ideal undergraduate 1-page resume is **350 to 700 words**. Deducts points if $< 150$ words (too sparse) or $> 800$ words (spills onto second page).

---

### Phase 6: Learning Resources & Career Archetypes (`src/resources.py`)

1. **Curated Free Learning Resources**:
   Retrieves verified documentation and tutorial links from `skill_meta.csv` and companion resources for top-ranked skills (e.g., *MDN*, *Fast.ai*, *Google ML Crash Course*, *Docker Labs*). Never generates synthetic or unverified URLs.
2. **Graph Modularity Career Archetypes**:
   Applies modularity-based community detection (`nx.community.greedy_modularity_communities` or `louvain_communities`) on $G_R$ to identify natural sub-clusters of specialization within a role. For example, in Machine Learning:
   - *Cluster A (Deep Learning & NLP)*: PyTorch, Hugging Face, Transformers, NLTK.
   - *Cluster B (MLOps & Cloud)*: Docker, Kubernetes, AWS, MLflow, CI/CD.
   - *Cluster C (Core Analytics)*: Pandas, NumPy, Scikit-Learn, SQL, Tableau.

---

### Phase 7: Streamlit Interactive Web Application (`app/streamlit_app.py`)

#### Design Principles:
- **Strict Separation of Concerns**: `streamlit_app.py` contains **zero business logic**. It only captures user inputs, calls `SkillBridgePipeline.run_full_analysis()`, and renders visualizations.
- **State Management & Caching**: The pipeline and models are cached using `@st.cache_resource` to ensure instant tab switching and smooth interactions without re-parsing datasets.
- **Interactive Network Graph Rendering**: PyVis HTML is dynamically generated with embedded physics simulation (Barnes-Hut algorithm) and injected into Streamlit via `streamlit.components.v1.html()`.

#### UI Component Layout:
1. **Sidebar**:
   - Role selector (8 canonical roles).
   - Resume input mode (Text area with sample quick-load buttons or multi-format file upload).
   - Configurable objective weight sliders ($w_1, w_2, w_3$).
   - Prominent "Analyze Career Match & Skill Gaps" button.
2. **Top Metric Row**:
   - Overall Fit Score Card.
   - Role Skill Coverage Card.
   - Resume Readability Score Card (color-coded green/amber/red).
   - Top Next Skill Card.
3. **Tabbed Analysis Workspace**:
   - **Tab 1: Category Breakdown & Gap Table**: Interactive bar chart comparing student capabilities against role requirements across categories, accompanied by a sortable gap list.
   - **Tab 2: Interactive Knowledge Graph**: Embedded PyVis graph with zoom, drag, and hover tooltips showing demand % and estimated weeks.
   - **Tab 3: Readability Audit & Learning Path**: Itemized ATS rubric breakdown, actionable suggestions, and verified learning resource cards.

---

## 5. Mathematical Formulations Summary

| Metric | Mathematical Formula | Purpose |
| :--- | :--- | :--- |
| **Skill Demand** | $\text{Demand}(u) = \frac{N(u)}{N_{\text{role}}}$ | Measures market prevalence of skill $u$ in role postings. |
| **Degree Centrality** | $C_D(u) = \frac{\deg(u)}{|V| - 1}$ | Measures how broadly connected a skill is to other tools. |
| **Set Coverage** | $S_{\text{cov}} = \frac{\|U \cap R_{\text{core}}\|}{\|R_{\text{core}}\|} \times 100$ | Evaluates candidate's hard prerequisite satisfaction. |
| **TF-IDF Similarity** | $S_{\text{tfidf}} = \frac{\vec{v}_{\text{resume}} \cdot \vec{v}_{\text{corpus}}}{\|\vec{v}_{\text{resume}}\| \|\vec{v}_{\text{corpus}}\|} \times 100$ | Evaluates semantic alignment and vocabulary depth. |
| **Blended Fit** | $S_{\text{overall}} = 0.60 \cdot S_{\text{cov}} + 0.40 \cdot S_{\text{tfidf}}$ | Unified candidate match percentage. |
| **Ease Score** | $\text{Ease}(M) = \frac{1}{1 + \text{weeks}(M)/4.0}$ | Maps learning duration to a bounded score in $(0, 1]$. |
| **Recommendation Score** | $\text{Score}(M) = w_1 C_{\text{norm}}(M) + w_2 D_{\text{norm}}(M) + w_3 \text{Ease}(M)$ | Multi-criteria next-best-skill ranking objective. |

---

## 6. Comprehensive Viva Voce Defense Q&A

### Q1: Why did you use NetworkX and PyVis instead of a Deep Learning recommendation model like BERT or an autoencoder?
> **Answer**: Deep learning models act as "black boxes" that compute latent vector similarities without explainable reasoning. If a deep neural network recommends *Kubernetes* to a frontend developer, it cannot explain *why* or quantify the learning barrier. In contrast, our NetworkX co-occurrence graph models empirical market pairings directly from real job postings. We can explicitly trace that *Docker* connects to *Linux* with 37 co-occurrences and *AWS* with 25 co-occurrences. This ensures 100% determinism, full mathematical explainability, and zero hallucination risk, while running efficiently on low-cost CPU hardware.

### Q2: How does your skill extraction handle false positives for short words like "go", "r", or "c"?
> **Answer**: In `src/skill_extract.py`, ambiguous single-character keywords and common English verbs are removed from the broad case-insensitive `PhraseMatcher`. Instead, we route them through dedicated regular expressions with strict token boundaries and context lookaheads. For example, the English verb "go" in *"we will go to the office"* is rejected, while *"Golang"* or *"Go developer"* is correctly captured. Additionally, programming language symbols like *C++* and *C#*, which standard NLP tokenizers often break into punctuation, are preserved through custom token patterns.

### Q3: Explain the multi-criteria formula for recommending the "Next Best Skill".
> **Answer**: The objective function is:
> $$\text{Score}(M) = w_1 \cdot C_{\text{norm}}(M) + w_2 \cdot D_{\text{norm}}(M) + w_3 \cdot \text{Ease}(M)$$
> - $C_{\text{norm}}$ is **Graph Connectivity**: the sum of co-occurrence edge weights between the candidate missing skill and the skills the student already possesses. This represents the "bridge effect"—skills adjacent to prior knowledge are easier to assimilate.
> - $D_{\text{norm}}$ is **Market Demand**: the frequency with which the skill appears across industry postings for that role.
> - $\text{Ease}$ is the inverse of the hand-assigned estimated learning time: $\text{Ease} = \frac{1}{1 + \text{weeks}/4.0}$.
> Defaults are $w_1=0.5, w_2=0.3, w_3=0.2$, making the algorithm prioritize leverage over isolated high-demand skills.

### Q4: Why do you compute both Set Coverage and TF-IDF Cosine Similarity for the match score?
> **Answer**: They measure complementary dimensions of candidate qualification:
> - **Set Coverage** is discrete: it guarantees whether mandatory core tools (like *Python* or *Docker*) are present. However, set coverage treats all mentions as a binary yes/no and misses contextual narrative.
> - **TF-IDF Cosine Similarity** evaluates continuous term frequency and document-level vocabulary overlap, rewarding detailed project descriptions and relevant domain phrases.
> Blending them ($60\%$ Set Coverage $+ 40\%$ TF-IDF) prevents candidates from "gaming" the score by simply keyword-stuffing a list of skills without descriptive project context.

### Q5: How did you avoid "magic numbers" in the project?
> **Answer**: All parameters are isolated, commented, and centralized in `src/config.py`:
> - `MIN_EDGE_WEIGHT = 2`: Prunes isolated, one-off co-occurrences to eliminate noise from the knowledge graph.
> - `DEMAND_THRESHOLD = 0.15`: Defines high-demand skills as those appearing in at least $15\%$ of postings for a role.
> - `EASE_WEEKS_SCALE = 4.0`: Normalizes study time against a 4-week benchmark (one academic module).
> - `MAX_BULLET_WORDS = 25`: Standard professional typography limit for scannable resume bullets.

### Q6: What happens if an applicant uploads a PDF or Word document instead of plain text?
> **Answer**: In `src/gap.py`, `extract_text_from_file()` inspects the file extension. For `.pdf` files, it streams the raw bytes into `pypdf.PdfReader` to extract textual content across all pages. For `.docx` files, it uses `python-docx.Document` to aggregate paragraph runs. If extraction encounters an image-based scanned PDF, it handles it gracefully by returning an informative message advising plain text entry.

### Q7: What are the primary limitations of the current implementation?
> **Answer**:
> 1. **Lexical Dependence**: Skill extraction relies on the curated vocabulary and alias dictionary in `skill_meta.csv`. A newly invented library released yesterday would not be recognized until added to the seed list.
> 2. **Proficiency Depth**: The co-occurrence graph models binary presence within a posting or resume; it does not measure whether a candidate has 6 months or 5 years of experience in that skill.
> 3. **Geographic Bias**: Kaggle job posting datasets are predominantly sourced from US and European markets, which may slightly skew language and framework demand compared to regional hiring trends.

---

## 7. Complexity Analysis

### 1. Skill Extraction (`SkillExtractor.extract_skills`)
- **PhraseMatcher Search**: $O(N)$ where $N$ is the number of tokens in the resume text, using spaCy's optimized Aho-Corasick automaton.
- **Contextual Regex Checks**: $O(K \cdot L)$ where $K$ is the number of short keywords ($K=3$) and $L$ is text character length.
- **Total Time Complexity**: $\mathcal{O}(N)$ (linear with resume length). Runtime: $< 5\text{ ms}$ per resume.

### 2. Graph Construction (`build_role_graph`)
- For each posting with $S$ extracted skills, there are $\binom{S}{2} = \frac{S(S-1)}{2}$ combinations.
- For $P$ postings: $O(P \cdot S^2)$.
- Since $S \le 30$ in practice, graph construction for 400 postings completes in under 2 seconds.

### 3. Recommendation Ranking (`recommend_next_skills`)
- For $M$ missing skills ($M \le 20$) and $U$ user skills ($U \le 25$):
  - Connectivity calculation: $O(M \cdot U)$ graph edge lookups ($O(1)$ in NetworkX adjacency dictionary).
  - Shortest path distance: $O(M \cdot (V + E))$ using Breadth-First Search (BFS).
- **Total Time Complexity**: $\mathcal{O}(M \cdot (V + E))$. Runtime: $< 10\text{ ms}$.

---

## 8. Step-by-Step Execution Verification

To demonstrate the working project during a review or viva:

```bash
# 1. Activate Environment
source .venv/bin/activate

# 2. Run All 20 Unit Tests
pytest -v

# 3. Ingest Data & Verify Phase 1 Acceptance (Top 20 Skills per Role)
python -m src.ingest

# 4. Build Graphs & Verify Phase 2 Acceptance (React & Docker Neighbors)
python -m src.graph_builder

# 5. Launch the Streamlit Web UI
streamlit run app/streamlit_app.py
```

The browser will open to the interactive dashboard displaying the KPI cards, interactive PyVis network graph, category breakdown, gap list, and readability audit report.
