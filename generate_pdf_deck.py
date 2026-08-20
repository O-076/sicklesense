import os
from reportlab.lib.pagesizes import landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Page size: 16:9 widescreen (13.33 x 7.5 inches)
PAGE_WIDTH = 13.333 * inch
PAGE_HEIGHT = 7.5 * inch
PAGE_SIZE = (PAGE_WIDTH, PAGE_HEIGHT)

NAVY = colors.HexColor("#1a2744")
CRIMSON = colors.HexColor("#c0392b")
MUTED = colors.HexColor("#5e6e82")
LIGHT_BG = colors.HexColor("#f7f8fb")
WHITE = colors.HexColor("#ffffff")
CARD_BG = colors.HexColor("#ffffff")
CARD_BORDER = colors.HexColor("#dbe5e8")
DARK_CARD = colors.HexColor("#223150")
CORAL = colors.HexColor("#ff8a7a")
GREEN = colors.HexColor("#2e7d5a")

def draw_header(c, kicker, title):
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(CRIMSON)
    c.drawString(0.8 * inch, PAGE_HEIGHT - 0.6 * inch, kicker.upper())
    
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(NAVY)
    c.drawString(0.8 * inch, PAGE_HEIGHT - 0.95 * inch, title)

def draw_card(c, x, y, w, h, bg_color=CARD_BG, border_color=CARD_BORDER, r=10):
    c.saveState()
    c.setFillColor(bg_color)
    if border_color:
        c.setStrokeColor(border_color)
        c.setLineWidth(1.5)
    else:
        c.setStrokeColor(bg_color)
    c.roundRect(x * inch, y * inch, w * inch, h * inch, r, fill=1, stroke=1 if border_color else 0)
    c.restoreState()

c = canvas.Canvas("SickleSense_Pitch_Deck.pdf", pagesize=PAGE_SIZE)

# ══════════════════════════════════════════════════════════════════════
# SLIDE 1: Title Slide (Dark Navy)
# ══════════════════════════════════════════════════════════════════════
c.setFillColor(NAVY)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

if os.path.exists("public/mascot.png"):
    c.drawImage("public/mascot.png", 8.2 * inch, 1.2 * inch, width=4.3 * inch, preserveAspectRatio=True, mask='auto')

c.setFont("Helvetica-Bold", 42)
c.setFillColor(WHITE)
c.drawString(1.0 * inch, PAGE_HEIGHT - 2.0 * inch, "SICKLESENSE")

c.setFont("Helvetica", 19)
c.setFillColor(CORAL)
c.drawString(1.0 * inch, PAGE_HEIGHT - 2.5 * inch, "Citation-Bound Clinical Evidence Assistant for Sickle Cell Disease")

c.setFont("Helvetica", 13)
c.setFillColor(colors.HexColor("#cbd6e2"))
c.drawString(1.0 * inch, PAGE_HEIGHT - 3.2 * inch, "A grounded RAG system integrating domain-specific BiomedBERT embeddings,")
c.drawString(1.0 * inch, PAGE_HEIGHT - 3.5 * inch, "Azure AI Search hybrid retrieval, and constrained LLM synthesis.")

c.setFont("Helvetica-Bold", 12)
c.setFillColor(colors.HexColor("#a0b4cd"))
c.drawString(1.0 * inch, PAGE_HEIGHT - 4.5 * inch, "Presented by Team MINOR THREAT 2026 | Creativa SCD Hackathon")

c.showPage()

# ══════════════════════════════════════════════════════════════════════
# SLIDE 2: The Problem
# ══════════════════════════════════════════════════════════════════════
c.setFillColor(LIGHT_BG)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header(c, "The Clinical Challenge", "Why General-Purpose AI Fails in Sickle Cell Care")

