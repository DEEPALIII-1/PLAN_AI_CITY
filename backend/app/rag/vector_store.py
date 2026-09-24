import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import DocumentChunk, CityDocument

class VectorStore:
    def __init__(self):
        pass

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        a = np.array(v1, dtype=np.float32)
        b = np.array(v2, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def search_similar(
        self,
        db: Session,
        query_vector: List[float],
        city_id: Optional[int] = None,
        top_k: int = 5,
        min_score: float = 0.15
    ) -> List[Dict[str, Any]]:
        """
        Calculates cosine similarities across chunks in database.
        Works across SQLite or PostgreSQL.
        """
        query = db.query(DocumentChunk, CityDocument).join(
            CityDocument, DocumentChunk.document_id == CityDocument.id
        )
        if city_id:
            query = query.filter(DocumentChunk.city_id == city_id)
        
        results = query.all()
        scored_chunks = []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []

        for chunk, doc in results:
            if not chunk.embedding_json:
                continue
            c_vec = np.array(chunk.embedding_json, dtype=np.float32)
            c_norm = np.linalg.norm(c_vec)
            if c_norm == 0:
                continue
            sim = float(np.dot(q_vec, c_vec) / (q_norm * c_norm))
            if sim >= min_score:
                scored_chunks.append({
                    "chunk_id": chunk.id,
                    "document_id": doc.id,
                    "document_title": doc.title,
                    "source_type": doc.source_type,
                    "source_url": doc.source_url,
                    "city_id": chunk.city_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "metadata": chunk.metadata_json or {},
                    "similarity_score": round(sim, 4)
                })

        scored_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_chunks[:top_k]

vector_store = VectorStore()
