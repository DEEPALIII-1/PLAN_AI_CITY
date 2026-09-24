import math
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import Place, Category
from app.schemas.recommendations import RecommendationItem, RecommendationResponse

class RecommendationEngine:
    def __init__(self):
        # Weights for multi-factor scoring model
        self.w_interest = 0.35
        self.w_budget = 0.25
        self.w_rating = 0.20
        self.w_distance = 0.10
        self.w_popularity = 0.10

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates great-circle distance between two points in kilometers."""
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2.0) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    def score_place(
        self,
        place: Place,
        category_name: str,
        user_interests: List[str],
        budget_tier: str,
        max_price: Optional[float],
        user_lat: Optional[float],
        user_lng: Optional[float]
    ) -> Dict[str, Any]:
        """
        Calculates composite recommendation score and generates human-interpretable reasons.
        """
        reasons = []

        # 1. Interest Match (0.0 to 1.0)
        interest_score = 0.2  # baseline
        p_tags = [t.lower() for t in (place.tags or [])]
        cat_lower = category_name.lower()

        matched_interests = []
        for interest in user_interests:
            i_low = interest.lower()
            if i_low in cat_lower or any(i_low in tag for tag in p_tags):
                matched_interests.append(interest)

        if matched_interests:
            interest_score = min(1.0, 0.5 + 0.25 * len(matched_interests))
            reasons.append(f"Matches your interest in {', '.join(matched_interests)}")
        elif user_interests:
            interest_score = 0.3

        # 2. Budget Score (0.0 to 1.0)
        budget_score = 0.8
        tier_price_map = {"budget": 400.0, "moderate": 1200.0, "luxury": 3500.0}
        target_budget = max_price if max_price else tier_price_map.get(budget_tier.lower(), 1000.0)

        cost = place.estimated_cost or 0.0
        if cost <= target_budget:
            budget_score = 1.0
            if cost == 0:
                reasons.append("Free entry / no ticket cost")
            else:
                reasons.append(f"Within your budget (₹{int(cost)} est.)")
        else:
            # Decay score if over budget
            excess = (cost - target_budget) / target_budget
            budget_score = max(0.1, 1.0 - excess)

        # 3. Rating Score (0.0 to 1.0)
        rating = place.rating or 4.0
        rating_score = min(1.0, max(0.0, (rating - 3.0) / 2.0))
        if rating >= 4.6:
            reasons.append(f"Highly rated by visitors ({rating} ★)")

        # 4. Popularity Score
        reviews = place.review_count or 50
        popularity_score = min(1.0, math.log10(max(reviews, 1)) / 3.5)
        if place.is_popular:
            popularity_score = min(1.0, popularity_score + 0.2)
            reasons.append("Top trending attraction in the city")

        # 5. Distance Score (if coordinates provided)
        distance_km = 0.0
        distance_score = 0.8
        if user_lat is not None and user_lng is not None:
            distance_km = self.haversine_distance(user_lat, user_lng, place.latitude, place.longitude)
            # Distance decay: closer than 3km is 1.0, drops to 0.2 at 15km
            distance_score = max(0.2, 1.0 / (1.0 + 0.15 * distance_km))
            if distance_km <= 2.5:
                reasons.append(f"Conveniently close ({round(distance_km, 1)} km away)")

        # Composite Weighted Score
        composite_score = (
            self.w_interest * interest_score +
            self.w_budget * budget_score +
            self.w_rating * rating_score +
            self.w_distance * distance_score +
            self.w_popularity * popularity_score
        )

        return {
            "score": round(composite_score, 3),
            "reasons": reasons[:3],
            "distance_km": round(distance_km, 2),
            "breakdown": {
                "interest_alignment": round(interest_score, 2),
                "budget_fit": round(budget_score, 2),
                "rating_quality": round(rating_score, 2),
                "distance_proximity": round(distance_score, 2),
                "popularity_index": round(popularity_score, 2)
            }
        }

    def recommend(
        self,
        db: Session,
        city_id: int,
        interests: List[str] = [],
        budget_tier: str = "moderate",
        max_price: Optional[float] = None,
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        limit: int = 6
    ) -> List[RecommendationItem]:
        places = db.query(Place, Category).join(
            Category, Place.category_id == Category.id
        ).filter(Place.city_id == city_id).all()

        scored_items = []
        for place, cat in places:
            evaluation = self.score_place(
                place=place,
                category_name=cat.name,
                user_interests=interests,
                budget_tier=budget_tier,
                max_price=max_price,
                user_lat=lat,
                user_lng=lng
            )

            scored_items.append(
                RecommendationItem(
                    place_id=place.id,
                    name=place.name,
                    category=cat.name,
                    rating=place.rating,
                    review_count=place.review_count,
                    estimated_cost=place.estimated_cost,
                    price_level=place.price_level,
                    address=place.address,
                    latitude=place.latitude,
                    longitude=place.longitude,
                    image_url=place.images[0] if place.images else None,
                    match_score=evaluation["score"],
                    match_reasons=evaluation["reasons"],
                    features_breakdown=evaluation["breakdown"]
                )
            )

        scored_items.sort(key=lambda x: x.match_score, reverse=True)
        return scored_items[:limit]

recommendation_engine = RecommendationEngine()
