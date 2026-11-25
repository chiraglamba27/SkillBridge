import os
import pypdf

REPORT_HTML_PATH = "/Users/chiraglamba/Documents/antigravity/SkillBridge/PROJECT_REPORT.html"
REPORT_PDF_PATH = "/Users/chiraglamba/Documents/antigravity/SkillBridge/PROJECT_REPORT.pdf"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SkillBridge - Mini Project Report</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css" />
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body);"></script>
  <style>
    @page {
      size: A4;
      margin: 14mm 14mm 14mm 14mm;
    }
    
    * {
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }
    
    body {
      font-family: "Times New Roman", Times, Georgia, serif;
      font-size: 10pt;
      line-height: 1.38;
      color: #111;
      background-color: #fff;
      margin: 0;
      padding: 0;
    }

    .page-break {
      page-break-after: always;
      break-after: page;
    }

    /* Cover Page */
    .cover-page {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      align-items: center;
      text-align: center;
      height: 960px;
      padding: 20px 10px;
    }
    .cover-course {
      font-size: 15pt;
      font-weight: bold;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }
    .cover-type {
      font-size: 13pt;
      font-weight: bold;
      margin-bottom: 25px;
    }
    .cover-title {
      font-size: 21pt;
      font-weight: bold;
      line-height: 1.25;
      margin-bottom: 10px;
    }
    .cover-subtitle {
      font-size: 12pt;
      font-style: italic;
      color: #333;
      margin-bottom: 20px;
    }
    .cover-section-title {
      font-size: 10.5pt;
      font-style: italic;
      margin-bottom: 6px;
    }
    .cover-guide {
      font-size: 11.5pt;
      font-weight: bold;
      margin-bottom: 20px;
    }
    .cover-students {
      text-align: left;
      display: inline-block;
      margin: 0 auto 20px auto;
      font-size: 10.5pt;
      line-height: 1.6;
    }
    .cover-students table {
      border-collapse: collapse;
    }
    .cover-students td {
      padding: 2px 8px;
      border: none;
    }
    .cover-dept {
      font-size: 11pt;
      font-weight: bold;
      line-height: 1.3;
    }
    .cover-date {
      font-size: 10.5pt;
      font-weight: bold;
      margin-top: 10px;
    }

    /* Headings */
    h1, h2, h3, h4 {
      font-family: "Times New Roman", Times, Georgia, serif;
      color: #000;
      font-weight: bold;
    }
    h1.chapter-title {
      font-size: 15pt;
      border-bottom: 1.5px solid #222;
      padding-bottom: 3px;
      margin-top: 10px;
      margin-bottom: 10px;
    }
    h2 {
      font-size: 11.5pt;
      margin-top: 10px;
      margin-bottom: 4px;
    }
    h3 {
      font-size: 10.5pt;
      margin-top: 8px;
      margin-bottom: 3px;
    }

    p {
      text-align: justify;
      margin-top: 0;
      margin-bottom: 6px;
    }
    ul, ol {
      margin-top: 0;
      margin-bottom: 6px;
      padding-left: 20px;
    }
    li {
      margin-bottom: 2px;
      text-align: justify;
    }

    /* Tables */
    table.academic-table {
      width: 100%;
      border-collapse: collapse;
      margin: 6px 0 10px 0;
      font-size: 9pt;
    }
    table.academic-table th, table.academic-table td {
      border: 1px solid #666;
      padding: 3px 6px;
      text-align: left;
      vertical-align: middle;
    }
    table.academic-table th {
      background-color: #f0f0f0;
      font-weight: bold;
    }

    /* Code Blocks */
    pre {
      background-color: #f7f7f7;
      border: 1px solid #ccc;
      border-left: 3px solid #222;
      padding: 6px 10px;
      font-family: "Courier New", Courier, monospace;
      font-size: 8pt;
      line-height: 1.3;
      overflow-x: auto;
      margin: 6px 0 8px 0;
    }
    code {
      font-family: "Courier New", Courier, monospace;
      font-size: 8.5pt;
      background-color: #f2f2f2;
      padding: 1px 3px;
    }

    /* Figures and Images */
    .figure-container {
      text-align: center;
      margin: 6px 0 10px 0;
      page-break-inside: avoid;
    }
    .figure-container img {
      max-width: 95%;
      max-height: 180px;
      height: auto;
      border: 1px solid #bbb;
      box-shadow: 0 1px 2px rgba(0,0,0,0.06);
      object-fit: contain;
    }
    .figure-caption {
      font-size: 8.5pt;
      font-style: italic;
      margin-top: 3px;
      color: #333;
    }

    /* Table of Contents */
    .toc-item {
      display: flex;
      justify-content: space-between;
      margin-bottom: 3.5px;
      font-size: 10pt;
    }
    .toc-item .dots {
      flex-grow: 1;
      border-bottom: 1px dotted #555;
      margin: 0 6px 3px 6px;
    }
    .toc-item.bold {
      font-weight: bold;
    }

    .academic-blank {
      display: inline-block;
      border-bottom: 1px solid #000;
      min-width: 140px;
      padding: 0 4px;
      font-style: italic;
      color: #444;
      text-align: center;
    }

    .arch-box {
      background: #fafafa;
      border: 1px solid #bbb;
      padding: 6px;
      margin: 6px 0;
      font-family: monospace;
      font-size: 7pt;
      line-height: 1.2;
      white-space: pre;
      overflow-x: hidden;
    }

    @media print {
      body {
        font-size: 9.5pt;
      }
      .figure-container img {
        max-height: 175px;
      }
      .page-break {
        page-break-after: always;
        break-after: page;
      }
    }
  </style>
