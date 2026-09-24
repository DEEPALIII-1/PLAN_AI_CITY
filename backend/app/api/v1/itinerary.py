from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Itinerary, SearchQueryLog
from app.schemas.itinerary import (
    ItineraryRequest, ItineraryPlanResponse, ItinerarySaveRequest
)
from app.agents.planning_agent import planning_agent
from app.api.deps import get_current_user, require_current_user

router = APIRouter()

@router.post("/plan", response_model=ItineraryPlanResponse)
def generate_itinerary(
    req: ItineraryRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    Intelligent constraint-aware itinerary generation:
    Balances budget, available hours, meal intervals, and nearest-neighbor geographical routing.
    """
    try:
        plan = planning_agent.plan_itinerary(db, req)

        # Log search query
        log = SearchQueryLog(
            user_id=user.id if user else None,
            query=f"Plan {req.available_hours}h in city {req.city_id} under ₹{req.budget}",
            city_id=req.city_id,
            search_type="itinerary_planner",
            filters_applied={
                "budget": req.budget,
                "hours": req.available_hours,
                "pace": req.pace,
                "interests": req.interests
            }
        )
        db.add(log)
        db.commit()

        return plan
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/save", status_code=status.HTTP_201_CREATED)
def save_itinerary(
    save_in: ItinerarySaveRequest,
    current_user = Depends(require_current_user),
    db: Session = Depends(get_db)
):
    itinerary = Itinerary(
        user_id=current_user.id,
        city_id=save_in.city_id,
        title=save_in.title,
        total_budget=save_in.total_budget,
        estimated_cost=save_in.estimated_cost,
        duration_hours=save_in.duration_hours,
        start_location=save_in.start_location,
        interests=save_in.interests,
        pace=save_in.pace,
        group_size=save_in.group_size,
        transport_mode=save_in.transport_mode,
        itinerary_json=save_in.itinerary_json,
        ai_reasoning=save_in.ai_reasoning
    )
    db.add(itinerary)
    db.commit()
    db.refresh(itinerary)
    return {"message": "Itinerary saved successfully", "id": itinerary.id}

@router.get("/saved")
def list_saved_itineraries(
    current_user = Depends(require_current_user),
    db: Session = Depends(get_db)
):
    itineraries = db.query(Itinerary).filter(Itinerary.user_id == current_user.id).order_by(Itinerary.created_at.desc()).all()
    return [
        {
            "id": i.id,
            "title": i.title,
            "city_id": i.city_id,
            "total_budget": i.total_budget,
            "estimated_cost": i.estimated_cost,
            "duration_hours": i.duration_hours,
            "created_at": i.created_at.isoformat(),
            "stops_count": len(i.itinerary_json.get("stops", [])) if isinstance(i.itinerary_json, dict) else 0
        }
        for i in itineraries
    ]

@router.get("/{itinerary_id}")
def get_saved_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_db)
):
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return {
        "id": itinerary.id,
        "title": itinerary.title,
        "city_id": itinerary.city_id,
        "total_budget": itinerary.total_budget,
        "estimated_cost": itinerary.estimated_cost,
        "duration_hours": itinerary.duration_hours,
        "start_location": itinerary.start_location,
        "pace": itinerary.pace,
        "itinerary_data": itinerary.itinerary_json,
        "ai_reasoning": itinerary.ai_reasoning,
        "created_at": itinerary.created_at.isoformat()
    }
