import React, { useState, useRef } from 'react'
import { createRoot } from 'react-dom/client'
import { ArrowUp, BookOpen, ChevronDown, FileText, Menu, ShieldCheck, Sparkles, X, AlertTriangle, Loader2, Database, Brain, Shield, Search, Layers, CheckCircle } from 'lucide-react'
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
   API CONFIGURATION — FastAPI on Azure App Service
   ══════════════════════════════════════════════ */
const API_BASE = 'https://sicklesense-api-dgh3aqdwb3eghdc4.swedencentral-01.azurewebsites.net'
const API_QUERY = `${API_BASE}/api/query`

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
    citation: 'National Heart, Lung, and Blood Institute (2014). Evidence-Based Management of Sickle Cell Disease: Expert Panel Report, 2014.',
    description: 'Comprehensive clinical guideline covering hydroxyurea therapy, stroke prevention, acute chest syndrome management, transfusion therapy, pain management, renal complications, and preventive care across all age groups.',
    topics: ['Hydroxyurea Therapy', 'Stroke Prevention / TCD', 'Acute Chest Syndrome', 'Pain Management', 'Transfusion Therapy', 'Priapism', 'Pregnancy / Reproductive', 'Renal Complications', 'Ophthalmologic Screening', 'Pulmonary Hypertension', 'Infection Prevention'],
  },
  {
    id: '10_3390_jcm13237224',
    shortName: 'JCM 2024',
    title: 'Clinical Insights into Sickle Cell Disease: A Comprehensive Multicenter Retrospective Analysis of Clinical Characteristics and Outcomes Across Different Age Groups',
    citation: 'Almarghalani DA, et al. Clinical Insights into Sickle Cell Disease: A Comprehensive Multicenter Retrospective Analysis. J Clin Med. 2024;13(23):7224.',
    description: 'Multicenter retrospective analysis from Taif, Saudi Arabia examining clinical characteristics, complications, and hospital utilisation patterns across pediatric, adolescent, and adult age groups.',
    topics: ['Age-Group Epidemiology', 'Splenic Disease', 'Hospital Utilisation', 'Treatment Adherence', 'Renal Complications'],
  },
  {
    id: '9789240122666',
    shortName: 'WHO 2026',
    title: 'WHO Consolidated Guidelines for the Management of Common Childhood Illness: Management of Sickle-Cell Disease in Children and Adolescents',
    citation: 'World Health Organization. WHO consolidated guidelines for the management of sickle-cell disease in children and adolescents. Geneva: WHO; 2026. ISBN 978-92-4-012266-6.',
    description: 'WHO guideline for resource-limited settings covering newborn screening, malaria prophylaxis, penicillin prophylaxis, nutrition monitoring, danger sign recognition, community-level care, and GRADE-rated recommendations for pediatric SCD management.',
    topics: ['Newborn Screening', 'Malaria Prophylaxis', 'Dactylitis / Hand-Foot', 'Nutrition / Growth', 'Iron Supplementation', 'Danger Signs / Referral', 'Primary / Community Care', 'Folic Acid Supplementation', 'Pediatric Dosing'],
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
  const [result, setResult] = useState(null)   // { query, answer, sources }
  const [error, setError] = useState(null)
  const [showSources, setShowSources] = useState(true)
  const [menuOpen, setMenuOpen] = useState(false)
  const [askedQuestion, setAskedQuestion] = useState('')
  const [currentPage, setCurrentPage] = useState('ask')
  const textareaRef = useRef(null)

  /* ── API call — new FastAPI format ── */
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
      setResult(data)
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
          <span className="brand-mark"><img src="/mascot.png" alt="SickleSense mascot" /></span>
          <span><strong>SickleSense</strong><small>AI-Powered Knowledge for Sickle Cell Care</small></span>
        </a>
        <nav className={menuOpen ? 'nav-links is-open' : 'nav-links'} aria-label="Primary navigation">
          <a className={currentPage === 'ask' ? 'active' : ''} href="#" onClick={(e) => { e.preventDefault(); goHome() }}>Ask a question</a>
          <a className={currentPage === 'sources' ? 'active' : ''} href="#" onClick={(e) => { e.preventDefault(); navigate('sources') }}>Sources</a>
          <a className={currentPage === 'about' ? 'active' : ''} href="#" onClick={(e) => { e.preventDefault(); navigate('about') }}>About</a>
        </nav>
        <button className="menu-button" onClick={() => setMenuOpen(!menuOpen)} aria-label={menuOpen ? 'Close menu' : 'Open menu'}>
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
        <div className="status-pill"><span className="status-dot" /> Evidence mode</div>
      </header>

      <main>
        {/* ══════════ ASK PAGE ══════════ */}
        {currentPage === 'ask' && (
          <>
            <section className={submitted ? 'hero submitted' : 'hero'}>
              {!submitted && (
                <div className="hero-layout">
                  <div className="hero-copy">
                    <p className="kicker"><ShieldCheck size={15} /> Sickle cell disease evidence assistant</p>
                    <h1>Answers you can<br /><em>trace back.</em></h1>
                    <p className="hero-description">Ask a focused question. SickleSense searches trusted clinical sources and shows you the evidence behind every answer.</p>
                  </div>
                  <div className="hero-mascot">
                    <img src="/mascot.png" alt="SickleSense AI assistant mascot" />
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
                        <p className="loading-sub">This typically takes 5–15 seconds</p>
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
                        <span>Try rephrasing your question or check your internet connection.</span>
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
                          <p className="answer-meta">Generated from retrieved clinical evidence</p>
                        </div>
                        {result.sources && result.sources.length > 0 && (
                          <span className="confidence" style={{ color: '#2e7d5a', background: '#edf8f2' }}>
                            {result.sources.length} source{result.sources.length !== 1 ? 's' : ''} cited
                          </span>
                        )}
                      </div>

                      <div className="answer-markdown">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
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
                <div><FileText size={20} /><strong>Traceable by design</strong><span>See the document, section, page, and passage.</span></div>
              </section>
            )}
          </>
        )}

        {/* ══════════ SOURCES PAGE ══════════ */}
        {currentPage === 'sources' && (
          <section className="page-section">
            <div className="page-header">
              <p className="kicker"><BookOpen size={15} /> Clinical evidence corpus</p>
              <h1 className="page-title">Source Documents</h1>
              <p className="page-description">SickleSense answers are grounded exclusively in these three peer-reviewed clinical sources. Every citation traces back to a specific document, section, and page number.</p>
            </div>
            <div className="source-cards">
              {SOURCE_DOCUMENTS.map((doc) => (
                <article className="source-doc-card" key={doc.id}>
                  <div className="source-doc-header">
                    <span className="source-doc-badge">{doc.shortName}</span>
                    <FileText size={18} />
                  </div>
                  <h2>{doc.title}</h2>
                  <p className="source-doc-description">{doc.description}</p>
                  <div className="source-doc-citation">
                    <strong>Citation</strong>
                    <p>{doc.citation}</p>
                  </div>
                  <div className="source-doc-topics">
                    <strong>Topics covered</strong>
                    <div className="topic-chips">
                      {doc.topics.map((topic) => (
                        <span className="topic-chip" key={topic}>{topic}</span>
                      ))}
                    </div>
                  </div>
                </article>
              ))}
            </div>
            <div className="corpus-stats">
              <div className="stat-item">
                <Database size={20} />
                <div><strong>3 Documents</strong><span>Indexed in Azure AI Search</span></div>
              </div>
              <div className="stat-item">
                <Layers size={20} />
                <div><strong>800-char chunks</strong><span>150 char overlap, optimised for clinical text</span></div>
              </div>
              <div className="stat-item">
                <Search size={20} />
                <div><strong>Hybrid retrieval</strong><span>BM25 + vector search via Reciprocal Rank Fusion</span></div>
              </div>
            </div>
          </section>
        )}

        {/* ══════════ ABOUT PAGE ══════════ */}
        {currentPage === 'about' && (
          <section className="page-section">
            <div className="page-header">
              <p className="kicker"><ShieldCheck size={15} /> About SickleSense</p>
              <h1 className="page-title">Clinical evidence,<br /><em>clearly cited.</em></h1>
              <p className="page-description">SickleSense is a citation-bound clinical evidence assistant for sickle cell disease. It retrieves relevant passages from trusted clinical guidelines and generates answers grounded exclusively in the retrieved evidence.</p>
            </div>
            <div className="about-grid">
              <article className="about-card">
                <div className="about-card-icon"><Search size={22} /></div>
                <h3>Hybrid Retrieval</h3>
                <p>Questions are searched using both keyword (BM25) and semantic vector search against an Azure AI Search index, merged via Reciprocal Rank Fusion. The biomedical embedding model (NeuML/biomedbert-base-embeddings) ensures clinical terminology is understood accurately.</p>
              </article>
              <article className="about-card">
                <div className="about-card-icon"><Brain size={22} /></div>
                <h3>Grounded Generation</h3>
                <p>The LLM is constrained to answer only using the retrieved evidence passages. Every claim must be directly supported by source text, with citations referencing document, section, page, and chunk ID. The system returns structured responses with source evidence.</p>
              </article>
              <article className="about-card">
                <div className="about-card-icon"><Shield size={22} /></div>
                <h3>Safety Boundaries</h3>
                <p>Patient-specific questions (e.g. "what dose should I give my son?") are detected and refused before any model call. Out-of-scope questions with low retrieval scores are refused with a clear explanation rather than a fabricated answer.</p>
              </article>
              <article className="about-card">
                <div className="about-card-icon"><CheckCircle size={22} /></div>
                <h3>Citation Verification</h3>
                <p>Every citation returned by the model is verified against the evidence actually retrieved for that question. A citation cannot reference a chunk ID outside the retrieved context, preventing hallucinated references.</p>
              </article>
            </div>
            <div className="about-pipeline">
              <h2>How it works</h2>
              <div className="pipeline-steps">
                <div className="pipeline-step">
                  <span className="step-number">01</span>
                  <div>
                    <strong>Question received</strong>
                    <p>Your clinical question is checked for patient-specific patterns. If it asks for individualized advice, it's refused immediately.</p>
                  </div>
                </div>
                <div className="pipeline-step">
                  <span className="step-number">02</span>
                  <div>
                    <strong>Hybrid evidence retrieval</strong>
                    <p>The question is embedded with BiomedBERT and searched against the Azure AI Search index using hybrid (keyword + vector) search. Top-K chunks are retrieved.</p>
                  </div>
                </div>
                <div className="pipeline-step">
                  <span className="step-number">03</span>
                  <div>
                    <strong>Relevance threshold check</strong>
                    <p>If the top retrieved chunk scores below the calibrated threshold, the question is flagged as out-of-scope and a clear refusal is returned.</p>
                  </div>
                </div>
                <div className="pipeline-step">
                  <span className="step-number">04</span>
                  <div>
                    <strong>Grounded generation</strong>
                    <p>The LLM receives only the retrieved evidence and strict grounding rules. It generates a structured response with clinical recommendation, evidence summary, and cited sources.</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="boundary about-boundary">
              <ShieldCheck size={17} />
              <span>SickleSense is for clinical education and evidence review. It does not diagnose, prescribe, or replace a qualified clinician. Population-level guidance should never be interpreted as personalized treatment advice.</span>
            </div>
          </section>
        )}
      </main>

      <footer>
        <span>For clinical education and evidence review.</span>
        <span>SickleSense · Sources before certainty</span>
      </footer>
    </div>
  )
}

createRoot(document.getElementById('root')).render(<App />)
