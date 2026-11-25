import React, { useState, useEffect } from 'react';
import {
  ArrowUpRight,
  ChevronDown,
  ChevronUp,
  Download,
  FileText,
  Printer,
  RotateCcw,
  Sliders,
  Upload,
  X,
} from 'lucide-react';
import KnowledgeGraph from './components/KnowledgeGraph';
import { RadarChart, BellCurve } from './components/AnalyticsCharts';

const DEFAULT_ROLES = [
  "Machine Learning Engineer",
  "Data Scientist",
  "Frontend Developer",
  "Backend Developer",
  "Full Stack Developer",
  "DevOps Engineer",
  "Cloud Engineer",
  "Data Engineer",
];

export default function App() {
  const [roles, setRoles] = useState(DEFAULT_ROLES);
  const [targetRole, setTargetRole] = useState("Machine Learning Engineer");
  const [useCustomJd, setUseCustomJd] = useState(false);
  const [customJdText, setCustomJdText] = useState("");
  const [inputMode, setInputMode] = useState("text"); // 'text' | 'file'
  const [resumeText, setResumeText] = useState("");
  const [uploadedFile, setUploadedFile] = useState(null);
  const [sampleResumes, setSampleResumes] = useState({});
  const [w1, setW1] = useState(0.50);
  const [w2, setW2] = useState(0.30);
  const [w3, setW3] = useState(0.20);
  const [showWeights, setShowWeights] = useState(false);
  const [showInputDrawer, setShowInputDrawer] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [activeSection, setActiveSection] = useState("network");
  const [results, setResults] = useState(null);

  // Sync section with URL hash
  useEffect(() => {
    const hash = window.location.hash.replace('#', '');
    if (['network', 'categories', 'radar', 'roadmap', 'peers', 'rewriter', 'rubric'].includes(hash)) {
      setActiveSection(hash);
    }
  }, []);

  const handleTabChange = (sectionId) => {
    setActiveSection(sectionId);
    window.location.hash = sectionId;
  };

  // Fetch roles and sample presets from backend
  useEffect(() => {
    fetch('/api/roles')
      .then((res) => {
        if (!res.ok) throw new Error("Could not reach backend API");
        return res.json();
      })
      .then((data) => {
        if (data.roles) setRoles(data.roles);
        if (data.sample_resumes) {
          setSampleResumes(data.sample_resumes);
          const initialText = data.sample_resumes.machine_learning || "";
          setResumeText(initialText);

          // Check for URL trigger ?demo=ml or ?sample=1
          const params = new URLSearchParams(window.location.search);
          if (params.get('demo') === 'ml' || params.get('sample') === '1') {
            setTimeout(() => {
              handleRunAnalysis();
            }, 300);
          }
        }
      })
      .catch((err) => {
        console.warn("Backend offline or running on another port:", err);
      });
  }, []);

  // Keyboard shortcut: Cmd/Ctrl + Enter to trigger audit
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        handleRunAnalysis();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  });

  const handleRunAnalysis = async () => {
    setLoading(true);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append("target_role", targetRole);
    if (useCustomJd && customJdText.trim()) {
      formData.append("custom_job_description", customJdText.trim());
    }
    formData.append("w1", w1.toString());
    formData.append("w2", w2.toString());
    formData.append("w3", w3.toString());

    if (inputMode === 'file' && uploadedFile) {
      formData.append("resume_file", uploadedFile);
    } else {
      formData.append("resume_text", resumeText);
    }

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error(`API responded with status ${response.status}`);
      }
      const data = await response.json();
      setResults(data);
      setShowInputDrawer(false);
    } catch (err) {
      console.error("Analysis failed:", err);
      setErrorMessage("Analysis failed. Please verify that the backend is running at http://127.0.0.1:8000.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadHtml = () => {
    if (!results || !results.html_report) return;
    const blob = new Blob([results.html_report], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SkillBridge_${targetRole.replace(/\s+/g, '_')}_Report.html`;
    a.click();
  };

  const handleDownloadMarkdown = () => {
    if (!results || !results.markdown_report) return;
    const blob = new Blob([results.markdown_report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SkillBridge_${targetRole.replace(/\s+/g, '_')}_Report.md`;
    a.click();
  };

  const handlePrint = () => {
    window.print();
  };

  const topRec = results && results.recommendations && results.recommendations.length > 0 ? results.recommendations[0] : null;
  const matchedCount = results?.gap_results?.matched_skills?.length || 0;
  const totalCount = results?.gap_results?.total_role_skills || 0;

  return (
    <div className="min-h-screen bg-paper text-ink font-sans">
      {/* Editorial Masthead Header */}
      <header className="border-b border-rule bg-surface no-print">
        <div className="max-w-6xl mx-auto px-6 py-4 flex flex-col md:flex-row md:items-baseline md:justify-between gap-2">
          <div className="flex items-baseline gap-3">
            <span className="font-serif text-2xl font-bold tracking-tight text-ink">SkillBridge</span>
          </div>

          <div className="flex items-center gap-3 text-xs font-mono">
            {results && (
              <>
                <button
                  onClick={handlePrint}
                  className="inline-flex items-center gap-1 text-ink hover:text-cobalt border-b border-transparent hover:border-cobalt pb-0.5"
                  title="Print document"
                >
                  <Printer className="h-3.5 w-3.5" />
                  Print Document
                </button>
                <span className="text-rule">|</span>
                <button
                  onClick={handleDownloadHtml}
                  className="inline-flex items-center gap-1 text-ink hover:text-cobalt border-b border-transparent hover:border-cobalt pb-0.5"
                >
                  <Download className="h-3.5 w-3.5" />
                  HTML
                </button>
                <span className="text-rule">|</span>
                <button
                  onClick={handleDownloadMarkdown}
                  className="inline-flex items-center gap-1 text-ink hover:text-cobalt border-b border-transparent hover:border-cobalt pb-0.5"
                >
                  <FileText className="h-3.5 w-3.5" />
                  Markdown
                </button>
                <span className="text-rule">|</span>
                <button
                  onClick={() => { setResults(null); setShowInputDrawer(false); }}
                  className="inline-flex items-center gap-1 text-ink-muted hover:text-ink pb-0.5"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  Reset
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Slim Re-configurable Bar (Appears when viewing report) */}
      {results && (
        <div className="sticky top-0 z-40 border-b border-rule bg-surface/95 backdrop-blur-sm px-6 py-2.5 no-print shadow-subtle">
          <div className="max-w-6xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-baseline gap-3 font-mono">
              <span className="text-ink-muted uppercase tracking-wider text-[11px]">Audit Target:</span>
              <span className="font-serif text-base font-bold text-ink">{targetRole}</span>
              <span className="text-ink-muted">
                ({results.gap_results.overall_match_score}% Fit, {matchedCount}/{totalCount} skills)
              </span>
            </div>

            <button
              onClick={() => setShowInputDrawer(!showInputDrawer)}
              className="inline-flex items-center gap-1.5 border border-rule bg-surface-raised px-3 py-1 font-mono text-xs text-ink hover:bg-paper transition"
            >
              <Sliders className="h-3.5 w-3.5 text-ink-muted" />
              <span>{showInputDrawer ? "Hide Input Panel" : "Edit Input & Parameters"}</span>
              {showInputDrawer ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            </button>
          </div>
        </div>
      )}

      {/* Primary Input Panel (Full Page or Collapsible Drawer) */}
      {(!results || showInputDrawer) && (
        <section className={`border-b border-rule bg-surface-raised ${results ? 'no-print shadow-lift' : ''}`}>
          <div className="max-w-6xl mx-auto px-6 py-8">
            <div className="max-w-3xl space-y-6">
              <div>
                <span className="font-mono text-xs uppercase tracking-widest text-ink-muted block mb-1">
                  Step 01 / Target Role
                </span>
                <h2 className="font-serif text-2xl font-normal text-ink mb-2">
                  Select Benchmark Career Target
                </h2>
                <div className="relative">
                  <select
                    value={targetRole}
                    onChange={(e) => setTargetRole(e.target.value)}
                    className="w-full border border-rule bg-paper px-3.5 py-2.5 text-sm font-mono text-ink focus:border-ink focus:outline-none rounded-none"
                  >
                    {roles.map((r) => (
                      <option key={r} value={r}>
                        {r}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Resume Ingestion */}
              <div>
                <div className="flex items-baseline justify-between mb-2">
                  <div>
                    <span className="font-mono text-xs uppercase tracking-widest text-ink-muted block mb-1">
                      Step 02 / Candidate Evidence
                    </span>
                    <h3 className="font-serif text-lg font-normal text-ink">
                      Provide Resume Text or Document
                    </h3>
                  </div>

                  <div className="flex border border-rule font-mono text-xs">
                    <button
                      onClick={() => setInputMode('text')}
                      className={`px-3 py-1 ${inputMode === 'text' ? 'bg-ink text-surface' : 'bg-surface text-ink hover:bg-paper'}`}
                    >
                      Plain Text
                    </button>
                    <button
                      onClick={() => setInputMode('file')}
                      className={`px-3 py-1 border-l border-rule ${inputMode === 'file' ? 'bg-ink text-surface' : 'bg-surface text-ink hover:bg-paper'}`}
                    >
                      File Upload
                    </button>
                  </div>
                </div>

                {inputMode === 'text' ? (
                  <div className="space-y-2">
                    <div className="flex gap-2 font-mono text-xs">
                      <span className="text-ink-muted py-0.5">Quick fill presets:</span>
                      <button
                        onClick={() => setResumeText(sampleResumes.machine_learning || "")}
                        className="border border-rule px-2 py-0.5 hover:border-ink text-ink"
                      >
                        Sample: ML Engineer
                      </button>
                      <button
                        onClick={() => setResumeText(sampleResumes.frontend || "")}
                        className="border border-rule px-2 py-0.5 hover:border-ink text-ink"
                      >
                        Sample: Frontend Dev
                      </button>
                    </div>
                    <textarea
                      value={resumeText}
                      onChange={(e) => setResumeText(e.target.value)}
                      rows={9}
                      placeholder="Paste plain text resume or list of technical projects and skills here..."
                      className="w-full border border-rule bg-paper p-3 text-xs font-mono leading-relaxed text-ink placeholder-ink-subtle focus:border-ink focus:outline-none rounded-none"
                    />
                  </div>
                ) : (
                  <div className="border border-dashed border-rule bg-paper p-8 text-center hover:border-ink transition">
                    <Upload className="mx-auto h-6 w-6 text-ink-muted mb-2" />
                    <input
                      type="file"
                      accept=".pdf,.docx,.txt"
                      onChange={(e) => setUploadedFile(e.target.files ? e.target.files[0] : null)}
                      className="hidden"
                      id="resume-file-input"
                    />
                    <label htmlFor="resume-file-input" className="cursor-pointer font-mono text-xs text-cobalt underline">
                      {uploadedFile ? uploadedFile.name : "Select PDF, DOCX, or plain text file"}
                    </label>
                    <p className="font-mono text-[11px] text-ink-muted mt-1">
                      Deterministic textual extraction via pypdf and python-docx
                    </p>
                  </div>
                )}
              </div>

              {/* Real Job Posting Benchmark Toggle */}
              <div className="border-t border-rule pt-4">
                <label className="flex items-center gap-2 cursor-pointer font-mono text-xs text-ink">
                  <input
                    type="checkbox"
                    checked={useCustomJd}
                    onChange={(e) => setUseCustomJd(e.target.checked)}
                    className="accent-ink"
                  />
                  <span>Benchmark against a specific live job description</span>
                </label>

                {useCustomJd && (
                  <div className="mt-3">
                    <textarea
                      value={customJdText}
                      onChange={(e) => setCustomJdText(e.target.value)}
                      placeholder="Paste the full job requirements text here from LinkedIn, Indeed, etc..."
                      rows={5}
                      className="w-full border border-rule bg-paper p-3 text-xs font-mono text-ink placeholder-ink-subtle focus:border-ink focus:outline-none rounded-none"
                    />
                  </div>
                )}
              </div>

              {/* Scoring Weights Drawer */}
              <div className="border-t border-rule pt-3">
                <button
                  onClick={() => setShowWeights(!showWeights)}
                  className="flex items-center gap-1.5 font-mono text-xs text-ink-muted hover:text-ink"
                >
                  <Sliders className="h-3 w-3" />
                  <span>Objective recommendation weights ({Math.round(w1*100)}% Bridge, {Math.round(w2*100)}% Demand, {Math.round(w3*100)}% Ease)</span>
                  {showWeights ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                </button>

                {showWeights && (
                  <div className="mt-3 p-4 border border-rule bg-paper space-y-3 font-mono text-xs">
                    <div>
                      <div className="flex justify-between mb-1 text-ink">
                        <span>w1: Graph Connectivity (Bridge Effect)</span>
                        <span className="tabular-nums">{Math.round(w1 * 100)}%</span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.05"
                        value={w1}
                        onChange={(e) => setW1(parseFloat(e.target.value))}
                        className="w-full accent-ink"
                      />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1 text-ink">
                        <span>w2: Role Demand Frequency</span>
                        <span className="tabular-nums">{Math.round(w2 * 100)}%</span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.05"
                        value={w2}
                        onChange={(e) => setW2(parseFloat(e.target.value))}
                        className="w-full accent-ink"
                      />
                    </div>
                    <div>
                      <div className="flex justify-between mb-1 text-ink">
                        <span>w3: Acquisition Ease (1/Weeks)</span>
                        <span className="tabular-nums">{Math.round(w3 * 100)}%</span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.05"
                        value={w3}
                        onChange={(e) => setW3(parseFloat(e.target.value))}
                        className="w-full accent-ink"
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Execution Button */}
              {errorMessage && (
                <div className="border border-missing bg-missing-bg p-3 font-mono text-xs text-missing">
                  {errorMessage}
                </div>
              )}

              <div className="pt-2">
                <button
                  onClick={handleRunAnalysis}
                  disabled={loading}
                  className="inline-flex items-center gap-2 bg-ink text-paper px-6 py-3 font-mono text-xs uppercase tracking-wider font-semibold hover:bg-black transition disabled:opacity-50"
                >
                  {loading ? (
                    <>Processing Knowledge Graph & Evidence...</>
                  ) : (
                    <>
                      <span>Execute Skill Gap Audit</span>
                      <span className="text-paper/60 font-normal">⌘ ↵</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Report Viewport (Editorial Document Flow) */}
      {results && (
        <main className="max-w-6xl mx-auto px-6 py-10 space-y-12">
          {/* Section: Opening Plain-Language Verdict */}
          <section className="border-b border-rule pb-8">
            <span className="font-mono text-xs uppercase tracking-widest text-ink-muted block mb-2">
              Executive Evaluation Summary
            </span>
            <h2 className="font-serif text-3xl md:text-4xl text-ink font-normal leading-snug max-w-4xl">
              You cover <span className="font-semibold">{matchedCount}</span> of <span className="font-semibold">{totalCount}</span> core skills for <span className="font-semibold">{targetRole}</span>.
              {topRec && (
                <> Start with <span className="underline decoration-saffron decoration-2 font-semibold">{topRec.skill}</span>, about <span className="font-semibold">{topRec.est_weeks_to_learn} weeks</span> to acquire.</>
              )}
            </h2>

            {/* Honest Data Source Line */}
            <p className="font-mono text-[11px] text-ink-muted mt-3">
              Data source: {results.meta?.data_source || "Industry benchmark co-occurrence network (400 validated postings) and Kaggle 54k resume Gaussian distribution model."}
            </p>
          </section>

          {/* Section: Large Serif Figures & Thin Progress Rules */}
          <section className="grid grid-cols-2 md:grid-cols-4 gap-8 border-b border-rule pb-10">
            {/* Metric 1: Overall Fit */}
            <div>
              <div className="font-mono text-[11px] uppercase tracking-wider text-ink-muted mb-1">
                Overall Match
              </div>
              <div className="font-serif text-5xl md:text-6xl text-ink font-normal tabular-nums leading-none">
                {results.gap_results.overall_match_score}%
              </div>
              <div className="mt-3 h-1 w-full bg-rule-subtle overflow-hidden">
                <div
                  className="h-full bg-ink"
                  style={{ width: `${results.gap_results.overall_match_score}%` }}
                />
              </div>
              <p className="font-mono text-[11px] text-ink-muted mt-2">
                Blended 60% coverage + 40% TF-IDF
              </p>
            </div>

            {/* Metric 2: Core Coverage */}
            <div>
              <div className="font-mono text-[11px] uppercase tracking-wider text-ink-muted mb-1">
                Core Coverage
              </div>
              <div className="font-serif text-5xl md:text-6xl text-known font-normal tabular-nums leading-none">
                {results.gap_results.tech_coverage_pct || results.gap_results.set_coverage_score}%
              </div>
              <div className="mt-3 h-1 w-full bg-rule-subtle overflow-hidden">
                <div
                  className="h-full bg-known"
                  style={{ width: `${results.gap_results.tech_coverage_pct || results.gap_results.set_coverage_score}%` }}
                />
              </div>
              <p className="font-mono text-[11px] text-ink-muted mt-2">
                {matchedCount} of {totalCount} verified skills
              </p>
            </div>

            {/* Metric 3: Peer Percentile */}
            <div>
              <div className="font-mono text-[11px] uppercase tracking-wider text-ink-muted mb-1">
                Peer Standing
              </div>
              <div className="font-serif text-5xl md:text-6xl text-ink font-normal tabular-nums leading-none">
                {results.peer_benchmark.percentile}<span className="text-2xl text-ink-muted font-sans font-light">th</span>
              </div>
              <div className="mt-3 h-1 w-full bg-rule-subtle overflow-hidden">
                <div
                  className="h-full bg-cobalt"
                  style={{ width: `${results.peer_benchmark.percentile}%` }}
                />
              </div>
              <p className="font-mono text-[11px] text-ink-muted mt-2">
                Candidate pool Gaussian distribution
              </p>
            </div>

            {/* Metric 4: ATS Readability */}
            <div>
              <div className="font-mono text-[11px] uppercase tracking-wider text-ink-muted mb-1">
                ATS Readability
              </div>
              <div className="font-serif text-5xl md:text-6xl text-ink font-normal tabular-nums leading-none">
                {results.readability.readability_score}<span className="text-xl text-ink-muted font-mono font-light">/100</span>
              </div>
              <div className="mt-3 h-1 w-full bg-rule-subtle overflow-hidden">
                <div
                  className="h-full bg-saffron"
                  style={{ width: `${results.readability.readability_score}%` }}
                />
              </div>
              <p className="font-mono text-[11px] text-ink-muted mt-2">
                Deterministic 6-rule rubric
              </p>
            </div>
          </section>

          {/* Section: Priority Next Step Banner */}
          {topRec && (
            <section className="border border-rule bg-surface p-6">
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="inline-block h-3 w-3 rounded-full bg-saffron ring-2 ring-saffron/40"></span>
                    <span className="font-mono text-xs uppercase tracking-wider text-ink-muted">
                      Priority Next Step:
                    </span>
                    <span className="font-mono text-xs font-semibold px-2 py-0.5 border border-rule bg-paper text-ink">
                      {topRec.category}
                    </span>
                  </div>
                  <h3 className="font-serif text-2xl font-bold text-ink">
                    Start with {topRec.skill}
                  </h3>
                  <p className="text-sm text-ink-muted max-w-3xl leading-relaxed">
                    {topRec.reason}
                  </p>
                  <div className="flex flex-wrap gap-4 pt-1 font-mono text-xs text-ink">
                    <span>Combined Score: <b className="tabular-nums">{topRec.score}</b></span>
                    <span className="text-rule">•</span>
                    <span>Bridge Index: <b className="tabular-nums">{topRec.norm_connectivity}</b></span>
                    <span className="text-rule">•</span>
                    <span>Role Demand: <b className="tabular-nums">{(topRec.demand * 100).toFixed(1)}%</b></span>
                    <span className="text-rule">•</span>
                    <span>Estimated Study: <b className="tabular-nums">~{topRec.est_weeks_to_learn} weeks</b></span>
                  </div>
                </div>

                {results.resources[topRec.skill] && (
                  <div className="shrink-0 pt-2">
                    <a
                      href={results.resources[topRec.skill][0]?.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 border border-ink bg-ink text-surface px-4 py-2 font-mono text-xs hover:bg-black transition"
                    >
                      <span>Documentation Reference</span>
                      <ArrowUpRight className="h-3.5 w-3.5" />
                    </a>
                  </div>
                )}
              </div>
            </section>
          )}

          {/* Section: 3-Column Compatibility Matrix */}
          <section className="space-y-4">
            <h3 className="font-mono text-xs uppercase tracking-widest text-ink-muted">
              Evidence vs. Requirement Matrix
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Column 1: Matching */}
              <div className="border border-rule bg-surface p-5">
                <div className="flex items-baseline justify-between border-b border-rule pb-2 mb-3">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-full bg-known"></span>
                    <h4 className="font-serif text-lg font-bold text-ink">Verified Competencies</h4>
                  </div>
                  <span className="font-mono text-xs text-known font-semibold">
                    {matchedCount} Verified
                  </span>
                </div>
                <p className="text-xs text-ink-muted mb-3">Skills verified on your resume matching requirements:</p>
                <div className="flex flex-wrap gap-1.5 max-h-56 overflow-y-auto">
                  {results.gap_results.matched_skills.map((s) => (
                    <span
                      key={s}
                      className="inline-flex items-center gap-1 border border-known/30 bg-known-bg px-2 py-0.5 font-mono text-xs text-known font-medium"
                    >
                      <span className="h-1.5 w-1.5 rounded-full bg-known"></span>
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              {/* Column 2: Pending */}
              <div className="border border-rule bg-surface p-5">
                <div className="flex items-baseline justify-between border-b border-rule pb-2 mb-3">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-full border-2 border-missing bg-paper"></span>
                    <h4 className="font-serif text-lg font-bold text-ink">Missing Requirements</h4>
                  </div>
                  <span className="font-mono text-xs text-missing font-semibold">
                    {results.gap_results.missing_skills.length} Gaps
                  </span>
                </div>
                <p className="text-xs text-ink-muted mb-3">Prerequisites missing from candidate evidence:</p>
                <div className="flex flex-wrap gap-1.5 max-h-56 overflow-y-auto">
                  {results.gap_results.missing_skills.map((s) => (
                    <span
                      key={s}
                      className="inline-flex items-center gap-1 border border-dashed border-missing/40 bg-missing-bg px-2 py-0.5 font-mono text-xs text-missing font-medium"
                    >
                      <span className="h-1.5 w-1.5 rounded-full border border-missing"></span>
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              {/* Column 3: What to Cover First */}
              <div className="border border-rule bg-surface p-5">
                <div className="flex items-baseline justify-between border-b border-rule pb-2 mb-3">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2.5 w-2.5 rounded-full bg-saffron ring-2 ring-saffron/30"></span>
                    <h4 className="font-serif text-lg font-bold text-ink">Optimal First Bridge</h4>
                  </div>
                  <span className="font-mono text-xs text-saffron font-semibold">
                    ~{topRec ? topRec.est_weeks_to_learn : 0} wks
                  </span>
                </div>
                {topRec ? (
                  <div className="space-y-2">
                    <div className="font-serif text-2xl font-bold text-ink">{topRec.skill}</div>
                    <p className="text-xs text-ink-muted leading-relaxed">
                      Maximizes connectivity to your existing competencies while fulfilling {topRec.demand ? (topRec.demand*100).toFixed(0) : 75}% market demand.
                    </p>
                    {results.resources[topRec.skill] && (
                      <div className="pt-2">
                        <a
                          href={results.resources[topRec.skill][0]?.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 font-mono text-xs text-cobalt hover:underline"
                        >
                          <span>{results.resources[topRec.skill][0]?.title}</span>
                          <ArrowUpRight className="h-3 w-3" />
                        </a>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-xs text-known">All core requirements are fulfilled.</p>
                )}
              </div>
            </div>
          </section>

          {/* Section: Numbered Sticky Index (01-07) */}
          <nav className="sticky top-11 z-30 border-b border-rule bg-paper py-2 flex gap-4 overflow-x-auto no-print">
            {[
              { id: 'network', num: '01', label: 'Knowledge Graph' },
              { id: 'categories', num: '02', label: 'Category Gaps' },
              { id: 'radar', num: '03', label: 'Career Radar' },
              { id: 'roadmap', num: '04', label: '12-Week Roadmap' },
              { id: 'peers', num: '05', label: 'Peer Distribution' },
              { id: 'rewriter', num: '06', label: 'Bullet Rewriter' },
              { id: 'rubric', num: '07', label: 'Readability Rubric' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
                className={`flex items-baseline gap-1.5 pb-2 font-mono text-xs transition border-b-2 whitespace-nowrap ${
                  activeSection === tab.id
                    ? 'border-ink text-ink font-bold'
                    : 'border-transparent text-ink-muted hover:text-ink'
                }`}
              >
                <span className="text-[10px] text-ink-muted">{tab.num}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>

          {/* View 01: Knowledge Graph (The Hero) */}
          {activeSection === 'network' && (
            <section id="network" className="space-y-4 print-break-inside-avoid">
              <div className="flex items-baseline justify-between">
                <div>
                  <span className="font-mono text-xs uppercase tracking-widest text-ink-muted block mb-1">
                    Index 01 / Co-occurrence Map
                  </span>
                  <h3 className="font-serif text-2xl font-normal text-ink">
                    Empirical Co-occurrence Graph for {targetRole}
                  </h3>
                </div>
              </div>
              <KnowledgeGraph graphData={results.graph_data} targetRole={targetRole} />
            </section>
          )}

          {/* View 02: Category Gaps */}
          {activeSection === 'categories' && (
            <section id="categories" className="space-y-6 print-break-inside-avoid">
              <div>
                <span className="font-mono text-xs uppercase tracking-widest text-ink-muted block mb-1">
                  Index 02 / Categorical Distribution
                </span>
                <h3 className="font-serif text-2xl font-normal text-ink">
                  Skill Coverage Across Technical Disciplines
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Horizontal Category Rules */}
                <div className="border border-rule bg-surface p-6 space-y-4">
                  <h4 className="font-mono text-xs uppercase tracking-wider text-ink-muted mb-3">
                    Discipline Breakdown
                  </h4>
                  {Object.entries(results.gap_results.category_breakdown).map(([cat, val]) => (
                    <div key={cat} className="space-y-1">
                      <div className="flex justify-between font-mono text-xs">
                        <span className="text-ink font-semibold">{cat}</span>
                        <span className="text-ink-muted tabular-nums">
                          {val.match_pct}% ({val.matched_count}/{val.total_required})
                        </span>
                      </div>
                      <div className="h-1.5 w-full bg-rule-subtle overflow-hidden">
                        <div
                          className="h-full bg-ink"
                          style={{ width: `${val.match_pct}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {/* Demand-Ranked Missing Skills Table */}
                <div className="border border-rule bg-surface p-6">
                  <h4 className="font-mono text-xs uppercase tracking-wider text-ink-muted mb-3">
                    Missing Requirements Ranked by Market Frequency ({results.gap_results.gap_list.length})
                  </h4>
                  <div className="max-h-80 overflow-y-auto">
                    <table className="w-full text-left font-mono text-xs">
                      <thead className="border-b border-rule text-ink-muted">
                        <tr>
                          <th className="py-2 font-normal">Skill</th>
                          <th className="py-2 font-normal">Category</th>
                          <th className="py-2 font-normal">Demand</th>
                          <th className="py-2 font-normal">Est. Study</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-rule-subtle">
                        {results.gap_results.gap_list.map((g) => (
                          <tr key={g.skill} className="hover:bg-paper transition">
                            <td className="py-2 font-semibold text-ink">{g.skill}</td>
                            <td className="py-2 text-ink-muted">{g.category}</td>
                            <td className="py-2 text-ink tabular-nums">{(g.demand * 100).toFixed(1)}%</td>
                            <td className="py-2 text-ink-muted tabular-nums">~{g.est_weeks_to_learn} wks</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* View 03: Career Radar */}
          {activeSection === 'radar' && (
            <section id="radar" className="space-y-6 print-break-inside-avoid">
              <div>
                <span className="font-mono text-xs uppercase tracking-widest text-ink-muted block mb-1">
                  Index 03 / Multi-Role Readiness
                </span>
                <h3 className="font-serif text-2xl font-normal text-ink">
                  Comparative Qualification Across 8 Engineering Careers
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center border border-rule bg-surface p-6">
                <RadarChart leaderboard={results.leaderboard} />

                <div>
                  <h4 className="font-mono text-xs uppercase tracking-wider text-ink-muted mb-3">
                    Readiness Ranked Order
                  </h4>
                  <div className="space-y-2">
                    {results.leaderboard.map((item, idx) => (
                      <div
                        key={item.role}
                        className={`flex items-center justify-between p-3 border font-mono text-xs ${
                          idx === 0
                            ? 'border-known bg-known-bg text-known font-bold'
                            : 'border-rule bg-surface-raised text-ink'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-ink-muted">#{idx + 1}</span>
                          <span>{item.role}</span>
                        </div>
                        <div className="flex items-center gap-4 tabular-nums">
                          <span className="font-bold">{item.overall_fit}% Fit</span>
                          <span className="text-ink-muted">{item.coverage_score}% Coverage</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* View 04: 12-Week Roadmap */}
          {activeSection === 'roadmap' && (
            <section id="roadmap" className="space-y-6 print-break-inside-avoid">
              <div>
                <span className="font-mono text-xs uppercase tracking-widest text-ink-muted block mb-1">
                  Index 04 / Curriculum Sequencing
                </span>
                <h3 className="font-serif text-2xl font-normal text-ink">
                  12-Week Directed Learning Roadmap
                </h3>
                <p className="font-mono text-xs text-ink-muted mt-1">{results.roadmap.summary}</p>
              </div>

              <div className="space-y-4">
                {results.roadmap.phases.map((p, idx) => (
                  <div key={idx} className="border border-rule bg-surface p-6 space-y-3">
                    <div className="flex flex-col md:flex-row md:items-baseline justify-between border-b border-rule pb-2">
                      <div className="flex items-baseline gap-2">
                        <span className="font-mono text-xs text-ink-muted uppercase">{p.phase_title}:</span>
                        <h4 className="font-serif text-xl font-bold text-ink">{p.skill}</h4>
                        <span className="font-mono text-xs text-ink-muted px-2 py-0.5 border border-rule bg-paper">
                          {p.category}
                        </span>
                      </div>
                      <span className="font-mono text-xs text-ink font-semibold mt-1 md:mt-0">
                        {p.week_span} (~{p.duration_weeks} weeks)
                      </span>
                    </div>

                    <p className="text-xs text-ink-muted leading-relaxed">
                      <span className="font-semibold text-ink">Objective:</span> {p.objective}
                    </p>

                    <div>
                      <span className="font-mono text-[11px] uppercase tracking-wider text-ink-muted block mb-1">
                        Applied Milestones:
                      </span>
                      <ul className="list-disc list-inside space-y-1 text-xs text-ink">
                        {p.milestones.map((m, mIdx) => (
                          <li key={mIdx}>{m}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* View 05: Peer Distribution */}
          {activeSection === 'peers' && (
            <section id="peers" className="space-y-6 print-break-inside-avoid">
              <div>
                <span className="font-mono text-xs uppercase tracking-widest text-ink-muted block mb-1">
                  Index 05 / Statistical Benchmark
                </span>
                <h3 className="font-serif text-2xl font-normal text-ink">
                  Candidate Gaussian Standing Against Applicant Pool
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center border border-rule bg-surface p-6">
                <BellCurve peer={results.peer_benchmark} />

                <div className="space-y-4 font-mono text-xs">
                  <div className="border-b border-rule pb-3">
                    <div className="text-ink-muted text-[11px] uppercase tracking-wider">Candidate Standing:</div>
                    <div className="font-serif text-2xl text-ink font-bold mt-1">
                      {results.peer_benchmark.standing}
                    </div>
                  </div>

                  {/* Formula Breakdown Card */}
                  <div className="border border-rule bg-surface-raised p-4 space-y-2">
                    <span className="text-[10px] uppercase tracking-wider text-ink-muted block">
                      Z-Score Standard Normal Transformation:
                    </span>
                    <div className="font-mono text-xs font-bold text-ink">
                      Z = (X - μ) / σ = ({results.peer_benchmark.user_skill_count} - {results.peer_benchmark.peer_mean_skills}) / 1.8 = {results.peer_benchmark.z_score}
                    </div>
                    <p className="text-ink-muted text-[11px]">
                      Transforms empirical skill counts into a standard Gaussian distribution where Φ(Z) yields the exact percentile rank: <b>{results.peer_benchmark.percentile}th percentile</b>.
                    </p>
                  </div>

                  <p className="text-xs text-ink-muted">
                    Data source note: Gaussian distribution derived from empirical sampling of the Kaggle 54k Resume dataset benchmark model.
                  </p>
                </div>
              </div>
            </section>
          )}

          {/* View 06: Bullet Rewriter */}
          {activeSection === 'rewriter' && (
            <section id="rewriter" className="space-y-6 print-break-inside-avoid">
              <div>
                <span className="font-mono text-xs uppercase tracking-widest text-ink-muted block mb-1">
                  Index 06 / Action-Verb Rewriter
                </span>
                <h3 className="font-serif text-2xl font-normal text-ink">
                  Google XYZ Formula Bullet Refinements
                </h3>
                <p className="font-mono text-xs text-ink-muted mt-1">
                  Accomplished [X], as measured by [Y], by doing [Z].
                </p>
              </div>

              <div className="space-y-4">
                {results.bullet_rewrites.map((item, idx) => (
                  <div key={idx} className="border border-rule bg-surface p-6 space-y-3">
                    <div className="border-l-2 border-missing pl-3 py-1">
                      <span className="font-mono text-[10px] uppercase tracking-wider text-missing block">
                        Original Bullet #{idx + 1}
                      </span>
                      <p className="font-mono text-xs text-ink mt-0.5 italic">"{item.original}"</p>
                      <div className="font-mono text-[11px] text-missing mt-1">{item.reasons.join(" • ")}</div>
                    </div>

                    <div className="border-t border-rule-subtle pt-3">
                      <span className="font-mono text-[10px] uppercase tracking-wider text-known block mb-2">
                        XYZ Engineering Rewrites:
                      </span>
                      <ul className="space-y-1.5 font-mono text-xs text-ink">
                        {item.improved_options.map((opt, oIdx) => (
                          <li key={oIdx} className="flex items-start gap-2">
                            <span className="text-ink-muted">→</span>
                            <span>{opt}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* View 07: ATS Rubric */}
          {activeSection === 'rubric' && (
            <section id="rubric" className="space-y-6 print-break-inside-avoid">
              <div>
                <span className="font-mono text-xs uppercase tracking-widest text-ink-muted block mb-1">
                  Index 07 / ATS Diagnostic Rubric
                </span>
                <h3 className="font-serif text-2xl font-normal text-ink">
                  Deterministic 100-Point Readability Rubric & Learning Links
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* 6 Rule Rubric Bars */}
                <div className="border border-rule bg-surface p-6 space-y-4">
                  <h4 className="font-mono text-xs uppercase tracking-wider text-ink-muted mb-2">
                    Evaluation Checks
                  </h4>
                  {Object.entries(results.readability.rules).map(([rKey, rInfo]) => (
                    <div key={rKey} className="space-y-1">
                      <div className="flex justify-between font-mono text-xs">
                        <span className="text-ink font-semibold">{rInfo.rule || rKey}</span>
                        <span className="text-ink-muted tabular-nums">
                          {rInfo.score}/{rInfo.max_score} pts
                        </span>
                      </div>
                      <div className="h-1.5 w-full bg-rule-subtle overflow-hidden">
                        <div
                          className="h-full bg-ink"
                          style={{ width: `${(rInfo.score / rInfo.max_score) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}

                  <div className="border-t border-rule pt-4 mt-4">
                    <span className="font-mono text-[11px] uppercase tracking-wider text-ink-muted block mb-1.5">
                      Actionable Improvement Tips:
                    </span>
                    <ul className="list-disc list-inside space-y-1 font-mono text-xs text-ink-muted">
                      {results.readability.tips.map((tip, idx) => (
                        <li key={idx}>{tip}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Verified Documentation Links */}
                <div className="border border-rule bg-surface p-6 space-y-4">
                  <h4 className="font-mono text-xs uppercase tracking-wider text-ink-muted mb-2">
                    Verified Free Documentation Links
                  </h4>
                  <div className="space-y-3">
                    {results.recommendations.map((rec) => (
                      <div key={rec.skill} className="border border-rule bg-surface-raised p-3.5 space-y-1">
                        <div className="flex justify-between font-mono text-xs font-semibold text-ink">
                          <span>{rec.skill}</span>
                          <span className="text-ink-muted font-normal">{rec.category}</span>
                        </div>
                        {results.resources[rec.skill]?.map((item, idx) => (
                          <a
                            key={idx}
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 font-mono text-xs text-cobalt hover:underline mt-1 truncate max-w-full"
                          >
                            <span>{item.title}</span>
                            <ArrowUpRight className="h-3 w-3" />
                          </a>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Footer Note */}
          <footer className="border-t border-rule pt-8 text-center font-mono text-xs text-ink-muted">
            <p>SkillBridge</p>
            <p className="text-[11px] text-ink-subtle mt-1">
              Deterministic, interpretable graph-theoretic algorithms without black-box neural networks.
            </p>
          </footer>
        </main>
      )}
    </div>
  );
}
