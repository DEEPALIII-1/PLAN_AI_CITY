import re
import math
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import DocumentChunk, CityDocument
from app.rag.embedder import embedder
from app.rag.vector_store import vector_store

class HybridRetriever:
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k

    def _keyword_search(
        self,
        db: Session,
        query: str,
        city_id: Optional[int] = None,
        top_k: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Calculates term frequency - inverse document frequency relevance for chunks.
        """
        q_tokens = set(re.findall(r'\b[a-zA-Z0-9]{3,}\b', query.lower()))
        if not q_tokens:
            return []

        chunks_query = db.query(DocumentChunk, CityDocument).join(
            CityDocument, DocumentChunk.document_id == CityDocument.id
        )
        if city_id:
            chunks_query = chunks_query.filter(DocumentChunk.city_id == city_id)
        
        all_chunks = chunks_query.all()
        scored = []

        total_docs = max(len(all_chunks), 1)

        for chunk, doc in all_chunks:
            text = (chunk.content + " " + doc.title).lower()
            score = 0.0
            for token in q_tokens:
                count = text.count(token)
                if count > 0:
                    # BM25-style saturation: tf / (tf + 1.2)
                    tf = count / (count + 1.2)
                    score += tf

            if score > 0:
                scored.append({
                    "chunk_id": chunk.id,
                    "document_id": doc.id,
                    "document_title": doc.title,
                    "source_type": doc.source_type,
                    "source_url": doc.source_url,
                    "city_id": chunk.city_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "metadata": chunk.metadata_json or {},
                    "keyword_score": round(score, 4)
                })

        scored.sort(key=lambda x: x["keyword_score"], reverse=True)
        return scored[:top_k]

    async def hybrid_search(
        self,
        db: Session,
        query: str,
        city_id: Optional[int] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Combines BM25 Keyword Search and Dense Vector Cosine Similarity
        using Reciprocal Rank Fusion (RRF).
        """
        # 1. Run keyword search
        kw_results = self._keyword_search(db, query, city_id=city_id, top_k=top_k * 2)

        # 2. Run vector search
        q_vector = await embedder.get_embedding(query)
        vec_results = vector_store.search_similar(
            db, q_vector, city_id=city_id, top_k=top_k * 2
        )

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        chunk_map = {}

        for rank, res in enumerate(kw_results):
            cid = res["chunk_id"]
            chunk_map[cid] = res
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank + 1))

        for rank, res in enumerate(vec_results):
            cid = res["chunk_id"]
            if cid not in chunk_map:
                chunk_map[cid] = res
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank + 1))

        # Rank by combined RRF score
        combined = []
        for cid, score in rrf_scores.items():
            item = dict(chunk_map[cid])
            item["rrf_score"] = round(score, 5)
            combined.append(item)

        combined.sort(key=lambda x: x["rrf_score"], reverse=True)
        return combined[:top_k]

retriever = HybridRetriever()