# 3 Cards
cards_s2 = [
    (0.8, "Fragmented Guidelines", NAVY, [
        "• Authoritative protocols (NHLBI, WHO, regional studies) span hundreds of pages.",
        "• Clinicians lack fast, trustworthy margin-note tools during urgent patient rounds.",
        "• Critical dosage and screening thresholds (e.g. TCD velocities) are buried in dense text."
    ]),
    (4.8, "Generic LLM Hallucinations", CRIMSON, [
        "• Standard LLMs generate ungrounded, unverified medical advice with false confidence.",
        "• Fabricated citations and inaccurate contraindication advice create severe patient risk.",
        "• No page-level provenance or verification checks against the true medical corpus."
    ]),
    (8.8, "Uncontrolled Prescribing Risk", NAVY, [
        "• Population guidelines must never be confused with individual patient prescriptions.",
        "• Existing chatbots fail to intercept patient-specific inquiries (e.g. 'What dose for my child?').",
        "• Lack of strict safety interceptors creates clinical liability."
    ])
]

for x, title, t_col, bullets in cards_s2:
    draw_card(c, x, 0.8, 3.7, 5.3)
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(t_col)
    c.drawString((x + 0.3) * inch, PAGE_HEIGHT - 2.0 * inch, title)
    
    c.setFont("Helvetica", 11)
    c.setFillColor(MUTED)
    curr_y = PAGE_HEIGHT - 2.5 * inch
    for b in bullets:
        # Wrap simple
        words = b.split()
        line = ""
        for w in words:
            if len(line + " " + w) > 42:
                c.drawString((x + 0.3) * inch, curr_y, line)
                curr_y -= 0.22 * inch
                line = "  " + w
            else:
                line = line + " " + w if line else w
        if line:
            c.drawString((x + 0.3) * inch, curr_y, line)
            curr_y -= 0.35 * inch

c.showPage()

# ══════════════════════════════════════════════════════════════════════
# SLIDE 3: The Solution
# ══════════════════════════════════════════════════════════════════════
c.setFillColor(LIGHT_BG)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header(c, "Our Solution", "SickleSense: The Citation-Bound Clinical Margin Note")

pillars = [
    ("Strict Grounding", "Every generated claim is bound to retrieved evidence chunks. Zero unverified external speculation.", GREEN),
    ("Verifiable Citations", "Exact page numbers, section classifications, and chunk IDs (doc-CH-XXXX) for transparent provenance.", NAVY),
    ("Two-Tier Safety Gates", "Regex interceptor for patient-specific dosing requests + score threshold gating for out-of-scope queries.", CRIMSON),
    ("Clinical Speed & Reliability", "FastAPI Linux architecture on Azure App Service with sub-second hybrid retrieval and structured markdown output.", NAVY),
]

