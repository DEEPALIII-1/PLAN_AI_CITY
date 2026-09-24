from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class CategoryStat(BaseModel):
    category: str
    count: int
    avg_price: float

class PriceDistribution(BaseModel):
    tier: str  # "Budget (₹0-500)", "Moderate (₹500-1500)", "Premium (₹1500+)"
    percentage: float
    place_count: int

class UserPersonaCluster(BaseModel):
    cluster_id: int
    persona_name: str
    description: str
    percentage: float
    key_traits: List[str]

class CityAnalyticsResponse(BaseModel):
    city_id: Optional[int] = None
    city_name: Optional[str] = "All Cities"
    total_places: int
    total_events: int
    total_documents: int
    total_itineraries_generated: int
    total_queries: int
    avg_itinerary_budget: float
    category_distribution: List[CategoryStat]
    price_distribution: List[PriceDistribution]
    user_persona_clusters: List[UserPersonaCluster]
    top_search_queries: List[Dict[str, Any]]
    popular_places: List[Dict[str, Any]]
