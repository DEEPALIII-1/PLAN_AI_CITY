from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class DocumentCreate(BaseModel):
    city_id: int
    title: str
    source_type: str = "official_tourism"
    source_url: Optional[str] = None
    content: str

class DocumentResponse(DocumentCreate):
    id: int
    chunks_count: Optional[int] = 0

    class Config:
        from_attributes = True

class ChunkResponse(BaseModel):
    id: int
    document_id: int
    city_id: int
    chunk_index: int
    content: str
    metadata_json: Dict[str, Any] = {}

    class Config:
        from_attributes = True

class RAGSourceCitation(BaseModel):
    document_id: int
    title: str
    source_type: str
    source_url: Optional[str] = None
    snippet: str
    relevance_score: float

class RAGQueryRequest(BaseModel):
    query: str
    city_id: Optional[int] = None
    top_k: int = 4
    include_raw_chunks: bool = False

class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[RAGSourceCitation] = []
    confidence_score: float
    retrieval_method: str = "hybrid_rrf"
    model_used: str
