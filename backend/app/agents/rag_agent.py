from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.rag.engine import rag_engine
from app.schemas.rag import RAGQueryResponse

class RAGAgent:
    """
    RAG Agent responsible for retrieving verified evidence from municipal,
    tourism, and local documents, producing answers with strict citations.
    """

    async def answer(self, db: Session, query: str, city_id: Optional[int] = None) -> RAGQueryResponse:
        return await rag_engine.answer_query(db, query=query, city_id=city_id, top_k=4)

rag_agent = RAGAgent()
