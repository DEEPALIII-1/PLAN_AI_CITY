from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import SearchQueryLog, Place, Category, City
from app.rag.embedder import embedder
from app.rag.vector_store import vector_store
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/")
async def search_city_knowledge(
    q: str = Query(..., min_length=2),
    city_id: Optional[int] = Query(None),
    limit: int = Query(10),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    Hybrid semantic & keyword search across places and city entities.
    """
    # 1. Search places by keyword & metadata
    query_pattern = f"%{q}%"
    place_results = db.query(Place, Category, City).join(
        Category, Place.category_id == Category.id
    ).join(
        City, Place.city_id == City.id
    )
    if city_id:
        place_results = place_results.filter(Place.city_id == city_id)

    matched_places = place_results.filter(
        (Place.name.ilike(query_pattern)) |
        (Place.description.ilike(query_pattern)) |
        (Category.name.ilike(query_pattern))
    ).limit(limit).all()

    places_data = []
    for p, cat, c in matched_places:
        places_data.append({
            "id": p.id,
            "name": p.name,
            "category": cat.name,
            "city": c.name,
            "description": p.description,
            "rating": p.rating,
            "cost": p.estimated_cost,
            "type": "place"
        })

    # 2. Vector search on document knowledge chunks
    q_vec = await embedder.get_embedding(q)
    doc_chunks = vector_store.search_similar(
        db, query_vector=q_vec, city_id=city_id, top_k=4, min_score=0.25
    )

    # 3. Log query for city analytics
    log = SearchQueryLog(
        user_id=user.id if user else None,
        query=q,
        city_id=city_id,
        search_type="hybrid_search",
        filters_applied={"city_id": city_id, "limit": limit}
    )
    db.add(log)
    db.commit()

    return {
        "query": q,
        "places": places_data,
        "knowledge_snippets": [
            {
                "title": c["document_title"],
                "source": c["source_type"],
                "content": c["content"],
                "relevance": c["similarity_score"]
            }
            for c in doc_chunks
        ]
    }