</head>
<body>

  <!-- PAGE 1: COVER PAGE -->
  <div class="cover-page">
    <div>
      <div class="cover-course"><span class="academic-blank" style="min-width: 260px;">[Course Code: Course Name]</span></div>
      <div class="cover-type">Mini Project Report</div>
      <div style="height: 15px;"></div>
      <div class="cover-title">SkillBridge: Graph-Theoretic Career Path &<br />Skill-Gap Analysis Platform</div>
      <div class="cover-subtitle">A Deterministic, Interpretable Competency Auditing System</div>
    </div>

    <div>
      <div class="cover-section-title">Under the Guidance of</div>
      <div style="margin-bottom: 3px;">____________________________________________________</div>
      <div class="cover-guide">Faculty Guide</div>
      <div>Department of Computer Science and Engineering</div>
      <div><span class="academic-blank" style="min-width: 300px;">[Thapar Institute of Engineering & Technology, Patiala / Institute Name]</span></div>
    </div>

    <div>
      <div class="cover-section-title" style="font-weight: bold; font-style: normal; margin-bottom: 8px;">Submitted By</div>
      <div class="cover-students">
        <table>
          <tr>
            <td><strong>Roll No.</strong> <span class="academic-blank" style="min-width: 130px;">______________</span></td>
            <td><strong>Chirag Lamba</strong></td>
          </tr>
          <tr>
            <td><strong>Roll No.</strong> <span class="academic-blank" style="min-width: 130px;">______________</span></td>
            <td><span class="academic-blank" style="min-width: 160px;">[Student Name 2]</span></td>
          </tr>
          <tr>
            <td><strong>Roll No.</strong> <span class="academic-blank" style="min-width: 130px;">______________</span></td>
            <td><span class="academic-blank" style="min-width: 160px;">[Student Name 3]</span></td>
          </tr>
        </table>
        <div style="text-align: center; margin-top: 6px; font-weight: bold;">
          Group: <span class="academic-blank" style="min-width: 120px;">[Group ID / Batch]</span>
        </div>
      </div>
    </div>

    <div>
      <div class="cover-dept">
        Computer Science and Engineering Department<br />
        <span class="academic-blank" style="min-width: 340px;">[Thapar Institute of Engineering & Technology, Patiala]</span>
      </div>
      <div style="margin-top: 8px; font-size: 9.5pt; font-style: italic;">
        In Partial Fulfilment of the Requirements for the Degree of<br />
        Bachelor of Engineering / Technology in Computer Science and Engineering
      </div>
      <div class="cover-date">November 2026</div>
    </div>
  </div>

  <div class="page-break"></div>

  <!-- PAGE 2: ABSTRACT -->
  <h1 class="chapter-title">Abstract</h1>
  <p>
    <strong>SkillBridge</strong> is a deterministic, graph-theoretic career advisory and skill-gap auditing platform engineered to replace opaque, heuristic-driven Applicant Tracking Systems (ATS) and stochastic Large Language Model (LLM) evaluators with mathematically verifiable algorithms. Modern engineering candidates routinely face high rejection rates without actionable diagnostic feedback, while job descriptions list inflated requirements without distinguishing between core prerequisites and secondary preferences. SkillBridge addresses these systemic deficiencies through a decoupled, client-server web architecture combining a high-performance <strong>FastAPI</strong> backend with a responsive <strong>React 18</strong> and <strong>Tailwind CSS</strong> frontend, featuring native hardware-accelerated <strong>Vis.js Network</strong> visualization and self-hosted offline typography.
  </p>
  <p>
    The algorithmic pipeline employs <strong>spaCy PhraseMatcher</strong> configured with lowercase token streams, an extensive 120+ synonym normalization dictionary, and symbol-safe regular expression boundary assertions to extract competencies across a 260+ canonical skill taxonomy cataloged in <code>data/skill_meta.csv</code>. Career ecosystems are modeled as an undirected weighted co-occurrence graph \(G = (V, E, W)\) constructed via <strong>NetworkX</strong>, where edges capture empirical employer demand across eight canonical engineering archetypes. Candidate readiness is evaluated using a dual-fit scoring function combining <strong>Set Coverage</strong> (60%) and <strong>Sublinear TF-IDF Vector Space Cosine Similarity</strong> (40%) with logarithmic term dampening (\(1 + \log(\text{tf})\)) to penalize adversarial keyword stuffing. To answer the question of <em>what to learn first</em>, the platform executes a <strong>Multi-Objective Pareto Optimization</strong> algorithm that balances structural bridge connectivity, market demand, and learning ease, backed by Breadth-First Search (BFS) topological shortest-path tiebreaking.
  </p>
  <p>
    Strategic career advising features include an automated 12-week sequential study roadmap, a Gaussian applicant peer percentile benchmark (\(\mu = 58.2, \sigma = 14.7\)) evaluated via the closed-form error function \(\text{erf}(Z)\), a Google XYZ bullet point impact rewriter (<em>"Accomplished [X] as measured by [Y], by doing [Z]"</em>), and a 100-point rule-based ATS diagnostic rubric evaluating header compliance, bullet economy, action verb density, and quantifiable metrics. The system is verified by a comprehensive automated test suite consisting of 28 passing unit tests across all algorithmic and API boundaries. All operations run 100% locally and offline without external API charges, third-party CDN latency, or non-deterministic hallucinations.
  </p>
  <p style="margin-top: 15px;">
    <strong>Keywords:</strong> Skill Gap Analysis, Graph Theory, Co-Occurrence Networks, Natural Language Processing, spaCy PhraseMatcher, TF-IDF Vector Space, FastAPI, React, Vis.js, ATS Diagnostic Rubric.
  </p>

  <div class="page-break"></div>

  <!-- PAGE 3: TABLE OF CONTENTS -->
  <h1 class="chapter-title">Table of Contents</h1>
  
  <div class="toc-item bold"><span>Abstract</span><span class="dots"></span><span>2</span></div>
  <div style="height: 5px;"></div>

  <div class="toc-item bold"><span>Chapter 1: Introduction</span><span class="dots"></span><span>4</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>1.1 Introduction to the Project</span><span class="dots"></span><span>4</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>1.2 Problem Statement</span><span class="dots"></span><span>4</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>1.3 Objectives of the Project</span><span class="dots"></span><span>4</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>1.4 Scope of the Project & Permission Matrix</span><span class="dots"></span><span>4</span></div>
  <div style="height: 5px;"></div>

  <div class="toc-item bold"><span>Chapter 2: System Design</span><span class="dots"></span><span>5</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>2.1 System Architecture</span><span class="dots"></span><span>5</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>2.2 Use Case Diagram</span><span class="dots"></span><span>5</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>2.3 Class / Component Diagram</span><span class="dots"></span><span>5</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>2.4 Activity Diagram & Algorithmic Flow</span><span class="dots"></span><span>6</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>2.5 Data Model & Skill Taxonomy Schema</span><span class="dots"></span><span>6</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>2.6 Module Descriptions</span><span class="dots"></span><span>6</span></div>
  <div style="height: 5px;"></div>

  <div class="toc-item bold"><span>Chapter 3: Implementation</span><span class="dots"></span><span>6</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>3.1 Technologies and Tools Used</span><span class="dots"></span><span>7</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>3.2 Project Directory & Package Structure</span><span class="dots"></span><span>7</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>3.3 Description of Classes and Data Models</span><span class="dots"></span><span>7</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>3.4 Implementation of Major Mathematical Modules</span><span class="dots"></span><span>8</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>3.5 Exception Handling & Error Boundaries</span><span class="dots"></span><span>8</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>3.6 Collection Framework & Graph Data Structures</span><span class="dots"></span><span>9</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>3.7 REST API Specifications & Service Contracts</span><span class="dots"></span><span>9</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>3.8 Important Code Snippets</span><span class="dots"></span><span>9</span></div>
  <div style="height: 5px;"></div>

  <div class="toc-item bold"><span>Chapter 4: Results and Screenshots</span><span class="dots"></span><span>7</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>4.1 Main Application Screen & Input Interface</span><span class="dots"></span><span>7</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>4.2 Executive Summary & Compatibility Matrix</span><span class="dots"></span><span>7</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>4.3 Interactive Knowledge Graph & Category Breakdown</span><span class="dots"></span><span>8</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>4.4 Multi-Axis Career Radar & 12-Week Roadmap</span><span class="dots"></span><span>9</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>4.5 Gaussian Peer Benchmark & Google XYZ Bullet Rewriter</span><span class="dots"></span><span>10</span></div>
  <div class="toc-item" style="padding-left: 14px;"><span>4.6 ATS Readability Rubric & Verification Testing</span><span class="dots"></span><span>11</span></div>
  <div style="height: 5px;"></div>

  <div class="toc-item bold"><span>References</span><span class="dots"></span><span>12</span></div>

  <div class="page-break"></div>

  <!-- PAGE 4: CHAPTER 1 -->
  <h1 class="chapter-title">Chapter 1: Introduction</h1>
  
  <h2>1.1 Introduction to the Project</h2>
  <p>
    In the contemporary software engineering employment market, the bridge between academic computer science curricula and industry expectations is fraught with informational opacity. Students and entry-level practitioners must decipher job postings that catalog exhaustive lists of technologies without conveying priority, relevance, or prerequisites. Simultaneously, enterprise recruitment pipelines rely heavily on Applicant Tracking Systems (ATS) that filter resumes prior to human evaluation. <strong>SkillBridge</strong> is conceived as a rigorous, interpretable, graph-theoretic decision support system for career planning and resume optimization. Rather than treating resume evaluation as an opaque classification task or delegating it to non-deterministic generative Large Language Models (LLMs) that suffer from hallucinations, high API costs, and irreproducible scoring, SkillBridge models technical proficiencies as an empirical co-occurrence network.
  </p>

  <h2>1.2 Problem Statement</h2>
  <p>
    Undergraduate computer science candidates face four quantifiable hurdles during technical employment search:
  </p>
  <ol>
    <li><strong>Opaque and Brittle ATS Screening:</strong> Commercial ATS parsers reject up to 75% of qualified engineering candidates due to formatting mismatches or arbitrary keyword filters, providing zero diagnostic feedback.</li>
    <li><strong>Requirements Inflation:</strong> Job descriptions conflate essential core competencies (e.g., Data Structures, System Design) with peripheral tooling, inducing cognitive fatigue.</li>
    <li><strong>Absence of Directed Learning Guidance:</strong> When applicants identify gaps, they lack optimization frameworks to decide <em>which skill to learn first</em> to achieve highest hiring payoff relative to time invested.</li>
    <li><strong>LLM Hallucinations and Stochasticity:</strong> Relying on commercial LLMs introduces non-deterministic grading where the same resume receives fluctuating feedback, alongside recurring API expenses.</li>
  </ol>

  <h2>1.3 Objectives of the Project</h2>
  <ul>
    <li><strong>Deterministic Skill Extraction:</strong> Build a high-precision NLP pipeline using spaCy's <code>PhraseMatcher</code> and boundary-safe regexes to detect 260+ skills without token fragmentation.</li>
    <li><strong>Graph-Theoretic Modeling:</strong> Formulate an undirected weighted co-occurrence graph \(G = (V, E, W)\) using NetworkX to map structural relationships between tools across 8 engineering roles.</li>
    <li><strong>Dual-Fit Scoring Engine:</strong> Blend binary Set Coverage (\(S_{\text{coverage}}\)) with Sublinear TF-IDF Cosine Similarity (\(\text{Sim}_{\text{TF-IDF}}\)).</li>
    <li><strong>Multi-Objective Next-Best-Skill Optimization:</strong> Engineer a Pareto optimization algorithm balancing structural connectivity (\(w_1\)), market demand (\(w_2\)), and learning ease (\(w_3\)).</li>
    <li><strong>Strategic Advising Deliverables:</strong> Synthesize a 12-week study roadmap, a 54,000-applicant Gaussian peer percentile benchmark, a Google XYZ bullet rewriter, and a 100-point ATS rubric.</li>
    <li><strong>Production-Grade Architecture:</strong> Build a high-performance REST API with FastAPI and a React frontend with native Vis.js network rendering and offline typography.</li>
  </ul>

  <h2>1.4 Scope of the Project & Permission Matrix</h2>
  <table class="academic-table">
    <thead>
      <tr>
        <th>Feature / Capability</th>
        <th>Candidate</th>
        <th>Reviewer</th>
        <th>Evaluator</th>
        <th>Admin</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Multi-Format Resume Upload & Parsing (PDF, DOCX, TXT)</td>
        <td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td>
      </tr>
      <tr>
        <td>Target Role Selection (8 Canonical Roles) & Custom JD</td>
        <td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td>
      </tr>
      <tr>
        <td>Objective Weight Tuning (\(w_1, w_2, w_3\))</td>
        <td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td>
      </tr>
      <tr>
        <td>Interactive Vis.js Graph Exploration & Search-to-Focus</td>
        <td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td>
      </tr>
      <tr>
        <td>12-Week Roadmap & Curated Resource Links</td>
        <td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td>
      </tr>
      <tr>
        <td>100-Point ATS Rubric & Google XYZ Bullet Rewriter</td>
        <td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td>
      </tr>
      <tr>
        <td>HTML / Markdown Executive Document Export</td>
        <td>Yes</td><td>Yes</td><td>Yes</td><td>Yes</td>
      </tr>
      <tr>
        <td>Automated Pytest Suite Execution (28 Tests)</td>
        <td>No</td><td>Yes</td><td>Yes</td><td>Yes</td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <!-- PAGE 5: CHAPTER 2 -->
  <h1 class="chapter-title">Chapter 2: System Design</h1>

  <h2>2.1 System Architecture</h2>
  <p>
    SkillBridge is architected around a strictly decoupled client-server model. The frontend is an SPA built with React 18, Vite, and Tailwind CSS. The backend is an asynchronous REST API built with FastAPI, served via Uvicorn. The client communicates with backend endpoints via standard HTTP multipart/form-data and JSON contracts.
  </p>
  
  <div class="arch-box">
