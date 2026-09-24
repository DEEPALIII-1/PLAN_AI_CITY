import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import User, UserPreference, UserProfile
from app.core.security import verify_password, get_password_hash, create_access_token
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse, UserProfileUpdate
from app.api.deps import require_current_user
from app.ml.clustering import user_clusterer

router = APIRouter()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    clean_email = user_in.email.lower().strip()
    existing = db.query(User).filter(User.email == clean_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists. Please sign in instead."
        )

    # 1. Create Core User Account
    user = User(
        email=clean_email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role="user"
    )
    db.add(user)
    db.flush()

    # 2. Store Extended User Information in Dedicated user_profiles Table
    user_profile = UserProfile(
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone_number=user_in.phone_number,
        home_city=user_in.home_city or "India",
        home_state=user_in.home_state,
        country="India",
        account_status="active",
        total_itineraries_created=0,
        total_places_explored=0,
        last_login_at=datetime.datetime.utcnow(),
        created_at=datetime.datetime.utcnow()
    )
    db.add(user_profile)

    # 3. Initial persona cluster prediction & preferences
    persona = user_clusterer.predict_persona(budget_tier="moderate", pace="medium", interests=[])
    
    pref = UserPreference(
        user_id=user.id,
        preferred_categories=[],
        budget_tier="moderate",
        travel_style="solo",
        preferred_pace="medium",
        cluster_id=persona["cluster_id"]
    )
    db.add(pref)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.id, role=user.role)
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=user.role,
        full_name=user.full_name,
        home_city=user_profile.home_city,
        home_state=user_profile.home_state
    )

@router.post("/login", response_model=Token)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    clean_email = login_in.email.lower().strip()
    user = db.query(User).filter(User.email == clean_email).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password. Please verify your credentials or register a new account."
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is deactivated")

    # Update last_login_at in dedicated user_profiles table
    if not user.profile:
        user_prof = UserProfile(
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
            home_city="India",
            account_status="active",
            last_login_at=datetime.datetime.utcnow()
        )
        db.add(user_prof)
    else:
        user.profile.last_login_at = datetime.datetime.utcnow()
    
    db.commit()

    token = create_access_token(subject=user.id, role=user.role)
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=user.role,
        full_name=user.full_name,
        home_city=user.profile.home_city if user.profile else None,
        home_state=user.profile.home_state if user.profile else None
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    # Ensure profile row exists in user_profiles table
    if not current_user.profile:
        user_prof = UserProfile(
            user_id=current_user.id,
            full_name=current_user.full_name,
            email=current_user.email,
            home_city="India",
            account_status="active",
            last_login_at=datetime.datetime.utcnow()
        )
        db.add(user_prof)
        db.commit()
        db.refresh(current_user)

    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_in: UserProfileUpdate,
    current_user: User = Depends(require_current_user),
    db: Session = Depends(get_db)
):
    if profile_in.full_name is not None:
        current_user.full_name = profile_in.full_name

    # Manage dedicated user_profiles table entry
    if not current_user.profile:
        current_user.profile = UserProfile(
            user_id=current_user.id,
            full_name=current_user.full_name,
            email=current_user.email,
            home_city=profile_in.home_city or "India",
            home_state=profile_in.home_state,
            phone_number=profile_in.phone_number,
            bio=profile_in.bio
        )
        db.add(current_user.profile)
    else:
        if profile_in.full_name is not None:
            current_user.profile.full_name = profile_in.full_name
        if profile_in.phone_number is not None:
            current_user.profile.phone_number = profile_in.phone_number
        if profile_in.home_city is not None:
            current_user.profile.home_city = profile_in.home_city
        if profile_in.home_state is not None:
            current_user.profile.home_state = profile_in.home_state
        if profile_in.bio is not None:
            current_user.profile.bio = profile_in.bio

    # Manage user preferences
    pref = current_user.preference
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)

    if profile_in.preferred_categories is not None:
        pref.preferred_categories = profile_in.preferred_categories
    if profile_in.budget_tier is not None:
        pref.budget_tier = profile_in.budget_tier
    if profile_in.travel_style is not None:
        pref.travel_style = profile_in.travel_style
    if profile_in.preferred_pace is not None:
        pref.preferred_pace = profile_in.preferred_pace
    if profile_in.favorite_place_ids is not None:
        pref.favorite_place_ids = profile_in.favorite_place_ids

    # Re-evaluate K-Means persona cluster
    persona = user_clusterer.predict_persona(
        budget_tier=pref.budget_tier or "moderate",
        pace=pref.preferred_pace or "medium",
        interests=pref.preferred_categories or []
    )
    pref.cluster_id = persona["cluster_id"]

    db.commit()
    db.refresh(current_user)
    return current_user
