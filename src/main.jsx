import React, { useState, useRef, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import {
  ArrowUp, BookOpen, ChevronDown, FileText, Menu, ShieldCheck,
  Sparkles, X, AlertTriangle, Loader2, Database, Brain, Shield,
  Search, Layers, CheckCircle, HelpCircle, Activity, ExternalLink,
  MessageSquare, Cpu, Lock, Terminal, RefreshCw
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './styles.css'

function preprocessMarkdown(text) {
  if (!text) return ''
  // Expand collapsed table rows (e.g. '| |---|' or '| | Row |') into separate lines
  let formatted = text.replace(/\|\s*\|\s*/g, '|\n| ')
  // Ensure headers have blank lines before them
  formatted = formatted.replace(/([^\n])\n(#{1,6}\s)/g, '$1\n\n$2')
  return formatted
}

/* ══════════════════════════════════════════════
   API CONFIGURATION — Serverless Azure Function Backend
   ══════════════════════════════════════════════ */
const API_BASE = 'https://sicklesense-func.azurewebsites.net/api'
const API_QUERY = `${API_BASE}/query`
const API_HEALTH = `${API_BASE}/health`
const MASCOT_IMG = `${import.meta.env.BASE_URL}mascot.png`

const examples = [
  'When should hydroxyurea be started in adults with sickle cell anemia?',
  'How is stroke risk screened in children?',
  'How is acute chest syndrome managed?',
]

/* ── Source documents from the corpus ── */
const SOURCE_DOCUMENTS = [
  {
    id: 'nhlbi-scd-2014',
    shortName: 'NHLBI 2014',
    title: 'Evidence-Based Management of Sickle Cell Disease: Expert Panel Report, 2014',
    publisher: 'National Heart, Lung, and Blood Institute (NIH)',
    citation: 'National Heart, Lung, and Blood Institute (2014). Evidence-Based Management of Sickle Cell Disease: Expert Panel Report, 2014. U.S. Department of Health and Human Services.',
    description: 'Comprehensive clinical guideline covering adult and pediatric SCD management, hydroxyurea therapy indications, transcranial Doppler (TCD) stroke screening, acute chest syndrome protocols, chronic kidney disease monitoring, and blood transfusion protocols.',
    sampleQuery: 'When should hydroxyurea be started in adults with sickle cell anemia?',
    topics: ['Hydroxyurea Therapy', 'Stroke Prevention / TCD', 'Acute Chest Syndrome', 'Pain Management', 'Transfusion Therapy', 'Priapism', 'Pregnancy / Reproductive', 'Renal Complications', 'Ophthalmologic Screening', 'Pulmonary Hypertension', 'Infection Prevention'],
  },
  {
    id: '10_3390_jcm13237224',
    shortName: 'JCM 2024',
    title: 'Clinical Insights into Sickle Cell Disease: A Comprehensive Multicenter Retrospective Analysis of Clinical Characteristics and Outcomes Across Different Age Groups',
    publisher: 'Journal of Clinical Medicine (MDPI)',
    citation: 'Almarghalani DA, Alotaibi RA, Alzlami TT, et al. Clinical Insights into Sickle Cell Disease: A Comprehensive Multicenter Retrospective Analysis of Clinical Characteristics and Outcomes Across Different Age Groups. J Clin Med. 2024;13(23):7224.',
    description: 'A multicenter retrospective study from Taif, Saudi Arabia evaluating clinical manifestations, splenic complications, hospital length-of-stay, ICU admissions, and age-stratified outcomes across pediatric, adolescent, and adult SCD cohorts.',
    sampleQuery: 'Which age group had the highest ICU admission rate in the multicenter study?',
    topics: ['Age-Group Epidemiology', 'Splenic Disease', 'Hospital Utilisation', 'Treatment Adherence', 'Renal Complications'],
  },
  {
    id: '9789240122666',
    shortName: 'WHO 2026',
    title: 'WHO Consolidated Guidelines for the Management of Common Childhood Illness: Management of Sickle-Cell Disease in Children and Adolescents',
    publisher: 'World Health Organization (Geneva)',
    citation: 'World Health Organization. WHO consolidated guidelines for the management of common childhood illness: management of sickle-cell disease in children and adolescents. Geneva: World Health Organization; 2026. ISBN 978-92-4-012266-6.',
    description: 'Global WHO pediatric recommendations covering universal newborn screening, penicillin prophylaxis, malaria prevention in endemic zones, nutrition faltering, danger sign recognition, community-level care, and universal pediatric hydroxyurea initiation.',
    sampleQuery: 'What is the recommended starting dose of hydroxyurea in pediatric SCD?',
    topics: ['Newborn Screening', 'Malaria Prophylaxis', 'Dactylitis / Hand-Foot', 'Nutrition / Growth', 'Iron Supplementation', 'Danger Signs / Referral', 'Primary / Community Care', 'Folic Acid Supplementation', 'Pediatric Dosing'],
  },
]

/* ── FAQ items for Support ── */
const FAQ_ITEMS = [
  {
    q: 'How does SickleSense prevent medical hallucinations?',
    a: 'SickleSense uses a strict Grounding System Prompt combined with Azure AI Search hybrid retrieval (BiomedBERT vector embeddings + BM25 keyword matching). The model is instructed to answer ONLY using retrieved passages, with every clinical claim backed by document, section, and page citations. If evidence is insufficient, it explicitly refuses rather than guessing.',
  },
  {
    q: 'Why was my patient-specific question refused or redirected?',
    a: 'Population-level clinical guidelines provide generalized protocols, not individualized medical prescriptions. SickleSense features an automated safety gate that detects patient-specific phrases (e.g. "my child has...", "what dose should I take?"). It refuses personalized dosing to safeguard patient safety and directs users to consult a licensed clinician.',
  },
  {
    q: 'How are citations and chunk IDs structured?',
    a: 'Every cited chunk follows the format [document-id]-CH-[number] or [document-id]-P[page]-C[chunk], referencing the exact page number and text chunk indexed in Azure AI Search. You can trace any statement back to the source guideline document.',
  },
  {
    q: 'What is the underlying technology stack?',
    a: 'The frontend is built with React and Vite. The backend is a dedicated FastAPI service deployed on Azure App Service Linux, querying an Azure AI Search index (`creativa-hackathon-pc`) with `NeuML/biomedbert-base-embeddings` and generating grounded synthesis via `openai/gpt-oss-120b`.',
  },
  {
    q: 'Can SickleSense be used for urgent medical emergencies?',
    a: 'No. SickleSense is strictly an evidence lookup and educational margin-note tool. In any emergency—such as acute chest syndrome symptoms, severe splenic sequestration, stroke warning signs, or unmanageable pain crises—immediate clinical evaluation in an emergency setting is required.',
  },
]

/* ── Floating blood cells background ── */
function BloodCells() {
  return (
    <div className="blood-cells" aria-hidden="true">
      <div className="cell cell-round c1" />
      <div className="cell cell-round c2" />
      <div className="cell cell-round c3" />
      <div className="cell cell-round c4" />
      <div className="cell cell-round c5" />
      <div className="cell cell-round c6" />
      <div className="cell cell-sickle s1" />
      <div className="cell cell-sickle s2" />
      <div className="cell cell-sickle s3" />
      <div className="cell cell-sickle s4" />
      <div className="cell cell-dot d1" />
      <div className="cell cell-dot d2" />
      <div className="cell cell-dot d3" />
      <div className="cell cell-dot d4" />
      <div className="cell cell-dot d5" />
    </div>
  )
}

function App() {
  const [query, setQuery] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [showSources, setShowSources] = useState(true)
  const [menuOpen, setMenuOpen] = useState(false)
  const [askedQuestion, setAskedQuestion] = useState('')
  const [currentPage, setCurrentPage] = useState('ask') // 'ask' | 'sources' | 'about' | 'support'
  const [openFaq, setOpenFaq] = useState(0)
  const [healthStatus, setHealthStatus] = useState(null)
  const [healthLoading, setHealthLoading] = useState(false)
  const textareaRef = useRef(null)

  // Fetch health status on mount
  useEffect(() => {
    checkBackendHealth()
  }, [])

  async function checkBackendHealth() {
    setHealthLoading(true)
    try {
      const res = await fetch(API_HEALTH, { method: 'GET', headers: { Accept: 'application/json' } })
      if (res.ok) {
        const data = await res.json()
        setHealthStatus(data)
      } else {
        setHealthStatus({ status: 'offline', model: 'unknown', index: 'unknown' })
      }
    } catch {
      setHealthStatus({ status: 'offline', model: 'unknown', index: 'unknown' })
    } finally {
      setHealthLoading(false)
    }
  }

  /* ── API call — FastAPI on Azure App Service ── */
  async function askBackend(question) {
    setLoading(true)
    setError(null)
    setResult(null)
    setAskedQuestion(question)
    setSubmitted(true)
    setCurrentPage('ask')

    try {
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), 30000) // 30s timeout

      const res = await fetch(API_QUERY, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ query: question, top_k: 5 }),
        signal: controller.signal,
      })
      clearTimeout(timeout)

      if (!res.ok) {
        let message = `Server responded with ${res.status}`
        try {
          const errBody = await res.json()
          if (errBody.detail) {
            message = typeof errBody.detail === 'string'
              ? errBody.detail
              : JSON.stringify(errBody.detail)
          }
        } catch { /* use default message */ }
        throw new Error(message)
      }

      const data = await res.json()
      const normalized = {
        ...data,
        answer: data.answer || data.recommendation || data.evidence || 'No response text available.',
        sources: data.sources || data.citations || [],
        confidence: data.confidence || 'medium'
      }
      setResult(normalized)
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Request timed out. The server may be processing a complex query — please try again.')
      } else {
        setError(err.message || 'Something went wrong. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  function submitQuestion(event) {
    event?.preventDefault()
    const q = query.trim()
    if (q && !loading) askBackend(q)
  }

  function chooseExample(example) {
    setQuery(example)
    askBackend(example)
  }

  function handleQuestionKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      submitQuestion(event)
    }
  }

  function goHome() {
    setQuery('')
    setSubmitted(false)
    setResult(null)
    setError(null)
    setAskedQuestion('')
    setCurrentPage('ask')
  }

  function navigate(page) {
    setCurrentPage(page)
    setMenuOpen(false)
    window.scrollTo(0, 0)
  }

  return (
    <div className="app-shell">
      <BloodCells />

      {/* ── Top bar ── */}
      <header className="topbar">
        <a className="brand" href="#" onClick={(e) => { e.preventDefault(); goHome() }} aria-label="SickleSense home">
          <span className="brand-mark"><img src={MASCOT_IMG} alt="SickleSense mascot" /></span>
          <span><strong>SickleSense</strong><small>AI-Powered Knowledge for Sickle Cell Care</small></span>
        </a>
        <nav className={menuOpen ? 'nav-links is-open' : 'nav-links'} aria-label="Primary navigation">
          <a className={currentPage === 'ask' ? 'active' : ''} href="#" onClick={(e) => { e.preventDefault(); goHome() }}>Ask a question</a>
          <a className={currentPage === 'sources' ? 'active' : ''} href="#" onClick={(e) => { e.preventDefault(); navigate('sources') }}>Sources</a>
          <a className={currentPage === 'about' ? 'active' : ''} href="#" onClick={(e) => { e.preventDefault(); navigate('about') }}>About</a>
          <a className={currentPage === 'support' ? 'active' : ''} href="#" onClick={(e) => { e.preventDefault(); navigate('support') }}>Support & FAQ</a>
        </nav>
        <button className="menu-button" onClick={() => setMenuOpen(!menuOpen)} aria-label={menuOpen ? 'Close menu' : 'Open menu'}>
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
        <div className="status-pill">
          <span className={healthStatus?.status === 'healthy' ? 'status-dot is-healthy' : 'status-dot'} />
          {healthStatus?.status === 'healthy' ? 'FastAPI Live' : 'Evidence mode'}
        </div>
      </header>

      <main>
        {/* ══════════ ASK PAGE ══════════ */}
        {currentPage === 'ask' && (
          <>
            <section className={submitted ? 'hero submitted' : 'hero'}>
              {!submitted && (
                <div className="hero-layout">
                  <div className="hero-copy">
                    <p className="kicker"><ShieldCheck size={15} /> Sickle cell disease evidence assistant · Made by MINOR THREAT 2026</p>
                    <h1>Answers you can<br /><em>trace back.</em></h1>
                    <p className="hero-description">Ask a focused clinical question. SickleSense searches peer-reviewed guidelines and provides grounded answers with verifiable page-level citations.</p>
                  </div>
                  <div className="hero-mascot">
                    <img src={MASCOT_IMG} alt="SickleSense AI assistant mascot" />
                  </div>
                </div>
              )}

              <form className="query-box" onSubmit={submitQuestion}>
                <label htmlFor="question">What would you like to understand?</label>
                <textarea
                  id="question"
                  ref={textareaRef}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleQuestionKeyDown}
                  placeholder="e.g. When should hydroxyurea be started?"
                  rows="2"
                  disabled={loading}
                />
                <div className="query-footer">
                  <span><span className="key">⏎</span> Enter to ask</span>
                  <button className="send-button" type="submit" disabled={!query.trim() || loading} aria-label="Ask SickleSense">
                    {loading ? <Loader2 size={19} className="spinner" /> : <ArrowUp size={19} />}
                  </button>
                </div>
              </form>

              {!submitted && (
                <div className="examples">
                  <span>Try asking</span>
                  {examples.map((example) => (
                    <button key={example} onClick={() => chooseExample(example)}>{example}</button>
                  ))}
                </div>
              )}
            </section>

            {/* ── Results workspace ── */}
            {submitted && (
              <section className="workspace" aria-live="polite">
                <div className="answer-column">
                  <div className="question-echo">
                    <span>You asked</span>
                    <p>{askedQuestion}</p>
                  </div>

                  {/* Loading state */}
                  {loading && (
                    <article className="answer-card loading-card">
                      <div className="loading-state">
                        <Loader2 size={32} className="spinner" />
                        <p className="loading-text">Searching clinical evidence sources…</p>
                        <p className="loading-sub">Retrieving passages via hybrid Azure AI Search</p>
                      </div>
                    </article>
                  )}

                  {/* Error state */}
                  {error && !loading && (
                    <article className="answer-card error-card">
                      <div className="answer-heading">
                        <div className="answer-icon error-icon"><AlertTriangle size={18} /></div>
                        <div>
                          <span className="answer-label">Unable to retrieve answer</span>
                          <p className="answer-meta">There was a problem contacting the evidence server</p>
                        </div>
                      </div>
                      <p className="recommendation">{error}</p>
                      <div className="boundary">
                        <ShieldCheck size={17} />
                        <span>Try rephrasing your question or check your connection to the FastAPI backend.</span>
                      </div>
                    </article>
                  )}

                  {/* Answer state — renders markdown */}
                  {result && !loading && (
                    <article className="answer-card">
                      <div className="answer-heading">
                        <div className="answer-icon"><Sparkles size={18} /></div>
                        <div>
                          <span className="answer-label">SickleSense answer</span>
                          <p className="answer-meta">Synthesized from retrieved clinical guidelines</p>
                        </div>
                        {result.sources && result.sources.length > 0 && (
                          <span className="confidence" style={{ color: '#2e7d5a', background: '#edf8f2' }}>
                            {result.sources.length} source{result.sources.length !== 1 ? 's' : ''} cited
                          </span>
                        )}
                      </div>

                      <div className="answer-markdown">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            table: ({ node, ...props }) => (
                              <div className="table-responsive">
                                <table {...props} />
                              </div>
                            ),
                          }}
                        >
                          {preprocessMarkdown(result.answer)}
                        </ReactMarkdown>
                      </div>

                      <div className="boundary">
                        <ShieldCheck size={17} />
                        <span>This information is for clinical education and evidence review only. It does not constitute personalized medical advice.</span>
                      </div>
                    </article>
                  )}
                </div>

                {/* ── Sources panel ── */}
                <aside className="sources-panel">
                  <button className="sources-heading" onClick={() => setShowSources(!showSources)}>
                    <span><BookOpen size={17} /> Guideline Sources</span>
                    <ChevronDown className={showSources ? 'rotated' : ''} size={18} />
                  </button>

                  {showSources && (
                    <div className="source-list">
                      {loading && <p className="sources-loading">Retrieving sources…</p>}

                      {result && result.sources && result.sources.length > 0 && result.sources.map((src, index) => (
                        <div className="source-item" key={src.chunk_id || index}>
                          <span className="source-number">0{index + 1}</span>
                          <div>
                            <strong>{src.section}</strong>
                            <span className="source-title">{src.title}</span>
                            <small>
                              Page {src.page_number} · Score {src.score.toFixed(4)}
                              {src.chunk_id && <> · <code className="chunk-id">{src.chunk_id}</code></>}
                            </small>
                          </div>
                          <FileText size={16} />
                        </div>
                      ))}

                      {result && (!result.sources || result.sources.length === 0) && !loading && (
                        <p className="no-sources">No sources were retrieved for this response.</p>
                      )}

                      {error && !loading && (
                        <p className="no-sources">Sources could not be retrieved.</p>
                      )}
                    </div>
                  )}
                </aside>
              </section>
            )}

            {/* ── Trust strip (landing) ── */}
            {!submitted && (
              <section className="trust-strip">
                <div><ShieldCheck size={20} /><strong>Built for careful reading</strong><span>Every response stays within the supplied clinical sources.</span></div>
                <div><BookOpen size={20} /><strong>Three trusted sources</strong><span>NHLBI, JCM, and WHO guidance in one place.</span></div>
                <div><FileText size={20} /><strong>Traceable by design</strong><span>See the document, section, page, and chunk.</span></div>
              </section>
            )}
          </>
        )}

        {/* ══════════ SOURCES PAGE ══════════ */}
        {currentPage === 'sources' && (
          <section className="page-section">
            <div className="page-header">
              <p className="kicker"><BookOpen size={15} /> Clinical evidence corpus</p>
              <h1 className="page-title">Indexed Clinical Sources</h1>
              <p className="page-description">SickleSense answers are grounded exclusively in three peer-reviewed, recognized clinical documents. Every claim cites the specific document, section, and verified page number.</p>
            </div>

            <div className="source-cards">
              {SOURCE_DOCUMENTS.map((doc) => (
                <article className="source-doc-card" key={doc.id}>
                  <div className="source-doc-header">
                    <span className="source-doc-badge">{doc.shortName}</span>
                    <span className="source-publisher">{doc.publisher}</span>
                  </div>
                  <h2>{doc.title}</h2>
                  <p className="source-doc-description">{doc.description}</p>
                  
                  <div className="source-doc-citation">
                    <strong>Official Citation</strong>
                    <p>{doc.citation}</p>
                  </div>

                  <div className="source-doc-topics">
                    <strong>Indexed Clinical Topics</strong>
                    <div className="topic-chips">
                      {doc.topics.map((topic) => (
                        <span className="topic-chip" key={topic}>{topic}</span>
                      ))}
                    </div>
                  </div>

                  <div className="source-action-bar">
                    <button
                      className="source-ask-button"
                      onClick={() => {
                        setQuery(doc.sampleQuery)
                        askBackend(doc.sampleQuery)
                      }}
                    >
                      <Search size={14} />
                      Ask: "{doc.sampleQuery}"
                    </button>
                  </div>
                </article>
              ))}
            </div>

            <div className="corpus-stats">
              <div className="stat-item">
                <Database size={20} />
                <div><strong>3 Source Guidelines</strong><span>Indexed in Azure AI Search (`creativa-hackathon-pc`)</span></div>
              </div>
              <div className="stat-item">
                <Layers size={20} />
                <div><strong>800-char Chunks</strong><span>150 overlap, optimized via empirical Precision@K tests</span></div>
              </div>
              <div className="stat-item">
                <Search size={20} />
                <div><strong>Hybrid RRF Retrieval</strong><span>BM25 keyword + BiomedBERT 768d vector queries</span></div>
              </div>
            </div>
          </section>
        )}

        {/* ══════════ ABOUT PAGE ══════════ */}
        {currentPage === 'about' && (
          <section className="page-section">
            <div className="page-header">
              <p className="kicker"><ShieldCheck size={15} /> About SickleSense · Made by MINOR THREAT 2026</p>
              <h1 className="page-title">Clinical evidence,<br /><em>clearly cited.</em></h1>
              <p className="page-description">SickleSense is a citation-bound clinical retrieval-augmented generation (RAG) assistant created by team <strong>MINOR THREAT 2026</strong>. It empowers clinicians, hematologists, and healthcare learners to query sickle cell disease guidelines with complete, verifiable provenance.</p>
            </div>

            {/* Live System Health Card */}
            <div className="system-health-banner">
              <div className="health-header">
                <div className="health-title">
                  <Activity size={18} />
                  <strong>Backend System Architecture</strong>
                </div>
                <button className="health-refresh" onClick={checkBackendHealth} disabled={healthLoading}>
                  <RefreshCw size={13} className={healthLoading ? 'spinner' : ''} />
                  {healthLoading ? 'Checking...' : 'Refresh Status'}
                </button>
              </div>
              <div className="health-grid">
                <div className="health-metric">
                  <span className="metric-label">API Status</span>
                  <span className="metric-val status-live">
                    <span className="status-dot is-healthy" />
                    {healthStatus?.status === 'healthy' ? 'Active & Ready' : 'Online (Always-On)'}
                  </span>
                </div>
                <div className="health-metric">
                  <span className="metric-label">LLM Engine</span>
                  <span className="metric-val font-mono">{healthStatus?.model || 'openai/gpt-oss-120b'}</span>
                </div>
                <div className="health-metric">
                  <span className="metric-label">Azure Search Index</span>
                  <span className="metric-val font-mono">{healthStatus?.index || 'creativa-hackathon-pc'}</span>
                </div>
                <div className="health-metric">
                  <span className="metric-label">Embeddings</span>
                  <span className="metric-val font-mono">BiomedBERT (768d)</span>
                </div>
              </div>
            </div>

            <div className="about-grid">
              <article className="about-card">
                <div className="about-card-icon"><Search size={22} /></div>
                <h3>Hybrid RRF Retrieval</h3>
                <p>Combines dense semantic retrieval (`NeuML/biomedbert-base-embeddings`) with lexical BM25 search in Azure AI Search. Server-side Reciprocal Rank Fusion (RRF) merges top results to prevent keyword-misses on complex acronyms (TCD, VOC, ACS).</p>
              </article>

              <article className="about-card">
                <div className="about-card-icon"><Brain size={22} /></div>
                <h3>Constrained Generation</h3>
                <p>The reasoning model (`openai/gpt-oss-120b`) is strictly constrained to the retrieved context. It produces structured, evidence-grounded recommendations with explicit source citations and zero external speculation.</p>
              </article>

              <article className="about-card">
                <div className="about-card-icon"><Shield size={22} /></div>
                <h3>Dual Safety Boundaries</h3>
                <p>First, patient-specific inquiries (e.g., individual dosages, personal symptoms) are intercepted by regex filters before LLM invocation. Second, queries scoring below the calibrated retrieval threshold (0.025) return structured refusals rather than partial guesses.</p>
              </article>

              <article className="about-card">
                <div className="about-card-icon"><CheckCircle size={22} /></div>
                <h3>Citation Provenance</h3>
                <p>Every claim maps to traceable chunk IDs, publication titles, and page numbers. The citation validation algorithm verifies that every cited chunk was genuinely part of the retrieved evidence context.</p>
              </article>
            </div>

            <div className="about-pipeline">
              <h2>End-to-End Query Lifecycle</h2>
              <div className="pipeline-steps">
                <div className="pipeline-step">
                  <span className="step-number">01</span>
                  <div>
                    <strong>Patient-Safety Interceptor</strong>
                    <p>The incoming prompt is inspected for individualized clinical advice patterns. If personalized treatment is requested, a clinical refusal is returned immediately to prevent unauthorized medical advice.</p>
                  </div>
                </div>
                <div className="pipeline-step">
                  <span className="step-number">02</span>
                  <div>
                    <strong>BiomedBERT Embedding & Hybrid Search</strong>
                    <p>The query is converted into a 768-dimensional normalized vector and searched against the Azure AI Search index alongside BM25 keyword matching, retrieving the Top-K most relevant chunks.</p>
                  </div>
                </div>
                <div className="pipeline-step">
                  <span className="step-number">03</span>
                  <div>
                    <strong>Relevance Score Gating</strong>
                    <p>The top RRF score is evaluated against calibrated thresholds. Out-of-scope queries (e.g. unrelated medical fields) are flagged to prevent force-fitting irrelevant context into answers.</p>
                  </div>
                </div>
                <div className="pipeline-step">
                  <span className="step-number">04</span>
                  <div>
                    <strong>Grounded Synthesis & Provenance Verification</strong>
                    <p>The LLM generates formatted Markdown containing the clinical summary, structured tables, and page-level source references from the verified chunks.</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="boundary about-boundary">
              <ShieldCheck size={17} />
              <span>SickleSense is developed for clinical education and evidence cross-referencing. It does not replace professional medical judgment or direct patient assessment.</span>
            </div>
          </section>
        )}

        {/* ══════════ SUPPORT & FAQ PAGE ══════════ */}
        {currentPage === 'support' && (
          <section className="page-section">
            <div className="page-header">
              <p className="kicker"><HelpCircle size={15} /> Clinical Support & FAQ</p>
              <h1 className="page-title">Support & Usage Guide</h1>
              <p className="page-description">Learn how to get the most accurate answers from SickleSense, understand the clinical boundaries, and review common questions regarding evidence retrieval.</p>
            </div>

            {/* Prompting Guide Cards */}
            <div className="support-guide-grid">
              <div className="guide-card guide-good">
                <div className="guide-header">
                  <CheckCircle size={18} />
                  <strong>Recommended Query Style</strong>
                </div>
                <p>Ask about guideline standards, thresholds, clinical trials, or protocols:</p>
                <ul>
                  <li>"When should hydroxyurea be initiated in adults with SCD?"</li>
                  <li>"What are the annual TCD screening protocols for pediatric patients?"</li>
                  <li>"How is acute chest syndrome diagnosed and managed?"</li>
                </ul>
              </div>

              <div className="guide-card guide-bad">
                <div className="guide-header">
                  <AlertTriangle size={18} />
                  <strong>Will Trigger Safety Refusal</strong>
                </div>
                <p>Personalized patient details and direct prescription requests will be refused:</p>
                <ul>
                  <li>"My 12-year-old son has a pain crisis, what dose should I give him?"</li>
                  <li>"I have SCD and my creatinine is 1.4, should I start hydroxyurea?"</li>
                  <li>"Diagnose my symptoms: fever and chest pain."</li>
                </ul>
              </div>
            </div>

            {/* Interactive FAQ Accordion */}
            <div className="faq-section">
              <h2>Frequently Asked Questions</h2>
              <div className="faq-list">
                {FAQ_ITEMS.map((item, idx) => (
                  <div
                    key={idx}
                    className={openFaq === idx ? 'faq-item is-open' : 'faq-item'}
                    onClick={() => setOpenFaq(openFaq === idx ? -1 : idx)}
                  >
                    <button className="faq-question">
                      <span>{item.q}</span>
                      <ChevronDown size={18} className={openFaq === idx ? 'rotated' : ''} />
                    </button>
                    {openFaq === idx && (
                      <div className="faq-answer">
                        <p>{item.a}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Contact & API Info Card */}
            <div className="support-contact-card">
              <div className="contact-icon"><MessageSquare size={24} /></div>
              <div>
                <h3>Need Technical Support or API Access?</h3>
                <p>SickleSense is powered by an open REST API on Azure App Service. For integration documentation, test endpoints, and live schema parameters, explore the interactive Swagger documentation.</p>
                <div className="contact-links">
                  <a
                    href="https://sicklesense-api-dgh3aqdwb3eghdc4.swedencentral-01.azurewebsites.net/docs"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="contact-link-btn"
                  >
                    <Terminal size={14} />
                    Interactive Swagger API Docs
                    <ExternalLink size={12} />
                  </a>
                </div>
              </div>
            </div>

            <div className="boundary about-boundary">
              <ShieldCheck size={17} />
              <span>For clinical emergencies, contact local emergency healthcare services immediately. SickleSense is an asynchronous reference system only.</span>
            </div>
          </section>
        )}
      </main>

      <footer>
        <span>For clinical education and evidence review · Made by MINOR THREAT 2026</span>
        <span>SickleSense · Sources before certainty</span>
      </footer>
    </div>
  )
}

createRoot(document.getElementById('root')).render(<App />)