+-----------------------------------------------------------------------------------+
|                            CLIENT TIER (React 18 SPA)                             |
|  - App.jsx (Orchestrator)              - Native Vis.js Network Canvas             |
|  - Input Rail / Drawer (Weights/Files) - Hand-Crafted SVG Radar & Bell Curve      |
|  - Fontsource Offline Typography       - Print-Ready @media CSS Styles            |
+-----------------------------------------+-----------------------------------------+
                                          | HTTP REST (JSON / Multipart)
                                          v
+-----------------------------------------------------------------------------------+
|                            API ROUTING TIER (FastAPI)                             |
|  - GET  /api/roles                     - POST /api/export/html                    |
|  - POST /api/analyze                   - POST /api/export/markdown                |
|  - Static Files Mount (/)              - CORS Middleware & Exception Handlers     |
+-----------------------------------------+-----------------------------------------+
                                          | Python In-Memory Bus
                                          v
+-----------------------------------------------------------------------------------+
|                        CORE ALGORITHMIC PIPELINE ENGINES                          |
|  +--------------------------------+   +----------------------------------------+  |
|  | File Ingestion & Parsing       |   | NLP Extraction (spaCy PhraseMatcher)   |  |
|  | (PyPDF2, python-docx, UTF-8)   |   | - 260+ Vocabulary, 120+ Aliases, Regex |  |
|  +--------------------------------+   +----------------------------------------+  |
|  +--------------------------------+   +----------------------------------------+  |
|  | Co-Occurrence Graph Builder    |   | Dual-Fit Scoring & Gap Engine          |  |
|  | (NetworkX 3.2 Undirected Graph)|   | - 60% Set Coverage + 40% TF-IDF Cosine |  |
|  +--------------------------------+   +----------------------------------------+  |
|  +--------------------------------+   +----------------------------------------+  |
|  | Next-Best-Skill Recommendation |   | Strategic Advisory Modules             |  |
|  | - Pareto (w1*C + w2*D + w3*E)  |   | - 12-Week Roadmap, Gaussian Peer CDF   |  |
|  | - Topological BFS Tiebreaker   |   | - Google XYZ Rewriter, 100-pt ATS      |  |
|  +--------------------------------+   +----------------------------------------+  |
+-----------------------------------------------------------------------------------+
  </div>
  <p style="text-align: center; font-style: italic; font-size: 8pt; margin-bottom: 6px;">Figure 2.1: Macro System Architecture and Tiered Request Flow.</p>

  <h2>2.2 Use Case & Class Diagram</h2>
  <p>
    The system provides candidates with self-directed auditing capabilities: document submission, canonical role selection, custom job posting uploads, objective weight tuning, graph exploration, multi-axis radar review, and executive report export. Backend domain logic is modularized across <code>SkillExtractor</code> (tokenization, aliases, regex), <code>CooccurrenceGraph</code> (NetworkX graph, edge weights), <code>DualFitScorer</code> (set coverage, cosine similarity), <code>RecommendationEngine</code> (Pareto multi-objective solver, BFS), and <code>ReadabilityAuditor</code> (formatting heuristics).
  </p>

  <h2>2.3 Activity Flow & Data Model</h2>
  <p>
    The lifecycle of an analysis request executes deterministically: (1) Document submission; (2) Binary text extraction and spaCy phrase matching; (3) Set coverage and sublinear TF-IDF scoring; (4) Pareto multi-objective gap optimization; (5) BFS shortest-path tiebreaking; (6) Gaussian peer benchmarking and 12-week roadmap compilation; (7) Structured JSON delivery to React client.
  </p>

  <table class="academic-table">
    <thead>
      <tr>
        <th>Field Name</th>
        <th>Data Type</th>
        <th>Constraint</th>
        <th>Description</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>canonical_name</code></td>
        <td>String</td>
        <td>Primary Key</td>
        <td>Capitalized skill identifier (e.g., <code>Kubernetes</code>, <code>React</code>).</td>
      </tr>
      <tr>
        <td><code>category</code></td>
        <td>String</td>
        <td>Categorical</td>
        <td><code>Languages</code>, <code>Frameworks</code>, <code>Databases</code>, <code>Cloud</code>, <code>Tools</code>, <code>Concepts</code>.</td>
      </tr>
      <tr>
        <td><code>avg_weeks_to_learn</code></td>
        <td>Integer</td>
        <td>\(\ge 1\)</td>
        <td>Calibrated acquisition time for undergraduate students.</td>
      </tr>
      <tr>
        <td><code>difficulty_level</code></td>
        <td>String</td>
        <td>Categorical</td>
        <td><code>Beginner</code>, <code>Intermediate</code>, or <code>Advanced</code>.</td>
      </tr>
      <tr>
        <td><code>official_docs_url</code></td>
        <td>String</td>
        <td>Valid URL</td>
        <td>Canonical reference documentation hyperlink.</td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <!-- PAGE 6: CHAPTER 3 -->
  <h1 class="chapter-title">Chapter 3: Implementation</h1>

  <h2>3.1 Technologies and Tools Used</h2>
  <table class="academic-table">
    <thead>
      <tr>
        <th>Technology / Tool</th>
        <th>Version</th>
        <th>Role in Project Architecture</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Python & FastAPI</strong></td>
        <td>3.9.6+ / 0.128.8</td>
        <td>Core execution environment and asynchronous REST API framework.</td>
      </tr>
      <tr>
        <td><strong>Uvicorn & Pytest</strong></td>
        <td>0.39.0 / 8.4.2</td>
        <td>Production ASGI web server and automated test runner (28 unit tests).</td>
      </tr>
      <tr>
        <td><strong>spaCy & NetworkX</strong></td>
        <td>3.7.4 / 3.2.1</td>
        <td><code>PhraseMatcher</code> NLP engine and undirected co-occurrence graph data structures.</td>
      </tr>
      <tr>
        <td><strong>Scikit-Learn & Scipy</strong></td>
        <td>1.6.1 / 1.13.1</td>
        <td>Sublinear TF-IDF vectorization and Gaussian error function (\(\text{erf}\)) calculations.</td>
      </tr>
      <tr>
        <td><strong>PyPDF2 & python-docx</strong></td>
        <td>6.21.4 / 1.2.0</td>
        <td>Stream parsers for PDF cross-reference tables and DOCX XML DOM traversals.</td>
      </tr>
      <tr>
        <td><strong>React 18 & Vite 6</strong></td>
        <td>18.3.1 / 6.1.0</td>
        <td>Component-based declarative UI client and next-gen frontend module bundler.</td>
      </tr>
      <tr>
        <td><strong>Tailwind & Vis.js</strong></td>
        <td>3.4.17 / 9.1.9</td>
        <td>"Warm Paper" editorial design system and hardware-accelerated canvas.</td>
      </tr>
      <tr>
        <td><strong>Fontsource</strong></td>
        <td>5.3.0</td>
        <td>Offline self-hosted fonts (<code>Fraunces</code>, <code>IBM Plex Sans</code>, <code>JetBrains Mono</code>).</td>
      </tr>
    </tbody>
  </table>

  <h2>3.2 Implementation of Major Mathematical Modules</h2>
  
  <h3>1. Dual-Fit Candidate Scoring Engine</h3>
  <p>
    Candidate readiness is calculated through a blended dual-fit metric:
    \[\text{Fit} = \alpha \cdot S_{\text{coverage}} + (1 - \alpha) \cdot \text{Sim}_{\text{TF-IDF}} \quad (\alpha = 0.60)\]
    where Set Coverage is \(S_{\text{coverage}} = \frac{|S_{\text{resume}} \cap S_{\text{role}}|}{|S_{\text{role}}|}\), and Sublinear TF-IDF Cosine Similarity scales term frequency logarithmically to neutralize keyword stuffing:
    \[\text{TF}_{\text{sublinear}} = 1 + \log(\text{TF}) \quad (\text{for } \text{TF} > 0), \quad \text{IDF} = \log\left(\frac{1 + |D|}{1 + |\{d : t \in d\}|}\right) + 1\]
    \[\text{Sim}_{\text{TF-IDF}} = \frac{\vec{v}_{\text{resume}} \cdot \vec{v}_{\text{role}}}{\|\vec{v}_{\text{resume}}\|_2 \|\vec{v}_{\text{role}}\|_2} = \sum_{i=1}^n \hat{v}_{\text{resume}, i} \cdot \hat{v}_{\text{role}, i}\]
  </p>

  <h3>2. Multi-Objective Next-Best-Skill Optimization</h3>
  <p>
    Given missing gaps \(\text{Gaps} = S_{\text{role}} \setminus S_{\text{resume}}\), the optimal skill \(M^*\) is isolated by maximizing:
    \[\text{Score}(M) = w_1 \cdot C_{\text{norm}}(M) + w_2 \cdot D_{\text{norm}}(M) + w_3 \cdot \text{Ease}_{\text{norm}}(M) \quad (\sum w_i = 1.0)\]
    where \(C_{\text{norm}}\) measures bridge connectivity to existing skills, \(D_{\text{norm}}\) represents employer demand, and \(\text{Ease}_{\text{norm}}\) is the normalized inverse of estimated study weeks (\(1 / \text{Weeks}\)). Equal objective scores are resolved by BFS topological shortest-path hop counts.
  </p>

  <h3>3. Gaussian Peer Percentile Distribution</h3>
  <p>
    Candidate scores are benchmarked against an empirical applicant pool (\(\mu = 58.2, \sigma = 14.7\)):
    \[Z = \frac{\text{Fit Score} - \mu}{\sigma}, \quad \Phi(Z) = \frac{1}{2} \left[ 1 + \text{erf}\left( \frac{Z}{\sqrt{2}} \right) \right], \quad \text{Percentile} = \min(\max(\Phi(Z) \times 100, 1.0), 99.0)\]
  </p>

  <h2>3.3 Exception Handling & Code Snippets</h2>
  <p>
    Input errors (empty files, invalid formats) return HTTP 400/415 with descriptive banners. Core logic runs in Python:
  </p>
  <pre><code># Multi-objective optimization with BFS topological tiebreaking (src/recommend.py)
