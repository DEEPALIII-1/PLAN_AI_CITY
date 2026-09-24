from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ItineraryRequest(BaseModel):
    city_id: int
    budget: float = 2000.0  # In INR
    available_hours: float = 8.0
    start_time: str = "09:00"
    start_location: str = "Railway Station"
    start_lat: Optional[float] = None
    start_lng: Optional[float] = None
    interests: List[str] = ["cafes", "historical"]
    transport_mode: str = "walk_cab"  # walk_cab, public_transit, private_cab, walking
    group_size: int = 1
    pace: str = "medium"  # relaxed, medium, packed
    dietary_preference: Optional[str] = "any"  # veg, non-veg, vegan, any

class ItineraryStop(BaseModel):
    step_number: int
    time_slot: str  # e.g., "09:00 - 10:30"
    type: str  # "attraction", "cafe", "restaurant", "transit", "shopping"
    place_id: Optional[int] = None
    place_name: str
    category: str
    description: str
    estimated_cost: float
    duration_mins: int
    latitude: float
    longitude: float
    address: str
    travel_from_prev_mins: int = 0
    travel_mode: str = "Walking"
    travel_distance_km: float = 0.0
    ai_tips: str
    rag_sources: List[str] = []

class ItineraryPlanResponse(BaseModel):
    city_id: int
    city_name: str
    title: str
    summary: str
    total_budget: float
    estimated_cost: float
    duration_hours: float
    start_location: str
    pace: str
    group_size: int
    stops: List[ItineraryStop]
    budget_breakdown: Dict[str, float] = {}
    weather_advice: str
    crowd_season_tips: str
    ai_reasoning: str
    saved_itinerary_id: Optional[int] = None

class ItinerarySaveRequest(BaseModel):
    title: str
    city_id: int
    total_budget: float
    estimated_cost: float
    duration_hours: float
    start_location: str
    interests: List[str] = []
    pace: str = "medium"
    group_size: int = 1
    transport_mode: str = "walk_cab"
    itinerary_json: Dict[str, Any]
    ai_reasoning: Optional[str] = None
