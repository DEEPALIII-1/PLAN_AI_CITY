from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class RecommendationRequest(BaseModel):
    city_id: int
    user_id: Optional[int] = None
    interests: List[str] = []
    budget_tier: Optional[str] = "moderate"
    max_price: Optional[float] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_km: Optional[float] = 10.0
    limit: int = 6

class RecommendationItem(BaseModel):
    place_id: int
    name: str
    category: str
    rating: float
    review_count: int
    estimated_cost: float
    price_level: int
    address: str
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    match_score: float
    match_reasons: List[str] = []
    features_breakdown: Dict[str, float] = {}

class RecommendationResponse(BaseModel):
    city_name: str
    user_persona_applied: str
    recommendations: List[RecommendationItem] = []
