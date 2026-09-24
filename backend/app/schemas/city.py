from typing import List, Optional
from pydantic import BaseModel

class CityBase(BaseModel):
    name: str
    slug: str
    state: str
    district: Optional[str] = None
    country: str = "India"
    locality_type: Optional[str] = "city"  # city, town, village, coastal, hill_station
    description: str
    latitude: float
    longitude: float
    hero_image: Optional[str] = None
    best_time_to_visit: Optional[str] = None
    weather_summary: Optional[str] = None
    vibe_tags: List[str] = []
    is_featured: bool = False

class CityCreate(CityBase):
    pass

class CityResponse(CityBase):
    id: int
    places_count: Optional[int] = 0
    events_count: Optional[int] = 0

    class Config:
        from_attributes = True

class CityDetailResponse(CityResponse):
    top_categories: List[str] = []
    popular_places: List[dict] = []
    upcoming_events: List[dict] = []
