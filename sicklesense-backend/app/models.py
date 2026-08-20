from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Clinical query regarding Sickle Cell Disease")
    top_k: Optional[int] = Field(default=5, ge=1, le=10, description="Number of parent context chunks to return")

class CitationSource(BaseModel):
    chunk_id: str
    parent_id: str
    document_id: str
    title: str
    citation: str
    section: str
    page_number: int
    score: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[CitationSource]
    query: str
