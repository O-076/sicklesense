from typing import List, Literal, Optional
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
