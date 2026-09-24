from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import CityDocument, DocumentChunk, SearchQueryLog
from app.schemas.rag import (
    RAGQueryRequest, RAGQueryResponse, DocumentCreate, DocumentResponse
)
from app.rag.engine import rag_engine
from app.rag.chunker import chunker
from app.rag.embedder import embedder
from app.api.deps import require_admin_user, get_current_user

router = APIRouter()

@router.post("/query", response_model=RAGQueryResponse)
async def rag_query(
    req: RAGQueryRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    RAG-powered question answering over verified city documentation.
    Returns factual grounded answer along with exact source citations and confidence metrics.
    """
    res = await rag_engine.answer_query(
        db, query=req.query, city_id=req.city_id, top_k=req.top_k
    )

    # Log search for city analytics
    try:
        log = SearchQueryLog(
            user_id=user.id if user else None,
            query=req.query,
            city_id=req.city_id,
            search_type="rag_qa",
            filters_applied={"top_k": req.top_k, "confidence": res.confidence_score}
        )
        db.add(log)
        db.commit()
    except Exception:
        pass

    return res

@router.get("/documents", response_model=List[DocumentResponse])
def list_city_documents(
    city_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(CityDocument)
    if city_id:
        q = q.filter(CityDocument.city_id == city_id)
    docs = q.all()

    out = []
    for d in docs:
        chunks_count = db.query(DocumentChunk).filter(DocumentChunk.document_id == d.id).count()
        out.append(DocumentResponse(
            id=d.id,
            city_id=d.city_id,
            title=d.title,
            source_type=d.source_type,
            source_url=d.source_url,
            content=d.content,
            chunks_count=chunks_count
        ))
    return out

@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(
    doc_in: DocumentCreate,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_user)
):
    """
    Ingests a document, chunks it, generates embeddings, and indexes in vector database.
    """
    doc = CityDocument(**doc_in.model_dump())
    db.add(doc)
    db.flush()

    raw_chunks = chunker.chunk_text(
        doc.content,
        metadata={"title": doc.title, "source": doc.source_type, "city_id": doc.city_id}
    )

    for c in raw_chunks:
        emb = await embedder.get_embedding(c["content"])
        chunk_obj = DocumentChunk(
            document_id=doc.id,
            city_id=doc.city_id,
            chunk_index=c["chunk_index"],
            content=c["content"],
            metadata_json=c["metadata"],
            embedding_json=emb
        )
        db.add(chunk_obj)

    db.commit()
    db.refresh(doc)

    return DocumentResponse(
        id=doc.id,
        city_id=doc.city_id,
        title=doc.title,
        source_type=doc.source_type,
        source_url=doc.source_url,
        content=doc.content,
        chunks_count=len(raw_chunks)
    )
