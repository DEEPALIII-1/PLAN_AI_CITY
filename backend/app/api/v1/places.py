from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database.session import get_db
from app.database.models import Place, Category, City
from app.schemas.place import PlaceResponse, CategoryResponse, PlaceCreate
from app.agents.map_agent import map_agent
from app.api.deps import require_admin_user

router = APIRouter()

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.display_order).all()

@router.get("/", response_model=List[PlaceResponse])
def list_places(
    city_id: Optional[int] = Query(None),
    category_slug: Optional[str] = Query(None),
    max_price: Optional[float] = Query(None),
    child_friendly: Optional[bool] = Query(None),
    is_popular: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    q = db.query(Place, Category, City).join(
        Category, Place.category_id == Category.id
    ).join(
        City, Place.city_id == City.id
    )

    if city_id:
        q = q.filter(Place.city_id == city_id)
    if category_slug:
        q = q.filter(Category.slug == category_slug)
    if max_price is not None:
        q = q.filter(Place.estimated_cost <= max_price)
    if child_friendly is not None:
        q = q.filter(Place.child_friendly == child_friendly)
    if is_popular is not None:
        q = q.filter(Place.is_popular == is_popular)
    if search:
        pattern = f"%{search}%"
        q = q.filter(or_(
            Place.name.ilike(pattern),
            Place.description.ilike(pattern),
            Place.address.ilike(pattern)
        ))

    results = q.limit(limit).all()
    out = []
    for p, cat, c in results:
        res = PlaceResponse(
            id=p.id,
            city_id=p.city_id,
            category_id=p.category_id,
            name=p.name,
            slug=p.slug,
            description=p.description,
            address=p.address,
            latitude=p.latitude,
            longitude=p.longitude,
            price_level=p.price_level,
            estimated_cost=p.estimated_cost,
            avg_visit_duration_mins=p.avg_visit_duration_mins,
            opening_time=p.opening_time,
            closing_time=p.closing_time,
            rating=p.rating,
            review_count=p.review_count,
            tags=p.tags or [],
            images=p.images or [],
            child_friendly=p.child_friendly,
            family_friendly=p.family_friendly,
            accessibility=p.accessibility,
            is_popular=p.is_popular,
            seasonal_notes=p.seasonal_notes,
            category_name=cat.name,
            city_name=c.name
        )
        out.append(res)
    return out

@router.get("/nearby", response_model=List[PlaceResponse])
def get_nearby_places(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_km: float = Query(5.0),
    city_id: Optional[int] = Query(None),
    limit: int = Query(10),
    db: Session = Depends(get_db)
):
    q = db.query(Place, Category, City).join(
        Category, Place.category_id == Category.id
    ).join(
        City, Place.city_id == City.id
    )
    if city_id:
        q = q.filter(Place.city_id == city_id)

    candidates = q.all()
    scored = []

    for p, cat, c in candidates:
        dist = map_agent.haversine_km(lat, lng, p.latitude, p.longitude)
        if dist <= radius_km:
            res = PlaceResponse(
                id=p.id,
                city_id=p.city_id,
                category_id=p.category_id,
                name=p.name,
                slug=p.slug,
                description=p.description,
                address=p.address,
                latitude=p.latitude,
                longitude=p.longitude,
                price_level=p.price_level,
                estimated_cost=p.estimated_cost,
                avg_visit_duration_mins=p.avg_visit_duration_mins,
                opening_time=p.opening_time,
                closing_time=p.closing_time,
                rating=p.rating,
                review_count=p.review_count,
                tags=p.tags or [],
                images=p.images or [],
                child_friendly=p.child_friendly,
                family_friendly=p.family_friendly,
                accessibility=p.accessibility,
                is_popular=p.is_popular,
                seasonal_notes=p.seasonal_notes,
                category_name=cat.name,
                city_name=c.name,
                distance_km=round(dist, 2)
            )
            scored.append((dist, res))

    scored.sort(key=lambda x: x[0])
    return [item[1] for item in scored[:limit]]

@router.get("/{place_id}", response_model=PlaceResponse)
def get_place(place_id: int, db: Session = Depends(get_db)):
    res = db.query(Place, Category, City).join(
        Category, Place.category_id == Category.id
    ).join(
        City, Place.city_id == City.id
    ).filter(Place.id == place_id).first()

    if not res:
        raise HTTPException(status_code=404, detail="Place not found")

    p, cat, c = res
    return PlaceResponse(
        id=p.id,
        city_id=p.city_id,
        category_id=p.category_id,
        name=p.name,
        slug=p.slug,
        description=p.description,
        address=p.address,
        latitude=p.latitude,
        longitude=p.longitude,
        price_level=p.price_level,
        estimated_cost=p.estimated_cost,
        avg_visit_duration_mins=p.avg_visit_duration_mins,
        opening_time=p.opening_time,
        closing_time=p.closing_time,
        rating=p.rating,
        review_count=p.review_count,
        tags=p.tags or [],
        images=p.images or [],
        child_friendly=p.child_friendly,
        family_friendly=p.family_friendly,
        accessibility=p.accessibility,
        is_popular=p.is_popular,
        seasonal_notes=p.seasonal_notes,
        category_name=cat.name,
        city_name=c.name
    )

@router.post("/", response_model=PlaceResponse, status_code=status.HTTP_201_CREATED)
async def create_place(place_in: PlaceCreate, db: Session = Depends(get_db)):
    import re
    import time
    city = db.query(City).filter(City.id == place_in.city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    cat = db.query(Category).filter(Category.id == place_in.category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    # Generate unique slug
    base_slug = re.sub(r'[^a-zA-Z0-9]+', '-', place_in.name.lower()).strip('-')
    unique_slug = f"{base_slug}-{int(time.time())}"

    # Lat/Lng fallback to city center if omitted
    lat = place_in.latitude if place_in.latitude is not None else city.latitude
    lng = place_in.longitude if place_in.longitude is not None else city.longitude

    place = Place(
        city_id=place_in.city_id,
        category_id=place_in.category_id,
        name=place_in.name,
        slug=unique_slug,
        description=place_in.description,
        address=place_in.address,
        latitude=lat,
        longitude=lng,
        price_level=place_in.price_level,
        estimated_cost=place_in.estimated_cost,
        avg_visit_duration_mins=place_in.avg_visit_duration_mins,
        opening_time=place_in.opening_time,
        closing_time=place_in.closing_time,
        rating=place_in.rating,
        review_count=place_in.review_count,
        tags=place_in.tags or [],
        images=place_in.images if place_in.images else [
            "https://images.unsplash.com/photo-1597074866923-dc0589150358?auto=format&fit=crop&w=600&q=70"
        ],
        child_friendly=place_in.child_friendly,
        family_friendly=place_in.family_friendly,
        accessibility=place_in.accessibility,
        is_popular=place_in.is_popular,
        seasonal_notes=place_in.seasonal_notes
    )
    db.add(place)
    db.commit()
    db.refresh(place)

    return PlaceResponse(
        id=place.id,
        city_id=place.city_id,
        category_id=place.category_id,
        name=place.name,
        slug=place.slug,
        description=place.description,
        address=place.address,
        latitude=place.latitude,
        longitude=place.longitude,
        price_level=place.price_level,
        estimated_cost=place.estimated_cost,
        avg_visit_duration_mins=place.avg_visit_duration_mins,
        opening_time=place.opening_time,
        closing_time=place.closing_time,
        rating=place.rating,
        review_count=place.review_count,
        tags=place.tags or [],
        images=place.images or [],
        child_friendly=place.child_friendly,
        family_friendly=place.family_friendly,
        accessibility=place.accessibility,
        is_popular=place.is_popular,
        seasonal_notes=place.seasonal_notes,
        category_name=cat.name,
        city_name=city.name
    )