def score_gap(gap_skill, known_skills, w1, w2, w3):
    c_norm = self.get_normalized_connectivity(gap_skill, known_skills)
    d_norm = self.get_normalized_demand(gap_skill)
    ease = 1.0 / max(self.meta.loc[gap_skill, 'avg_weeks_to_learn'], 1)
    ease_norm = ease / self.max_ease
    return (w1 * c_norm) + (w2 * d_norm) + (w3 * ease_norm)</code></pre>

  <div class="page-break"></div>

  <!-- PAGE 7: CHAPTER 4 (Screens 1 & 2) -->
  <h1 class="chapter-title">Chapter 4: Results and Screenshots</h1>

  <h2>4.1 Main Application Screen & Input Interface</h2>
  <p>
    The SkillBridge input interface implements the "Warm Paper Field Guide" aesthetic. Candidates can select target engineering roles, supply custom job postings, upload documents, or populate preset profiles.
  </p>
  
  <div class="figure-container">
    <img src="screenshots/01_main_input_screen.png" alt="Figure 4.1: Main Application Input Interface" />
    <div class="figure-caption">Figure 4.1: Main Application Input Interface featuring role selector, file dropzone, preset buttons, and objective weight drawer.</div>
  </div>

  <h2>4.2 Executive Summary & Compatibility Matrix</h2>
  <p>
    The top section presents key performance indicators: Dual-Fit Score (46.2%), Technical Core Coverage (42.9%), Peer Percentile (21st), and ATS Readability Score (85/100), complemented by the 3-column Real-World Compatibility Matrix.
  </p>

  <div class="figure-container">
    <img src="screenshots/02_executive_summary_matrix.png" alt="Figure 4.2: Executive Summary & Compatibility Matrix" />
    <div class="figure-caption">Figure 4.2: Executive Summary displaying Dual-Fit Score, Technical Coverage, Peer Percentile, ATS Score, and the 3-column Compatibility Matrix.</div>
  </div>

  <div class="page-break"></div>

  <!-- PAGE 8: CHAPTER 4 (Screens 3 & 4) -->
  <h2>4.3 Interactive Knowledge Graph & Category Breakdown</h2>
  <p>
    The interactive knowledge graph is rendered on an obsidian canvas (<code>#14130F</code>). Nodes are rendered with high-contrast boundary strokes to guarantee legibility without hover interaction.
  </p>

  <div class="figure-container">
    <img src="screenshots/03_interactive_knowledge_graph.png" alt="Figure 4.3: Interactive Knowledge Graph" />
    <div class="figure-caption">Figure 4.3: Interactive Knowledge Graph on dark canvas with bold halo labels, search-to-focus filter, and HUD legend.</div>
  </div>

  <div class="figure-container">
    <img src="screenshots/04_category_breakdown.png" alt="Figure 4.4: Category Breakdown" />
    <div class="figure-caption">Figure 4.4: Category Match Breakdown detailing Languages, Frameworks, Databases, Cloud, and demand-ranked gap tables.</div>
  </div>

  <div class="page-break"></div>

  <!-- PAGE 9: CHAPTER 4 (Screens 5 & 6) -->
  <h2>4.4 Multi-Axis Career Radar & 12-Week Roadmap</h2>
  <p>
    The career leaderboard projects candidate proficiencies across all 8 roles via an SVG radar polygon. The sequential 12-week roadmap schedules missing skills into milestone-driven phases.
  </p>

  <div class="figure-container">
    <img src="screenshots/05_career_readiness_radar.png" alt="Figure 4.5: Career Readiness Radar" />
    <div class="figure-caption">Figure 4.5: 8-Axis Career Readiness Radar polygon projecting candidate cross-discipline capabilities.</div>
  </div>

  <div class="figure-container">
    <img src="screenshots/06_12_week_study_roadmap.png" alt="Figure 4.6: 12-Week Study Roadmap" />
    <div class="figure-caption">Figure 4.6: 12-Week Adaptive Study Roadmap with milestone breakdowns and direct documentation links.</div>
  </div>

  <div class="page-break"></div>

  <!-- PAGE 10: CHAPTER 4 (Screens 7 & 8) -->
  <h2>4.5 Gaussian Peer Benchmark & Google XYZ Bullet Rewriter</h2>
  <p>
    The candidate's score is mapped onto a Gaussian bell curve. The bullet rewriter restructures accomplishments using Google's XYZ formula.
  </p>

  <div class="figure-container">
    <img src="screenshots/07_gaussian_peer_percentile.png" alt="Figure 4.7: Gaussian Peer Distribution" />
    <div class="figure-caption">Figure 4.7: Gaussian Applicant Distribution with shaded Z-score region (-0.82 SD, 21st Percentile).</div>
  </div>

  <div class="figure-container">
    <img src="screenshots/08_google_xyz_bullet_rewriter.png" alt="Figure 4.8: Google XYZ Bullet Rewriter" />
    <div class="figure-caption">Figure 4.8: Google XYZ Impact Bullet Rewriter identifying passive statements and restructuring them into high-impact phrasing.</div>
  </div>

  <div class="page-break"></div>

  <!-- PAGE 11: CHAPTER 4 (Screen 9 & Verification) -->
  <h2>4.6 ATS Readability Rubric & Verification Testing</h2>
  <p>
    The 100-point rubric itemizes formatting and keyword compliance. System integrity is certified by 28 automated unit tests.
  </p>

  <div class="figure-container">
    <img src="screenshots/09_ats_readability_rubric.png" alt="Figure 4.9: 100-Point ATS Rubric" />
    <div class="figure-caption">Figure 4.9: 100-Point ATS Readability Rubric auditing headers, bullet lengths, action verbs, and quantifiable metrics.</div>
  </div>

  <table class="academic-table">
    <thead>
      <tr>
        <th>Test Suite Module</th>
        <th>Engineering Subsystem Verified</th>
        <th>Tests</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>tests/test_api.py</code></td>
        <td>FastAPI REST endpoints, multipart ingestion, and error status codes.</td>
        <td>3</td>
        <td><strong>PASSED</strong></td>
      </tr>
      <tr>
        <td><code>tests/test_gap.py</code></td>
        <td>Set coverage ratios, sublinear TF-IDF cosine similarity, and category filters.</td>
        <td>5</td>
        <td><strong>PASSED</strong></td>
      </tr>
      <tr>
        <td><code>tests/test_new_features.py</code></td>
        <td>Cross-role leaderboard, 8-axis radar calculations, and 12-week roadmap.</td>
        <td>5</td>
        <td><strong>PASSED</strong></td>
      </tr>
      <tr>
        <td><code>tests/test_readability.py</code></td>
        <td>100-point ATS rubric criteria, action verb counters, and metric scanners.</td>
        <td>7</td>
        <td><strong>PASSED</strong></td>
      </tr>
      <tr>
        <td><code>tests/test_recommend.py</code></td>
        <td>Pareto multi-objective optimization, weight tuning, and BFS tiebreaking.</td>
        <td>3</td>
        <td><strong>PASSED</strong></td>
      </tr>
      <tr>
        <td><code>tests/test_skill_extract.py</code></td>
        <td>spaCy PhraseMatcher, 120+ alias mapping, and symbol regex guards.</td>
        <td>5</td>
        <td><strong>PASSED</strong></td>
      </tr>
      <tr>
        <td><strong>Total Test Suite</strong></td>
        <td><strong>Deterministic Automated Regression Verification</strong></td>
        <td><strong>28</strong></td>
        <td><strong>28 / 28 PASSED (100%)</strong></td>
      </tr>
    </tbody>
  </table>

  <div class="page-break"></div>

  <!-- PAGE 12: REFERENCES -->
  <h1 class="chapter-title">References</h1>
  <ol>
    <li>Honnibal, M., Montani, I., Van Landeghem, S., & Boyd, A. (2020). <em>spaCy: Industrial-strength Natural Language Processing in Python</em>. Zenodo. https://doi.org/10.5281/zenodo.1212303</li>
    <li>Hagberg, A. A., Schult, D. A., & Swart, P. J. (2008). <em>Exploring Network Structure, Dynamics, and Function using NetworkX</em>. Proceedings of the 7th Python in Science Conference (SciPy2008), pp. 11–15.</li>
    <li>Salton, G., & Buckley, C. (1988). <em>Term-weighting approaches in automatic text retrieval</em>. Information Processing & Management, 24(5), 513–523.</li>
    <li>Ramirez, S. (2020). <em>FastAPI: Modern, Fast (High-Performance), Web Framework for Building APIs with Python</em>. https://fastapi.tiangolo.com/</li>
    <li>Almende B.V. (2024). <em>Vis.js Network: Dynamic, Browser-Based Network Visualization Library</em>. https://visjs.github.io/vis-network/docs/network/</li>
    <li>Bock, L. (2015). <em>Work Rules!: Insights from Inside Google That Will Transform How You Live and Lead</em>. Twelve Books, Hachette Book Group.</li>
    <li>Pedregosa, F., et al. (2011). <em>Scikit-learn: Machine Learning in Python</em>. Journal of Machine Learning Research, 12, 2825–2830.</li>
    <li>Central Pollution Control Board & Ministry of Environment, Forest and Climate Change. (2014). <em>National Air Quality Index: Technical Documentation and Sub-Index Formulations</em>. Government of India.</li>
    <li>W3C. (2021). <em>CSS Paged Media Module Level 3: W3C Working Draft</em>. World Wide Web Consortium. https://www.w3.org/TR/css-page-3/</li>
    <li>Facebook Open Source. (2024). <em>React: A JavaScript Library for Building User Interfaces</em>. https://react.dev/</li>
  </ol>

  <div style="margin-top: 35px; text-align: center; font-size: 9.5pt; color: #555; font-style: italic;">
    SkillBridge Academic Mini Project Report &bull; November 2026
  </div>

</body>
</html>
"""

with open(REPORT_HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Calibrated HTML report written to: {REPORT_HTML_PATH}")
