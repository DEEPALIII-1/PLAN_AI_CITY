import sys
import os
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from app.database.session import SessionLocal
from app.database.models import User, UserProfile, UserPreference, City, Place

client = TestClient(app)

def test_1_pan_india_cities():
    """Verify Pan-India cities and village coverage"""
    res = client.get("/api/v1/cities/")
    assert res.status_code == 200
    cities = res.json()
    assert len(cities) >= 10
    names = [c["name"] for c in cities]
    print(f"Verified {len(cities)} cities in database: {names}")
    
    # Check that major Indian destinations & villages exist
    assert any(c["name"] == "Jaipur" for c in cities)
    assert any(c["name"] == "Varanasi" for c in cities)
    assert any(c["name"] == "Chitkul" for c in cities)
    assert any(c["name"] == "Mawlynnong" for c in cities)

def test_2_pan_india_search_and_resolve():
    """Verify searching localities and resolving villages"""
    # 1. Search for Mawlynnong (cleanest village)
    res = client.get("/api/v1/cities/search?q=Mawlynnong")
    assert res.status_code == 200
    matches = res.json()
    assert len(matches) > 0
    assert "Mawlynnong" in [m["name"] for m in matches]

    # 2. Search for Varanasi
    res2 = client.get("/api/v1/cities/search?q=Varanasi")
    assert res2.status_code == 200
    assert any("Varanasi" in m["name"] for m in res2.json())

def test_3_user_registration_and_profiles_table():
    """Verify registering a new user and storing profile info in dedicated user_profiles table"""
    db = SessionLocal()
    test_email = "deepali_prajapati_test@gmail.com"
    
    # Clean up if already exists
    existing = db.query(User).filter(User.email == test_email).first()
    if existing:
        db.query(UserProfile).filter(UserProfile.user_id == existing.id).delete()
        db.query(UserPreference).filter(UserPreference.user_id == existing.id).delete()
        db.delete(existing)
        db.commit()

    # Register new user
    reg_payload = {
        "email": test_email,
        "password": "SecurePassword123!",
        "full_name": "Deepali Prajapati",
        "phone_number": "+91 98765 43210",
        "home_city": "Lucknow",
        "home_state": "Uttar Pradesh"
    }
    res = client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["email"] == test_email
    token = data["access_token"]

    # Verify dedicated user_profiles table has the stored profile row
    created_user = db.query(User).filter(User.email == test_email).first()
    assert created_user is not None
    assert created_user.profile is not None
    assert created_user.profile.full_name == "Deepali Prajapati"
    assert created_user.profile.phone_number == "+91 98765 43210"
    assert created_user.profile.home_city == "Lucknow"
    assert created_user.profile.home_state == "Uttar Pradesh"
    assert created_user.profile.country == "India"
    assert created_user.profile.account_status == "active"
    print("Dedicated user_profiles row verified successfully:", created_user.profile.full_name, created_user.profile.home_city)

    # Test Login with new user
    login_res = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # Test /me endpoint
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == test_email
    assert me_data["profile"]["home_city"] == "Lucknow"
    assert me_data["profile"]["phone_number"] == "+91 98765 43210"

    # Clean up
    db.query(UserProfile).filter(UserProfile.user_id == created_user.id).delete()
    db.query(UserPreference).filter(UserPreference.user_id == created_user.id).delete()
    db.delete(created_user)
    db.commit()
    db.close()
    print("User registration, login, and dedicated user_profiles table verification passed 100%!")

def test_4_itinerary_generation():
    """Verify constraint-aware itinerary generation for Jaipur"""
    db = SessionLocal()
    jaipur = db.query(City).filter(City.slug == "jaipur").first()
    db.close()
    assert jaipur is not None

    payload = {
        "city_id": jaipur.id,
        "budget": 2000,
        "available_hours": 8,
        "interests": ["attractions", "cafes"],
        "pace": "medium",
        "group_size": 1,
        "transport_mode": "walk_cab"
    }
    res = client.post("/api/v1/itinerary/plan", json=payload)
    assert res.status_code == 200
    itinerary = res.json()
    assert len(itinerary["stops"]) > 0
    assert itinerary["estimated_cost"] > 0
    print(f"Generated {len(itinerary['stops'])} stops in Jaipur with estimated cost INR {itinerary['estimated_cost']}!")

if __name__ == "__main__":
    test_1_pan_india_cities()
    test_2_pan_india_search_and_resolve()
    test_3_user_registration_and_profiles_table()
    test_4_itinerary_generation()
    print("\nALL 4 INTEGRATION TESTS PASSED SUCCESSFULLY!")
