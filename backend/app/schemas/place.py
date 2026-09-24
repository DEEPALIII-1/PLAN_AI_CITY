from typing import List, Optional
from pydantic import BaseModel

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    icon: Optional[str] = "MapPin"
    description: Optional[str] = None

    class Config:
        from_attributes = True

class PlaceBase(BaseModel):
    city_id: int
    category_id: int
    name: str
    slug: str
    description: str
    address: str
    latitude: float
    longitude: float
    price_level: int = 2
    estimated_cost: float = 0.0
    avg_visit_duration_mins: int = 60
    opening_time: str = "09:00"
    closing_time: str = "19:00"
    rating: float = 4.5
    review_count: int = 100
    tags: List[str] = []
    images: List[str] = []
    child_friendly: bool = True
    family_friendly: bool = True
    accessibility: bool = True
    is_popular: bool = False
    seasonal_notes: Optional[str] = None

class PlaceCreate(BaseModel):
    city_id: int
    category_id: int
    name: str
    slug: Optional[str] = None
    description: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    price_level: int = 2
    estimated_cost: float = 0.0
    avg_visit_duration_mins: int = 60
    opening_time: str = "09:00"
    closing_time: str = "19:00"
    rating: float = 4.5
    review_count: int = 1
    tags: List[str] = []
    images: List[str] = []
    child_friendly: bool = True
    family_friendly: bool = True
    accessibility: bool = True
    is_popular: bool = False
    seasonal_notes: Optional[str] = None

class PlaceResponse(PlaceBase):
    id: int
    category_name: Optional[str] = None
    city_name: Optional[str] = None
    distance_km: Optional[float] = None
    match_score: Optional[float] = None

    class Config:
        from_attributes = True

class PlaceFilterParams(BaseModel):
    city_id: Optional[int] = None
    category_slug: Optional[str] = None
    max_price: Optional[float] = None
    child_friendly: Optional[bool] = None
    is_popular: Optional[bool] = None
    search: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_km: Optional[float] = None
