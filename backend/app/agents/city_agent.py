from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import City, Place, Event

class CityAgent:
    """
    Expert on city characteristics, weather patterns, seasonal considerations,
    and high-level city statistics.
    """

    def get_city_profile(self, db: Session, city_id: int) -> Optional[Dict[str, Any]]:
        city = db.query(City).filter(City.id == city_id).first()
        if not city:
            return None

        places_count = db.query(Place).filter(Place.city_id == city_id).count()
        events_count = db.query(Event).filter(Event.city_id == city_id).count()

        return {
            "id": city.id,
            "name": city.name,
            "state": city.state,
            "description": city.description,
            "latitude": city.latitude,
            "longitude": city.longitude,
            "best_time_to_visit": city.best_time_to_visit,
            "weather_summary": city.weather_summary,
            "vibe_tags": city.vibe_tags or [],
            "total_places": places_count,
            "total_events": events_count
        }

    def get_weather_and_crowd_advice(self, city_name: str) -> Dict[str, str]:
        """
        Context-aware weather and crowd tips.
        """
        c = city_name.lower()
        if "shimla" in c:
            return {
                "weather": "Mild pleasant summers (15-24°C), chilly winters with occasional snowfall (0-10°C). Always carry a light jacket even in summer evenings.",
                "crowd": "Peak crowd on Mall Road & Ridge between 5:00 PM and 8:30 PM. Morning hours (8:30 AM - 11:00 AM) are best for peaceful sightseeing."
            }
        elif "delhi" in c:
            return {
                "weather": "Extremely hot in May-June (35-44°C), pleasant winters in Nov-Feb (8-22°C). Prefer indoor museums or morning monument visits during summer.",
                "crowd": "High traffic during peak rush hours (8:30-10:30 AM & 5:30-8:00 PM). Rely on Delhi Metro for predictable travel."
            }
        elif "mumbai" in c:
            return {
                "weather": "Warm and humid year-round; heavy monsoon showers from June to September. October to March is the most comfortable period.",
                "crowd": "Marine Drive and Colaba are bustling at sunset. Local trains are very crowded during rush hours; use taxis/cabs or sea-link routes."
            }
        elif "manali" in c:
            return {
                "weather": "Cool alpine weather. Snow in winter (Dec-Feb). Clear sunny skies in May-June. Check road passes before traveling to Solang/Rohtang.",
                "crowd": "High tourist influx in May-June. Start early (7:30 AM) when heading to Solang Valley or Rohtang Pass to avoid heavy vehicle bottlenecks."
            }
        else:
            return {
                "weather": "Moderate seasonal weather. Check local forecast before daily excursions.",
                "crowd": "Plan popular attraction visits during morning hours to avoid afternoon peak crowds."
            }

city_agent = CityAgent()
