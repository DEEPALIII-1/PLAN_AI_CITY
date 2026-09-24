from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class EventBase(BaseModel):
    city_id: int
    title: str
    description: str
    venue: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_date: datetime
    end_date: datetime
    price: float = 0.0
    category: str = "Cultural"
    tags: List[str] = []
    image_url: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    city_name: Optional[str] = None

    class Config:
        from_attributes = True
