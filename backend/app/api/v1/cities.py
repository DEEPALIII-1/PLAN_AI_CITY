from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import City, Place, Event, Category
from app.schemas.city import CityResponse, CityDetailResponse, CityCreate
from app.api.deps import require_admin_user

from app.services.india_geo import india_geo, INDIAN_STATES
from pydantic import BaseModel

class ResolveCityRequest(BaseModel):
    query: str

router = APIRouter()

@router.get("/states")
def get_all_states():
    return {"states": INDIAN_STATES}

@router.get("/search")
async def search_indian_localities(
    q: str = "",
    limit: int = 15,
    db: Session = Depends(get_db)
):
    """
    Search any Indian city, district, town, or village across India.
    Matches seeded database and queries OpenStreetMap India when needed.
    """
    results = await india_geo.search_localities(db, query=q, limit=limit)
    return results

@router.post("/resolve", response_model=CityResponse)
async def resolve_indian_locality(
    req: ResolveCityRequest,
    db: Session = Depends(get_db)
):
    """
    Resolves or dynamically creates a city, town, or village from any Indian location query.
    If not already in the database, automatically geocodes it and provisions authentic places and RAG documents!
    """
    city = await india_geo.resolve_or_create_locality(db, query=req.query)
    p_count = db.query(Place).filter(Place.city_id == city.id).count()
    e_count = db.query(Event).filter(Event.city_id == city.id).count()
    return CityResponse(
        id=city.id,
        name=city.name,
        slug=city.slug,
        state=city.state,
        district=city.district,
        country=city.country,
        locality_type=city.locality_type,
        description=city.description,
        latitude=city.latitude,
        longitude=city.longitude,
        hero_image=city.hero_image,
        best_time_to_visit=city.best_time_to_visit,
        weather_summary=city.weather_summary,
        vibe_tags=city.vibe_tags or [],
        is_featured=city.is_featured,
        places_count=p_count,
        events_count=e_count
    )

@router.get("/", response_model=List[CityResponse])
def list_cities(db: Session = Depends(get_db)):
    cities = db.query(City).order_by(City.is_featured.desc(), City.name.asc()).all()
    results = []
    for c in cities:
        p_count = db.query(Place).filter(Place.city_id == c.id).count()
        e_count = db.query(Event).filter(Event.city_id == c.id).count()
        res = CityResponse(
            id=c.id,
            name=c.name,
            slug=c.slug,
            state=c.state,
            district=c.district,
            country=c.country,
            locality_type=c.locality_type,
            description=c.description,
            latitude=c.latitude,
            longitude=c.longitude,
            hero_image=c.hero_image,
            best_time_to_visit=c.best_time_to_visit,
            weather_summary=c.weather_summary,
            vibe_tags=c.vibe_tags or [],
            is_featured=c.is_featured,
            places_count=p_count,
            events_count=e_count
        )
        results.append(res)
    return results

@router.get("/{id_or_slug}", response_model=CityDetailResponse)
def get_city_detail(id_or_slug: str, db: Session = Depends(get_db)):
    if id_or_slug.isdigit():
        city = db.query(City).filter(City.id == int(id_or_slug)).first()
    else:
        city = db.query(City).filter(City.slug == id_or_slug.lower()).first()

    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    places = db.query(Place, Category).join(
        Category, Place.category_id == Category.id
    ).filter(Place.city_id == city.id).all()

    popular = []
    categories_set = set()
    for p, cat in places:
        categories_set.add(cat.name)
        if p.is_popular or p.rating >= 4.6:
            popular.append({
                "id": p.id,
                "name": p.name,
                "category": cat.name,
                "rating": p.rating,
                "review_count": p.review_count,
                "estimated_cost": p.estimated_cost,
                "image": p.images[0] if p.images else None,
                "address": p.address
            })

    events = db.query(Event).filter(Event.city_id == city.id).limit(5).all()
    events_data = [{
        "id": e.id,
        "title": e.title,
        "venue": e.venue,
        "price": e.price,
        "start_date": e.start_date.isoformat(),
        "category": e.category
    } for e in events]

    return CityDetailResponse(
        id=city.id,
        name=city.name,
        slug=city.slug,
        state=city.state,
        country=city.country,
        description=city.description,
        latitude=city.latitude,
        longitude=city.longitude,
        hero_image=city.hero_image,
        best_time_to_visit=city.best_time_to_visit,
        weather_summary=city.weather_summary,
        vibe_tags=city.vibe_tags or [],
        is_featured=city.is_featured,
        places_count=len(places),
        events_count=len(events),
        top_categories=list(categories_set),
        popular_places=popular[:6],
        upcoming_events=events_data
    )

@router.post("/", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
def create_city(
    city_in: CityCreate,
    db: Session = Depends(get_db),
    admin = Depends(require_admin_user)
):
    existing = db.query(City).filter(City.slug == city_in.slug.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="City with this slug already exists.")
    city = City(**city_in.model_dump())
    db.add(city)
    db.commit()
    db.refresh(city)
    return city
