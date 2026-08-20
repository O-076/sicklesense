import os

FILES = {}

# ---------------------------------------------------------------------------
# 1. app/models/schemas.py
# ---------------------------------------------------------------------------
FILES["app/models/schemas.py"] = '''from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., description="The clinical query")
    top_k: int = Field(default=7, ge=1, le=20, description="Number of evidence chunks to retrieve")

class CitationItem(BaseModel):
    document: str
    section: str
    page: int
    chunk_id: str

class VerificationItem(BaseModel):
    chunk_id: str
    status: str
    passed: bool

class GroundedResponse(BaseModel):
    query: str
    recommendation: str
    evidence: str
    citations: List[CitationItem]
    confidence: Literal["high", "medium", "low", "insufficient"]
    verification_status: List[VerificationItem] = Field(default_factory=list)

class HealthResponse(BaseModel):
    status: str
    model: str
    index: str
'''

# ---------------------------------------------------------------------------
# 2. app/services/safety.py
# ---------------------------------------------------------------------------
FILES["app/services/safety.py"] = '''import re

PATIENT_SPECIFIC_PATTERNS = [
    r'\\bmy (son|daughter|child|wife|husband|patient|father|mother)\\b',
    r'\\bi (have|am|take|was diagnosed)\\b',
    r'\\bshould i (take|give|start|stop)\\b',
    r'\\bwhat dose should i\\b',
    r'\\bcan i give\\b',
    r'\\bis it safe for me\\b',
]

PATIENT_SAFETY_REFUSAL = {
    "recommendation": (
        "I can't provide individualized dosing or treatment instructions for a specific patient. "
        "The appropriate approach should be determined by a qualified clinician using the patient's clinical assessment."
    ),
    "evidence": "",
    "citations": [],
    "confidence": "insufficient",
}

INSUFFICIENT_EVIDENCE_REFUSAL = {
    "recommendation": (
        "The indexed guidelines do not appear to cover this topic with enough confidence for an answer. "
        "Rephrasing may help, or the topic may fall outside the indexed evidence scope."
    ),
    "evidence": "",
    "citations": [],
    "confidence": "insufficient",
}

def is_patient_specific(question: str) -> bool:
    """Checks for patient-specific phrases to trigger the safety gate."""
    lowered = question.lower()
    return any(re.search(p, lowered) for p in PATIENT_SPECIFIC_PATTERNS)
'''

