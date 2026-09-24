from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.models import Place, Category

class SearchAgent:
    """
    Handles candidate retrieval for places, cafes, and dining spots matching query criteria.
    """

    def search_places(
        self,
        db: Session,
        city_id: int,
        query: Optional[str] = None,
        category_slug: Optional[str] = None,
        max_price: Optional[float] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        q = db.query(Place, Category).join(Category, Place.category_id == Category.id).filter(Place.city_id == city_id)

        if category_slug:
            q = q.filter(Category.slug == category_slug)

        if max_price is not None:
            q = q.filter(Place.estimated_cost <= max_price)

        if query:
            search_pattern = f"%{query}%"
            q = q.filter(
                or_(
                    Place.name.ilike(search_pattern),
                    Place.description.ilike(search_pattern),
                    Category.name.ilike(search_pattern)
                )
            )

        places = q.order_by(Place.rating.desc()).limit(limit).all()

        results = []
        for p, c in places:
            results.append({
                "id": p.id,
                "name": p.name,
                "category": c.name,
                "category_slug": c.slug,
                "description": p.description,
                "address": p.address,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "estimated_cost": p.estimated_cost,
                "price_level": p.price_level,
                "avg_visit_duration_mins": p.avg_visit_duration_mins,
                "opening_time": p.opening_time,
                "closing_time": p.closing_time,
                "rating": p.rating,
                "review_count": p.review_count,
                "tags": p.tags or [],
                "images": p.images or [],
                "child_friendly": p.child_friendly,
                "is_popular": p.is_popular
            })
        return results

search_agent = SearchAgent()
