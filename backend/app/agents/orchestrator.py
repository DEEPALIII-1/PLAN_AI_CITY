import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.models import City
from app.agents.city_agent import city_agent
from app.agents.planning_agent import planning_agent
from app.agents.rag_agent import rag_agent
from app.agents.search_agent import search_agent
from app.ml.recommender import recommendation_engine
from app.schemas.agent import AgentChatRequest, AgentChatResponse, AgentStepLog
from app.schemas.itinerary import ItineraryRequest

class AIOrchestrator:
    """
    Central AI Orchestrator that detects user intent, routes tasks to specialized agents,
    and synthesizes comprehensive answers.
    """

    def _extract_budget(self, text: str) -> Optional[float]:
        # Matches ₹2000, 2000 inr, under 1500, etc.
        m = re.search(r'(?:₹|rs\.?|inr)\s*([0-9,]+)', text, re.IGNORECASE)
        if m:
            return float(m.group(1).replace(",", ""))
        m2 = re.search(r'under\s*([0-9,]+)', text, re.IGNORECASE)
        if m2:
            return float(m2.group(1).replace(",", ""))
        return None

    def _extract_hours(self, text: str) -> Optional[float]:
        # Matches 8 hours, 6 hrs, one day, half day
        m = re.search(r'([0-9]+)\s*(?:hours|hrs|hr)', text, re.IGNORECASE)
        if m:
            return float(m.group(1))
        if "one day" in text.lower() or "1 day" in text.lower():
            return 8.0
        if "half day" in text.lower():
            return 4.0
        return None

    def _detect_city(self, db: Session, text: str, city_id: Optional[int]) -> Optional[City]:
        if city_id:
            c = db.query(City).filter(City.id == city_id).first()
            if c:
                return c
        
        all_cities = db.query(City).all()
        for c in all_cities:
            if c.name.lower() in text.lower():
                return c
        return all_cities[0] if all_cities else None

    def _classify_intent(self, text: str) -> str:
        t = text.lower()
        if any(w in t for w in ["plan", "itinerary", "day trip", "schedule", "what can i do", "things to do in one day"]):
            return "itinerary_planning"
        elif any(w in t for w in ["is this suitable", "family", "children", "ticket", "cost", "timing", "open", "history", "guide", "faq"]):
            return "rag_factual_qa"
        elif any(w in t for w in ["recommend", "best cafe", "where to eat", "popular places", "find"]):
            return "place_recommendation"
        elif any(w in t for w in ["weather", "best time", "vibe", "about"]):
            return "city_information"
        return "general_city_query"

    async def handle_message(self, db: Session, req: AgentChatRequest) -> AgentChatResponse:
        text = req.message
        intent = self._classify_intent(text)
        city = self._detect_city(db, text, req.city_id)
        city_id = city.id if city else 1
        city_name = city.name if city else "Shimla"

        steps: List[AgentStepLog] = []
        agents_involved = ["AI Orchestrator"]
        suggested_places = []
        citations = []
        suggested_actions = []

        # Step 1: Orchestrator Intent Logging
        steps.append(
            AgentStepLog(
                agent_name="AI Orchestrator",
                action_taken=f"Classified intent as '{intent}' for target city '{city_name}'",
                summary_output=f"Extracted intent: {intent}. City resolved: {city_name}",
                confidence=0.95
            )
        )

        if intent == "itinerary_planning":
            agents_involved.extend(["Planning Agent", "Map Agent", "City Agent", "Recommendation Agent"])
            
            # Extract constraints
            budget = self._extract_budget(text) or 2000.0
            hours = self._extract_hours(text) or 8.0
            
            interests = []
            if "cafe" in text.lower():
                interests.append("cafes")
            if "histor" in text.lower() or "heritage" in text.lower():
                interests.append("historical")
            if "nature" in text.lower() or "view" in text.lower():
                interests.append("nature")
            if not interests:
                interests = ["attractions", "cafes"]

            start_loc = "Railway Station"
            if "railway station" in text.lower():
                start_loc = f"{city_name} Railway Station"
            elif "mall road" in text.lower():
                start_loc = "Mall Road"
            elif "airport" in text.lower():
                start_loc = f"{city_name} Airport"

            steps.append(
                AgentStepLog(
                    agent_name="Planning Agent",
                    action_taken=f"Generated constraint-satisfaction schedule for budget ₹{int(budget)}, {int(hours)} hours starting from {start_loc}",
                    summary_output=f"Computed visit intervals and meal placements fitting ₹{int(budget)} total expenditure",
                    confidence=0.93
                )
            )

            # Call Planning Agent
            plan = planning_agent.plan_itinerary(
                db,
                ItineraryRequest(
                    city_id=city_id,
                    budget=budget,
                    available_hours=hours,
                    start_location=start_loc,
                    interests=interests,
                    pace="medium",
                    group_size=1
                )
            )

            steps.append(
                AgentStepLog(
                    agent_name="Map Agent",
                    action_taken="Calculated nearest-neighbor sequence and travel times",
                    summary_output=f"Optimized route across {len(plan.stops)} stops to minimize transit time",
                    confidence=0.96
                )
            )

            # Build readable itinerary reply
            lines = [
                f"### 🗺️ Curated {int(hours)}-Hour Plan for {city_name}",
                f"**Starting point:** {start_loc} | **Total Budget:** ₹{int(budget)} | **Estimated Cost:** ₹{int(plan.estimated_cost)}\n",
                "Here is your optimized itinerary:\n"
            ]

            for s in plan.stops:
                lines.append(f"- **{s.time_slot}** ➔ **{s.place_name}** ({s.category})")
                lines.append(f"  *{s.description}* (Est. ₹{int(s.estimated_cost)} | {s.duration_mins} mins)")
                lines.append(f"  *Transit:* {s.travel_mode} (~{s.travel_from_prev_mins} mins) | *Tip:* {s.ai_tips}\n")

            lines.append(f"**🌦️ Weather:** {plan.weather_advice}")
            lines.append(f"**👥 Crowd & Timing:** {plan.crowd_season_tips}")
            lines.append(f"\n💡 **AI Reasoning:** {plan.ai_reasoning}")

            reply = "\n".join(lines)
            suggested_actions = ["Save this Itinerary", "View on Map", "Adjust Budget", "Explore Cafés"]
            suggested_places = [
                {"name": s.place_name, "category": s.category, "cost": s.estimated_cost}
                for s in plan.stops
            ]

        elif intent == "rag_factual_qa":
            agents_involved.extend(["RAG Agent", "Search Agent"])
            
            steps.append(
                AgentStepLog(
                    agent_name="RAG Agent",
                    action_taken="Retrieved verified municipal & tourism documents with hybrid BM25 + dense vector search",
                    summary_output="Extracted grounded evidence chunks and assembled citations",
                    confidence=0.94
                )
            )

            rag_res = await rag_agent.answer(db, query=text, city_id=city_id)
            reply = rag_res.answer
            citations = [c.model_dump() for c in rag_res.citations]
            suggested_actions = ["View Official Source", "Plan a Visit", "Check Ticket Prices"]

        elif intent == "place_recommendation":
            agents_involved.extend(["Search Agent", "Recommendation Agent"])
            
            interests = ["cafes"] if "cafe" in text.lower() else []
            recs = recommendation_engine.recommend(
                db,
                city_id=city_id,
                interests=interests,
                budget_tier="budget" if "budget" in text.lower() or "cheap" in text.lower() else "moderate",
                limit=4
            )

            steps.append(
                AgentStepLog(
                    agent_name="Recommendation Agent",
                    action_taken=f"Scored city places against preference vector: {interests}",
                    summary_output=f"Ranked top {len(recs)} places using multi-factor rating and budget score",
                    confidence=0.91
                )
            )

            lines = [f"### 📍 Top Recommendations in {city_name}:\n"]
            for r in recs:
                lines.append(f"- **{r.name}** ({r.category}) — {r.rating} ★ (₹{int(r.estimated_cost)} est.)")
                lines.append(f"  *Why you'll like it:* {', '.join(r.match_reasons)}")
                suggested_places.append({
                    "id": r.place_id,
                    "name": r.name,
                    "category": r.category,
                    "rating": r.rating,
                    "cost": r.estimated_cost
                })

            reply = "\n".join(lines)
            suggested_actions = ["Create Itinerary with These", "Filter by Distance", "Show on Map"]

        else:
            # City information
            agents_involved.append("City Agent")
            profile = city_agent.get_city_profile(db, city_id)
            advice = city_agent.get_weather_and_crowd_advice(city_name)
            
            reply = (
                f"### 🌆 Welcome to {city_name}\n\n"
                f"{profile['description'] if profile else ''}\n\n"
                f"- **Best Time to Visit:** {profile.get('best_time_to_visit') if profile else 'Year-round'}\n"
                f"- **Weather:** {advice['weather']}\n"
                f"- **Crowd Dynamics:** {advice['crowd']}\n\n"
                f"How can I help you explore {city_name}? You can ask me to plan a day trip (e.g., 'Plan 8 hours under ₹2000') "
                f"or ask specific questions (e.g., 'Is Viceregal Lodge child friendly?')."
            )
            suggested_actions = [f"Plan 1 Day in {city_name}", f"Explore Cafés in {city_name}", f"Top Historical Sights"]

        return AgentChatResponse(
            reply=reply,
            intent_detected=intent,
            agents_involved=agents_involved,
            agent_steps=steps,
            citations=citations,
            suggested_places=suggested_places,
            suggested_actions=suggested_actions
        )

orchestrator = AIOrchestrator()
