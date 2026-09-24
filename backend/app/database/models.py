import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default="user")  # "user", "admin", "superadmin"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    preference = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    itineraries = relationship("Itinerary", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("PlaceReview", back_populates="user")
    search_logs = relationship("SearchQueryLog", back_populates="user")

class UserProfile(Base):
    """
    Dedicated user profile and account details table storing extended registration information,
    travel background, contact info, home location, and activity metrics.
    """
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    full_name = Column(String(150), nullable=True)
    email = Column(String(255), nullable=False, index=True)
    phone_number = Column(String(30), nullable=True)
    home_city = Column(String(100), nullable=True)
    home_state = Column(String(100), nullable=True)
    country = Column(String(100), default="India")
    bio = Column(Text, nullable=True)
    preferred_language = Column(String(50), default="English")
    account_status = Column(String(50), default="active")  # active, verified
    total_itineraries_created = Column(Integer, default=0)
    total_places_explored = Column(Integer, default=0)
    last_login_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="profile")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    preferred_categories = Column(JSON, default=list)  # ["cafes", "heritage", "nature"]
    budget_tier = Column(String(20), default="moderate")  # "budget", "moderate", "luxury"
    travel_style = Column(String(50), default="solo")  # "solo", "couple", "family", "backpacking"
    preferred_pace = Column(String(20), default="medium")  # "relaxed", "medium", "packed"
    favorite_place_ids = Column(JSON, default=list)
    cluster_id = Column(Integer, nullable=True)  # Assigned by K-Means ML clustering
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="preference")

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=True)
    country = Column(String(100), default="India")
    locality_type = Column(String(50), default="city")  # "city", "town", "village", "heritage_site", "hill_station"
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    hero_image = Column(String(500), nullable=True)
    best_time_to_visit = Column(String(100), nullable=True)
    weather_summary = Column(String(255), nullable=True)
    vibe_tags = Column(JSON, default=list)  # ["Hills", "Colonial Heritage", "Winter Snow"]
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    places = relationship("Place", back_populates="city", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="city", cascade="all, delete-orphan")
    documents = relationship("CityDocument", back_populates="city", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="city", cascade="all, delete-orphan")
    itineraries = relationship("Itinerary", back_populates="city")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, index=True, nullable=False)
    icon = Column(String(50), default="MapPin")
    description = Column(String(255), nullable=True)
    display_order = Column(Integer, default=0)

    places = relationship("Place", back_populates="category")

class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)
    slug = Column(String(150), index=True, nullable=False)
    description = Column(Text, nullable=False)
    address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    price_level = Column(Integer, default=2)  # 1 = Cheap, 2 = Moderate, 3 = Expensive, 4 = Fine dining/luxury
    estimated_cost = Column(Float, default=0.0)  # Average cost per person in INR
    avg_visit_duration_mins = Column(Integer, default=60)
    opening_time = Column(String(10), default="09:00")
    closing_time = Column(String(10), default="19:00")
    rating = Column(Float, default=4.5)
    review_count = Column(Integer, default=100)
    tags = Column(JSON, default=list)  # ["historical", "viewpoint", "café", "romantic"]
    images = Column(JSON, default=list)
    child_friendly = Column(Boolean, default=True)
    family_friendly = Column(Boolean, default=True)
    accessibility = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)
    seasonal_notes = Column(String(255), nullable=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    city = relationship("City", back_populates="places")
    category = relationship("Category", back_populates="places")
    reviews = relationship("PlaceReview", back_populates="place", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    venue = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    price = Column(Float, default=0.0)
    category = Column(String(50), default="Cultural")
    tags = Column(JSON, default=list)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    city = relationship("City", back_populates="events")

class CityDocument(Base):
    __tablename__ = "city_documents"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    source_type = Column(String(50), default="official_tourism")  # official_tourism, local_guide, faq, transport
    source_url = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    city = relationship("City", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("city_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, default=0)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)  # {"title": "...", "source": "...", "child_friendly": true}
    embedding_json = Column(JSON, nullable=True)  # Stores float array vector
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("CityDocument", back_populates="chunks")
    city = relationship("City", back_populates="chunks")

class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    start_date = Column(String(50), nullable=True)
    total_budget = Column(Float, nullable=False)
    estimated_cost = Column(Float, default=0.0)
    duration_hours = Column(Float, default=8.0)
    start_location = Column(String(150), default="Railway Station")
    start_latitude = Column(Float, nullable=True)
    start_longitude = Column(Float, nullable=True)
    interests = Column(JSON, default=list)  # ["cafes", "historical"]
    pace = Column(String(30), default="medium")  # relaxed, medium, fast
    group_size = Column(Integer, default=1)
    transport_mode = Column(String(50), default="walk_cab")
    itinerary_json = Column(JSON, nullable=False)  # Full schedule array with timings, places, food, explanations
    ai_reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="itineraries")
    city = relationship("City", back_populates="itineraries")

class SearchQueryLog(Base):
    __tablename__ = "search_query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    query = Column(String(500), nullable=False)
    city_id = Column(Integer, nullable=True)
    search_type = Column(String(50), default="hybrid")  # keyword, semantic, rag_qa, itinerary
    filters_applied = Column(JSON, default=dict)
    response_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="search_logs")

class PlaceReview(Base):
    __tablename__ = "place_reviews"

    id = Column(Integer, primary_key=True, index=True)
    place_id = Column(Integer, ForeignKey("places.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rating = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    place = relationship("Place", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