# ---------------------------------------------------------------------------
# 3. app/services/rag_engine.py
# ---------------------------------------------------------------------------
FILES["app/services/rag_engine.py"] = '''import json
from groq import Groq
from app.services.safety import (
    is_patient_specific,
    PATIENT_SAFETY_REFUSAL,
    INSUFFICIENT_EVIDENCE_REFUSAL,
)

GROUNDING_SYSTEM_PROMPT = """You are a citation-bound clinical evidence assistant for sickle cell disease.

Rules:
1. Answer ONLY using the evidence passages provided below. Do not use outside medical knowledge.
2. Every claim in "recommendation" must be directly supported by the text in "evidence".
3. Return the answer as a JSON object matching exactly this structure:
   {
     "recommendation": "...",
     "evidence": "...",
     "citations": [{"document": "...", "section": "...", "page": N, "chunk_id": "..."}],
     "confidence": "high" | "medium" | "low" | "insufficient"
   }
4. If the evidence does not contain enough information to answer with confidence, confidence is set to "insufficient", "evidence" and "citations" are left empty, and "recommendation" contains a plain refusal rather than a guess.
5. Citations are never invented. A refusal is never softened into a partial guess.
6. Patient-specific medical advice is strictly prohibited. Do not diagnose, prescribe, calculate, recommend, or select a treatment, dose, frequency, duration, monitoring schedule, or treatment change for a specific or implied individual patient.
7. Do not apply general clinical recommendations, thresholds, formulas, weight-based doses, age-based recommendations, laboratory values, or other guideline criteria to the characteristics of an individual patient. General clinical information may be provided only when it is clearly presented as general guidance rather than an individualized recommendation.
8. Treat a question as patient-specific when it provides characteristics of an individual, such as age, weight, symptoms, laboratory values, diagnosis, medical history, current medications, or treatment response, and asks what should be done for that individual. If so, refuse the personalized request even when the supplied evidence contains enough information to answer it.
9. Do not perform arithmetic, calculations, or other transformations on guideline information when doing so would produce a personalized dose, treatment recommendation, monitoring decision, or other clinical decision. When refusing a patient-specific request, set "confidence" to "insufficient" and leave "evidence" and "citations" empty. The "recommendation" should briefly explain that the system provides general clinical information and cannot make individualized medical decisions.
"""

# Calibrated relevance cutoff for Azure AI Search RRF scores
RETRIEVAL_THRESHOLD = 0.020

def verify_citations(answer: dict, evidence_blocks: list) -> list:
    """Verifies that every cited chunk_id was in retrieved context and checks lexical overlap."""
    evidence_by_id = {e["chunk_id"]: e for e in evidence_blocks}
    report = []
    
    for c in answer.get("citations", []):
        cid = c.get("chunk_id")
        if cid not in evidence_by_id:
            report.append({
                "chunk_id": cid or "unknown",
                "status": "fabricated citation: chunk_id not present in retrieved evidence",
                "passed": False
            })
            continue
            
        real_text = evidence_by_id[cid]["text"].lower()
        rec_words = answer.get("recommendation", "").lower().split()[:6]
        overlap_ok = any(word in real_text for word in rec_words)
        
        status = "passed" if overlap_ok else "flagged for manual review: low lexical overlap"
        report.append({
            "chunk_id": cid,
            "status": status,
            "passed": True
        })
    return report

def run_grounded_rag(query: str, retrieved_chunks: list, groq_client: Groq, model: str) -> dict:
    """Runs the 4-gate grounded generation pipeline."""
    # Gate 1: Patient-specific safety gate
    if is_patient_specific(query):
        res = PATIENT_SAFETY_REFUSAL.copy()
        res["verification_status"] = [{"chunk_id": "none", "status": "blocked by patient safety gate", "passed": True}]
        return res

    # Gate 2: Evidence relevance threshold gate
    top_score = retrieved_chunks[0]["score"] if retrieved_chunks else 0.0
    if top_score < RETRIEVAL_THRESHOLD:
        res = INSUFFICIENT_EVIDENCE_REFUSAL.copy()
        res["verification_status"] = [{"chunk_id": "none", "status": f"score ({top_score:.4f}) below threshold", "passed": True}]
        return res

    # Context construction
    context = "\\n\\n---\\n\\n".join([
        f"[chunk_id: {c['chunk_id']} | document: {c['document']} | section: {c['section']} | page: {c['page']}]\\n{c['text']}"
        for c in retrieved_chunks
    ])
    user_prompt = f"Evidence:\\n{context}\\n\\nQuestion: {query}\\n\\nThe response is the JSON object described in the system rules, with no additional text."

    # Gate 3: Constrained JSON generation via Groq
    response = groq_client.chat.completions.create(
        model=model,
        temperature=0.0,
        max_tokens=1200,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": GROUNDING_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    
    raw = response.choices[0].message.content
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "recommendation": "Internal error: Generation output was not valid JSON.",
            "evidence": "",
            "citations": [],
            "confidence": "insufficient",
            "verification_status": [{"chunk_id": "none", "status": "json_decode_error", "passed": False}]
        }

    # Gate 4: Citation verification
    verification = verify_citations(parsed, retrieved_chunks)
    
    # If any citation was fabricated, mark confidence as insufficient
    if any(not v["passed"] for v in verification):
        parsed["confidence"] = "insufficient"
        
    parsed["verification_status"] = verification
    return parsed
'''