for i, (title, desc, color) in enumerate(pillars):
    x = 0.8 + (i % 2) * 5.9
    y = 3.6 if (i // 2) == 0 else 1.0
    draw_card(c, x, y, 5.7, 2.4)
    
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(color)
    c.drawString((x + 0.3) * inch, (y + 1.8) * inch, title)
    
    c.setFont("Helvetica", 12)
    c.setFillColor(MUTED)
    words = desc.split()
    line = ""
    curr_y = (y + 1.3) * inch
    for w in words:
        if len(line + " " + w) > 60:
            c.drawString((x + 0.3) * inch, curr_y, line)
            curr_y -= 0.25 * inch
            line = w
        else:
            line = line + " " + w if line else w
    if line:
        c.drawString((x + 0.3) * inch, curr_y, line)

c.showPage()

# ══════════════════════════════════════════════════════════════════════
# SLIDE 4: The 3 Indexed Guidelines
# ══════════════════════════════════════════════════════════════════════
c.setFillColor(LIGHT_BG)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header(c, "Knowledge Corpus", "Three Authoritative Guidelines Powering SickleSense")

sources = [
    (0.8, "NHLBI (2014)", "National Heart, Lung, and Blood Institute (NIH)", 
     "Evidence-Based Management of SCD Report",
     ["• Adult & pediatric hydroxyurea initiation thresholds",
      "• Annual TCD stroke screening protocols",
      "• Acute chest syndrome diagnosis & management",
      "• Transfusion therapy & CKD monitoring"]),
    (4.8, "JCM (2024)", "Journal of Clinical Medicine (MDPI)", 
     "Multicenter Retrospective Analysis (Taif Cohort)",
     ["• Real-world Saudi multicenter cohort findings",
      "• Splenic disease manifestations across age groups",
      "• Hospital length of stay & ICU admission rates",
      "• Pediatric vs. adult clinical comparison"]),
    (8.8, "WHO (2026)", "World Health Organization (Geneva)", 
     "Consolidated Guidelines for Children & Adolescents",
     ["• Universal newborn screening & diagnostic pathways",
      "• Penicillin & malaria prophylaxis in endemic zones",
      "• Universal pediatric hydroxyurea recommendation",
      "• Growth faltering, danger signs, & referral criteria"]),
]

for x, tag, pub, title, bullets in sources:
    draw_card(c, x, 0.8, 3.7, 5.3)
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(CRIMSON)
    c.drawString((x + 0.3) * inch, PAGE_HEIGHT - 2.0 * inch, tag)
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(NAVY)
    c.drawString((x + 0.3) * inch, PAGE_HEIGHT - 2.3 * inch, pub)
    
    c.setFont("Helvetica-Oblique", 11)
    c.setFillColor(MUTED)
    c.drawString((x + 0.3) * inch, PAGE_HEIGHT - 2.65 * inch, title)
    
    c.setFont("Helvetica", 10.5)
    c.setFillColor(NAVY)
    curr_y = PAGE_HEIGHT - 3.2 * inch
    for b in bullets:
        c.drawString((x + 0.3) * inch, curr_y, b)
        curr_y -= 0.38 * inch

c.showPage()

# ══════════════════════════════════════════════════════════════════════
# SLIDE 5: Parent-Child Chunking Strategy
# ══════════════════════════════════════════════════════════════════════
c.setFillColor(LIGHT_BG)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header(c, "Data Engineering", "Parent-Child Chunking: Precision Without Losing Context")

# Left card
draw_card(c, 0.8, 0.8, 5.7, 5.3)
c.setFont("Helvetica-Bold", 15)
c.setFillColor(NAVY)
c.drawString(1.1 * inch, PAGE_HEIGHT - 2.0 * inch, "Why Parent-Child Chunking?")

c.setFont("Helvetica", 11.5)
c.setFillColor(MUTED)
bullets_s5 = [
    "• Small Chunks (800 chars): Optimize dense embedding similarity and pinpoint exact sentences in dense clinical text.",
    "• Parent References (Page-Level): Preserve chapter context, section hierarchy, and guideline tables.",
    "• 150-Char Overlap: Guarantees medical terms and multi-word drug protocols (e.g. '15-20 mg/kg/day') are never split across boundaries.",
    "• Result: High Precision@3 retrieval with complete paragraph context restored during LLM synthesis."
]
curr_y = PAGE_HEIGHT - 2.5 * inch
for b in bullets_s5:
    words = b.split()
    line = ""
    for w in words:
        if len(line + " " + w) > 58:
            c.drawString(1.1 * inch, curr_y, line)
            curr_y -= 0.22 * inch
            line = "  " + w
        else:
            line = line + " " + w if line else w
    if line:
        c.drawString(1.1 * inch, curr_y, line)
        curr_y -= 0.32 * inch

# Right dark card (JSON Schema)
draw_card(c, 6.8, 0.8, 5.7, 5.3, bg_color=DARK_CARD, border_color=None)
c.setFont("Helvetica-Bold", 14)
c.setFillColor(CORAL)
c.drawString(7.1 * inch, PAGE_HEIGHT - 2.0 * inch, "Indexed Vector Schema (Azure AI Search)")

c.setFont("Courier", 10.5)
c.setFillColor(colors.HexColor("#c8dcf0"))
schema_lines = [
    "{",
    '  "chunk_id": "nhlbi-scd-2014-CH-0396",',
    '  "parent_id": "nhlbi-scd-2014-P0077",',
    '  "document_id": "nhlbi-scd-2014",',
    '  "section": "Hydroxyurea Therapy",',
    '  "page_number": 77,',
    '  "text": "In adults with SCA who have >= 3...",',
    '  "vector": [0.0124, -0.0451, ..., 768 dims]',
    "}"
]
curr_y = PAGE_HEIGHT - 2.6 * inch
for l in schema_lines:
    c.drawString(7.1 * inch, curr_y, l)
    curr_y -= 0.28 * inch

c.showPage()

# ══════════════════════════════════════════════════════════════════════
# SLIDE 6: Hybrid Search & Reciprocal Rank Fusion (RRF)
# ══════════════════════════════════════════════
c.setFillColor(LIGHT_BG)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header(c, "Retrieval Architecture", "Hybrid Search & Reciprocal Rank Fusion (RRF)")

steps_s6 = [
    (0.8, "1. Dense Vector Embeddings", "NeuML/biomedbert-base-embeddings", 
     "Transforms clinical queries into 768-dimensional normalized dense vectors. Trained on PubMed and biomedical literature to capture deep clinical semantic relationships."),
    (4.8, "2. Lexical BM25 Search", "Exact Medical Acronym Matching", 
     "Performs inverted-index BM25 lexical search to ensure precise matching for critical medical abbreviations (VOC, ACS, TCD, HbSS, HbSβ⁰) that vector search might blur."),
    (8.8, "3. Reciprocal Rank Fusion", "Server-Side Score Merging", 
     "Azure AI Search merges dense vector and BM25 rankings via RRF algorithm. Scores are calibrated against threshold (0.025) to discard irrelevant questions before generation.")
]

for x, title, sub, desc in steps_s6:
    draw_card(c, x, 0.8, 3.7, 5.3)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(NAVY)
    c.drawString((x + 0.3) * inch, PAGE_HEIGHT - 2.0 * inch, title)
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(CRIMSON)
    c.drawString((x + 0.3) * inch, PAGE_HEIGHT - 2.3 * inch, sub)
    
    c.setFont("Helvetica", 11.5)
    c.setFillColor(MUTED)
    words = desc.split()
    line = ""
    curr_y = PAGE_HEIGHT - 2.9 * inch
    for w in words:
        if len(line + " " + w) > 40:
            c.drawString((x + 0.3) * inch, curr_y, line)
            curr_y -= 0.24 * inch
            line = w
        else:
            line = line + " " + w if line else w
    if line:
        c.drawString((x + 0.3) * inch, curr_y, line)

c.showPage()

# ══════════════════════════════════════════════════════════════════════
# SLIDE 7: Backend & Cloud Infrastructure
# ══════════════════════════════════════════════
c.setFillColor(LIGHT_BG)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header(c, "Cloud & Backend Infrastructure", "FastAPI on Azure App Service & Azure AI Search")

# Left card: FastAPI
draw_card(c, 0.8, 0.8, 5.7, 5.3)
c.setFont("Helvetica-Bold", 15)
c.setFillColor(NAVY)
c.drawString(1.1 * inch, PAGE_HEIGHT - 2.0 * inch, "FastAPI Backend Architecture")

bullets_s7_left = [
    "• High-Performance Async API: Python service built with FastAPI and strict Pydantic schemas.",
    "• Dedicated App Service Linux: Always-On configuration eliminates serverless cold starts.",
    "• Groq LLM Acceleration: Queries openai/gpt-oss-120b in sub-second response times under strict temperature=0 grounding.",
    "• Automated OpenAPI Docs: Live interactive Swagger UI at /docs and monitoring at /health."
]
c.setFont("Helvetica", 11.5)
c.setFillColor(MUTED)
curr_y = PAGE_HEIGHT - 2.5 * inch
for b in bullets_s7_left:
    words = b.split()
    line = ""
    for w in words:
        if len(line + " " + w) > 58:
            c.drawString(1.1 * inch, curr_y, line)
            curr_y -= 0.22 * inch
            line = "  " + w
        else:
            line = line + " " + w if line else w
    if line:
        c.drawString(1.1 * inch, curr_y, line)
        curr_y -= 0.32 * inch

# Right card: Azure Services
draw_card(c, 6.8, 0.8, 5.7, 5.3)
c.setFont("Helvetica-Bold", 15)
c.setFillColor(NAVY)
c.drawString(7.1 * inch, PAGE_HEIGHT - 2.0 * inch, "Azure Cloud Infrastructure")

bullets_s7_right = [
    "• Azure AI Search Index (creativa-hackathon-pc): Hosts 768d vector index with HNSW cosine similarity alongside BM25 indexes.",
    "• Azure App Service (sicklesense-api): Production Linux container hosting the FastAPI backend in Sweden Central region.",
    "• CORS & Security: Secure frontend access without exposing database credentials or API keys.",
    "• Zero-Downtime Reliability: Fully managed scalable cloud instance."
]
c.setFont("Helvetica", 11.5)
c.setFillColor(MUTED)
curr_y = PAGE_HEIGHT - 2.5 * inch
for b in bullets_s7_right:
    words = b.split()
    line = ""
    for w in words:
        if len(line + " " + w) > 58:
            c.drawString(7.1 * inch, curr_y, line)
            curr_y -= 0.22 * inch
            line = "  " + w
        else:
            line = line + " " + w if line else w
    if line:
        c.drawString(7.1 * inch, curr_y, line)
        curr_y -= 0.32 * inch

c.showPage()

# ══════════════════════════════════════════════════════════════════════
# SLIDE 8: Frontend & CI/CD Pipeline
# ══════════════════════════════════════════════════════════════════════
c.setFillColor(LIGHT_BG)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header(c, "Frontend & CI/CD", "Vite + React SPA & GitHub Actions Deployment")

cards_s8 = [
    (0.8, "Modern React UI", "Vite + React + Lucide", [
        "• Navy + Crimson clinical branding matching SickleSense mascot.",
        "• Markdown tables with remark-gfm responsive containers.",
        "• Live backend health checker & interactive FAQ accordion.",
        "• Zero chat clutter: structured evidence notes."
    ]),
    (4.8, "Decoupled Integration", "RESTful JSON Protocol", [
        "• POST /api/query: Sends { query, top_k } payload.",
        "• Dynamic citation mapping displaying score, section, & chunk ID.",
        "• AbortController timeout handling (30s resilience).",
        "• Direct sample query loading from Sources page."
    ]),
    (8.8, "Automated CI/CD", "GitHub Actions & Pages", [
        "• Automated deployment workflow on git push to master.",
        "• Production Vite build outputting optimized static assets.",
        "• Relative base path configuration for reliable subpath routing.",
        "• Zero hosting maintenance overhead."
    ])
]

for x, title, sub, bullets in cards_s8:
    draw_card(c, x, 0.8, 3.7, 5.3)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(NAVY)
    c.drawString((x + 0.3) * inch, PAGE_HEIGHT - 2.0 * inch, title)
    
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(CRIMSON)
    c.drawString((x + 0.3) * inch, PAGE_HEIGHT - 2.3 * inch, sub)
    
    c.setFont("Helvetica", 11)
    c.setFillColor(MUTED)
    curr_y = PAGE_HEIGHT - 2.8 * inch
    for b in bullets:
        words = b.split()
        line = ""
        for w in words:
            if len(line + " " + w) > 42:
                c.drawString((x + 0.3) * inch, curr_y, line)
                curr_y -= 0.22 * inch
                line = "  " + w
            else:
                line = line + " " + w if line else w
        if line:
            c.drawString((x + 0.3) * inch, curr_y, line)
            curr_y -= 0.32 * inch

c.showPage()

# ══════════════════════════════════════════════════════════════════════
# SLIDE 9: Evaluation & Benchmarks
# ══════════════════════════════════════════════════════════════════════
c.setFillColor(LIGHT_BG)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
draw_header(c, "Performance & Verification", "Empirical Evaluation Across 20 Clinical Benchmark Prompts")

# Stat boxes
stat_boxes = [
    (0.8, "Precision@3", "0.500", "50% of top-3 retrieved passages directly answer clinical intent", GREEN),
    (4.8, "Precision@5", "0.463", "Broad clinical context retained across 5 retrieved chunks", NAVY),
    (8.8, "Out-of-Scope Rejection", "100%", "0.000 false-relevance rate on unrelated medical questions", CRIMSON),
]

for x, label, val, note, col in stat_boxes:
    draw_card(c, x, 3.7, 3.7, 2.4)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(MUTED)
    c.drawString((x + 0.3) * inch, PAGE_HEIGHT - 2.0 * inch, label.upper())
    
    c.setFont("Helvetica-Bold", 34)
    c.setFillColor(col)
    c.drawString((x + 0.3) * inch, PAGE_HEIGHT - 2.65 * inch, val)
    
    c.setFont("Helvetica", 10)
    c.setFillColor(MUTED)
    c.drawString((x + 0.3) * inch, PAGE_HEIGHT - 3.1 * inch, note)

# Bottom Box: Benchmark breakdown
draw_card(c, 0.8, 0.8, 11.7, 2.6)
c.setFont("Helvetica-Bold", 13)
c.setFillColor(NAVY)
c.drawString(1.1 * inch, PAGE_HEIGHT - 4.5 * inch, "Benchmark Categories Tested During Development")

bench_bullets = [
    "1. Direct Guideline Fact Lookup (e.g. 'When should hydroxyurea be started in adults?') -> Exact guideline citation matched.",
    "2. Paraphrased Clinical Queries (e.g. 'How to lower alloimmunization risk from transfusion?') -> Correct matching across chapters.",
    "3. Thresholds & Acronyms (e.g. 'What does TCD stand for and how is stroke screened?') -> Precise abbreviation expansion.",
    "4. Out-of-Scope Disease Questions (e.g. 'Ibuprofen dosage for migraine in healthy adult') -> Gated & safely refused.",
    "5. Unsafe Patient-Specific Dosage Inquiries -> Intercepted immediately before LLM invocation."
]
c.setFont("Helvetica", 10.5)
c.setFillColor(MUTED)
curr_y = PAGE_HEIGHT - 4.85 * inch
for b in bench_bullets:
    c.drawString(1.1 * inch, curr_y, b)
    curr_y -= 0.24 * inch

c.showPage()

# ══════════════════════════════════════════════════════════════════════
# SLIDE 10: Conclusion (Dark Navy)
# ══════════════════════════════════════════════
c.setFillColor(NAVY)
c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

c.setFont("Helvetica-Bold", 38)
c.setFillColor(WHITE)
c.drawString(1.2 * inch, PAGE_HEIGHT - 2.0 * inch, "SICKLESENSE")

c.setFont("Helvetica-Oblique", 20)
c.setFillColor(CORAL)
c.drawString(1.2 * inch, PAGE_HEIGHT - 2.5 * inch, '"Sources Before Certainty"')

c.setFont("Helvetica", 13)
c.setFillColor(colors.HexColor("#cbd6e2"))
c.drawString(1.2 * inch, PAGE_HEIGHT - 3.3 * inch, "SickleSense demonstrates how domain-adapted embeddings, parent-child chunking, and hybrid RRF search")
c.drawString(1.2 * inch, PAGE_HEIGHT - 3.65 * inch, "can transform hundreds of pages of complex medical guidelines into an instant, traceable, and safe clinical assistant.")

c.drawString(1.2 * inch, PAGE_HEIGHT - 4.3 * inch, "Live Web App: https://O-076.github.io/sicklesense/")
c.drawString(1.2 * inch, PAGE_HEIGHT - 4.65 * inch, "FastAPI Swagger Docs: https://sicklesense-api-dgh3aqdwb3eghdc4.swedencentral-01.azurewebsites.net/docs")

c.setFont("Helvetica-Bold", 12)
c.setFillColor(colors.HexColor("#a0b4cd"))
c.drawString(1.2 * inch, PAGE_HEIGHT - 5.5 * inch, "Developed with care by Team MINOR THREAT 2026 for the Creativa SCD AI Hackathon")

c.save()
print("PDF Presentation saved successfully to SickleSense_Pitch_Deck.pdf")
