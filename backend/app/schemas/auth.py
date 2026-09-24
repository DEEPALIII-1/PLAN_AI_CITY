import datetime
from typing import Optional, List
from pydantic import BaseModel

class UserProfileDetailSchema(BaseModel):
    id: Optional[int] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    home_city: Optional[str] = None
    home_state: Optional[str] = None
    country: Optional[str] = "India"
    bio: Optional[str] = None
    preferred_language: Optional[str] = "English"
    account_status: Optional[str] = "active"
    total_itineraries_created: int = 0
    total_places_explored: int = 0
    last_login_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    phone_number: Optional[str] = None
    home_city: Optional[str] = None
    home_state: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    role: str
    full_name: Optional[str] = None
    home_city: Optional[str] = None
    home_state: Optional[str] = None

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None

class UserPreferenceSchema(BaseModel):
    preferred_categories: List[str] = []
    budget_tier: str = "moderate"
    travel_style: str = "solo"
    preferred_pace: str = "medium"
    favorite_place_ids: List[int] = []
    cluster_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    preference: Optional[UserPreferenceSchema] = None
    profile: Optional[UserProfileDetailSchema] = None

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    home_city: Optional[str] = None
    home_state: Optional[str] = None
    bio: Optional[str] = None
    preferred_categories: Optional[List[str]] = None
    budget_tier: Optional[str] = None
    travel_style: Optional[str] = None
    preferred_pace: Optional[str] = None
    favorite_place_ids: Optional[List[int]] = None
