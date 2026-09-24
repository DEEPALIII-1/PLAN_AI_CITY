import sys
import os

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.abspath("backend"))

from fastapi.testclient import TestClient
from app.main import app

def test_backend():
    client = TestClient(app)

    print("--- 1. Testing Health Check ---")
    r = client.get("/health")
    assert r.status_code == 200
    print("Health Status:", r.json())

    print("\n--- 2. Testing Cities Endpoint ---")
    r = client.get("/api/v1/cities/")
    assert r.status_code == 200
    cities = r.json()
    print("Available Cities:", [c["name"] for c in cities])

    print("\n--- 3. Testing RAG QA with Verified Citations ---")
    rag_query = {
        "query": "Is Viceregal Lodge suitable for a family with children?",
        "city_id": 1
    }
    r = client.post("/api/v1/rag/query", json=rag_query)
    assert r.status_code == 200
    rag_data = r.json()
    print("RAG Confidence Score:", rag_data["confidence_score"])
    print("RAG Grounded Answer:\n", rag_data["answer"])
    print("Verified Sources Cited:")
    for cit in rag_data["citations"]:
        print(f"  [✓] {cit['title']} ({cit['source_type']}) - Score: {cit['relevance_score']}")

    print("\n--- 4. Testing Constraint-Aware Itinerary Planner ---")
    itin_req = {
        "city_id": 1,
        "budget": 2000.0,
        "available_hours": 8.0,
        "start_time": "09:00",
        "start_location": "Shimla Railway Station",
        "interests": ["cafes", "historical"],
        "pace": "medium"
    }
    r = client.post("/api/v1/itinerary/plan", json=itin_req)
    assert r.status_code == 200
    itin = r.json()
    print("Generated Itinerary:", itin["title"])
    print(f"Budget: ₹{itin['total_budget']} | Estimated Cost: ₹{itin['estimated_cost']}")
    print("Budget Breakdown:", itin["budget_breakdown"])
    print("Schedule:")
    for s in itin["stops"]:
        print(f"  • {s['time_slot']} -> {s['place_name']} ({s['category']}) | Cost: ₹{s['estimated_cost']} | Transit: {s['travel_mode']} (~{s['travel_from_prev_mins']} min)")

    print("\n--- 5. Testing Multi-Agent Orchestrator ---")
    chat_req = {
        "message": "What can I do in Shimla in one day under ₹1500?"
    }
    r = client.post("/api/v1/agents/chat", json=chat_req)
    assert r.status_code == 200
    chat = r.json()
    print("Intent Detected:", chat["intent_detected"])
    print("Agents Involved:", chat["agents_involved"])
    print("Agent Execution Steps:")
    for step in chat["agent_steps"]:
        print(f"  [{step['agent_name']}] {step['action_taken']}")
    print("\nSample Agent Reply Preview:\n", chat["reply"][:250] + "...")

    print("\n--- 6. Testing ML Recommendations ---")
    rec_req = {
        "city_id": 1,
        "interests": ["cafes"],
        "budget_tier": "budget",
        "limit": 3
    }
    r = client.post("/api/v1/recommendations/", json=rec_req)
    assert r.status_code == 200
    recs = r.json()
    print("ML Persona Applied:", recs["user_persona_applied"])
    for item in recs["recommendations"]:
        print(f"  ★ {item['name']} ({item['category']}) - Match Score: {item['match_score']} | Reasons: {item['match_reasons']}")

    print("\n--- 7. Testing City Intelligence Analytics ---")
    r = client.get("/api/v1/analytics/city/1")
    assert r.status_code == 200
    analytics = r.json()
    print("City:", analytics["city_name"])
    print("Total Places:", analytics["total_places"])
    print("Category Breakdown:", [(c["category"], c["count"]) for c in analytics["category_distribution"]])
    print("K-Means Personas Identified:", [p["persona_name"] for p in analytics["user_persona_clusters"]])

    print("\n==========================================")
    print("ALL 7 CORE PLATFORM TESTS PASSED SUCCESSFULLY!")
    print("==========================================")

if __name__ == "__main__":
    test_backend()