# ---------------------------------------------------------------------------
# 4. app/services/search_service.py
# ---------------------------------------------------------------------------
FILES["app/services/search_service.py"] = '''from sentence_transformers import SentenceTransformer
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from app.config import settings

class SearchService:
    def __init__(self):
        # Using the biomedical PubMedBERT embedding model
        self.embedding_model = SentenceTransformer(
            "NeuML/biomedbert-base-embeddings",
            cache_folder="/tmp/huggingface"
        )
        self.client = SearchClient(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            index_name=settings.AZURE_SEARCH_INDEX,
            credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY),
        )

    def retrieve_hybrid(self, query: str, k: int = 7) -> list:
        # Generate query vector with normalization
        query_vector = self.embedding_model.encode(
            query, normalize_embeddings=True
        ).tolist()

        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=k,
            fields="content_vector",
        )

        results = self.client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=["chunk_id", "document_id", "title", "citation", "section", "page_number", "content"],
            top=k,
        )

        chunks = []
        for r in results:
            chunks.append({
                "chunk_id": r["chunk_id"],
                "document": r.get("document_id", "Unknown"),
                "title": r.get("title", ""),
                "citation": r.get("citation", ""),
                "section": r.get("section", "General / Unclassified"),
                "page": r.get("page_number", 0),
                "text": r.get("content", ""),
                "score": float(r.get("@search.score", 0.0)),
            })
        return chunks

search_service = SearchService()
'''

# ---------------------------------------------------------------------------
# 5. app/config.py
# ---------------------------------------------------------------------------
FILES["app/config.py"] = '''import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AZURE_SEARCH_ENDPOINT: str = os.getenv("AZURE_SEARCH_ENDPOINT", "https://creativa-hackathon-vb.search.windows.net")
    AZURE_SEARCH_KEY: str = os.getenv("AZURE_SEARCH_KEY", "")
    AZURE_SEARCH_INDEX: str = os.getenv("AZURE_SEARCH_INDEX", "creativa-hackathon-pc")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
'''

# ---------------------------------------------------------------------------
# 6. app/main.py
# ---------------------------------------------------------------------------
FILES["app/main.py"] = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq

from app.config import settings
from app.models.schemas import QueryRequest, GroundedResponse, HealthResponse
from app.services.search_service import search_service
from app.services.rag_engine import run_grounded_rag

app = FastAPI(
    title="SickleSense Clinical Evidence API",
    version="2.0.0",
    description="Grounded, Citation-Bound RAG Engine for Sickle Cell Disease Guidelines",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

groq_client = Groq(api_key=settings.GROQ_API_KEY)

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        model=settings.GROQ_MODEL,
        index=settings.AZURE_SEARCH_INDEX,
    )

@app.post("/api/query", response_model=GroundedResponse)
def clinical_query(request: QueryRequest):
    # 1. Retrieve hybrid chunks from Azure AI Search
    retrieved_chunks = search_service.retrieve_hybrid(request.query, k=request.top_k)
    
    # 2. Run Grounded Engine with safety and citation verification
    result = run_grounded_rag(
        query=request.query,
        retrieved_chunks=retrieved_chunks,
        groq_client=groq_client,
        model=settings.GROQ_MODEL,
    )
    
    return GroundedResponse(
        query=request.query,
        recommendation=result.get("recommendation", ""),
        evidence=result.get("evidence", ""),
        citations=result.get("citations", []),
        confidence=result.get("confidence", "insufficient"),
        verification_status=result.get("verification_status", []),
    )
'''

def main():
    print("Writing updated files to sickle-sense backend...")
    for file_path, content in FILES.items():
        dir_name = os.path.dirname(file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            print(f"Created directory: {dir_name}")
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.lstrip())
        print(f"Wrote file: {file_path}")

    # Ensure __init__.py files exist
    for init_dir in ["app", "app/models", "app/services"]:
        init_file = os.path.join(init_dir, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w", encoding="utf-8") as f:
                f.write("")
            print(f"Created init: {init_file}")

    print("\\nAll backend files have been updated successfully with the full grounded pipeline.")

if __name__ == "__main__":
    main()