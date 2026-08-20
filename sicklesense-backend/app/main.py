from fastapi import FastAPI
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
