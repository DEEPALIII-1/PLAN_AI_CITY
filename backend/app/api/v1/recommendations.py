from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import City, User
from app.schemas.recommendations import RecommendationRequest, RecommendationResponse
from app.ml.recommender import recommendation_engine
from app.ml.clustering import user_clusterer
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=RecommendationResponse)
def get_recommendations(
    req: RecommendationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    city = db.query(City).filter(City.id == req.city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    interests = req.interests
    budget_tier = req.budget_tier or "moderate"

    # Inherit from user preference profile if available and not explicitly overridden
    if user and user.preference:
        if not interests and user.preference.preferred_categories:
            interests = user.preference.preferred_categories
        if not req.budget_tier and user.preference.budget_tier:
            budget_tier = user.preference.budget_tier

    persona = user_clusterer.predict_persona(
        budget_tier=budget_tier,
        interests=interests
    )

    items = recommendation_engine.recommend(
        db=db,
        city_id=req.city_id,
        interests=interests,
        budget_tier=budget_tier,
        max_price=req.max_price,
        lat=req.lat,
        lng=req.lng,
        limit=req.limit
    )

    return RecommendationResponse(
        city_name=city.name,
        user_persona_applied=persona["persona_name"],
        recommendations=items
    )
