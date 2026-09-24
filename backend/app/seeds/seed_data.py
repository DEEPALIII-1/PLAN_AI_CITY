import asyncio
import os
import sys
from datetime import datetime, timedelta

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from app.database.session import SessionLocal, Base, engine
from app.database.models import (
    User, UserPreference, City, Category, Place, Event, CityDocument, DocumentChunk
)
from app.core.security import get_password_hash
from app.rag.chunker import chunker
from app.rag.embedder import embedder

CITIES_DATA = [
    {
        "name": "Shimla",
        "slug": "shimla",
        "state": "Himachal Pradesh",
        "country": "India",
        "description": "The picturesque summer capital of British India, perched amid cedar and rhododendron forests, known for Victorian architecture, pedestrian Mall Road, and the Himalayan Toy Train.",
        "latitude": 31.1048,
        "longitude": 77.1734,
        "hero_image": "https://images.unsplash.com/photo-1597074866923-dc0589150358?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "March to June (Pleasant) & December to February (Snowfall)",
        "weather_summary": "Cool mountain breeze, summer 15-24°C, winter 0-10°C",
        "vibe_tags": ["Hill Station", "Colonial Heritage", "Café Culture", "Mountain Panoramas"],
        "is_featured": True
    },
    {
        "name": "Delhi",
        "slug": "delhi",
        "state": "Delhi NCR",
        "country": "India",
        "description": "India's vibrant capital, seamlessly intertwining ancient Mughal splendor, British colonial boulevards, world-class metro connectivity, and legendary street gastronomy.",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "hero_image": "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "October to March (Crisp sunny days)",
        "weather_summary": "Hot summers (38-44°C), pleasant winters (8-22°C)",
        "vibe_tags": ["Mughal Monuments", "Food Capital", "Metro Hub", "Museums"],
        "is_featured": True
    },
    {
        "name": "Mumbai",
        "slug": "mumbai",
        "state": "Maharashtra",
        "country": "India",
        "description": "The City of Dreams on the Arabian Sea coast, celebrated for Art Deco architecture, bustling bazaars, the Gateway of India, sea view promenades, and vibrant energy.",
        "latitude": 18.9220,
        "longitude": 72.8347,
        "hero_image": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "November to February",
        "weather_summary": "Warm and coastal humid, 24-32°C",
        "vibe_tags": ["Coastal Metropolis", "Art Deco", "Nightlife", "Bollywood Hub"],
        "is_featured": True
    },
    {
        "name": "Chandigarh",
        "slug": "chandigarh",
        "state": "Punjab & Haryana",
        "country": "India",
        "description": "India's premier planned city conceived by Le Corbusier, famous for manicured gardens, wide tree-lined boulevards, Rock Garden, and peaceful urban serenity.",
        "latitude": 30.7333,
        "longitude": 76.7794,
        "hero_image": "https://images.unsplash.com/photo-1605649487212-47bdab064df7?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "September to March",
        "weather_summary": "Mild winter 10-23°C, warm summer",
        "vibe_tags": ["Planned Architecture", "Gardens", "Clean City", "Lakeside"],
        "is_featured": True
    },
    {
        "name": "Manali",
        "slug": "manali",
        "state": "Himachal Pradesh",
        "country": "India",
        "description": "An alpine resort town surrounded by towering pine forests and snow-capped Himalayan peaks, gateway to Solang Valley, Rohtang Pass, and old bohemian café culture.",
        "latitude": 32.2396,
        "longitude": 77.1887,
        "hero_image": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "May to June (Summer) & Dec to Feb (Snow)",
        "weather_summary": "Alpine mountain climate, cool & refreshing",
        "vibe_tags": ["Adventure Sports", "Snow Peaks", "Apple Orchards", "Backpacker Haven"],
        "is_featured": True
    }
]

CATEGORIES_DATA = [
    {"name": "Attractions", "slug": "attractions", "icon": "Landmark", "description": "Iconic monuments, palaces, and heritage sights", "display_order": 1},
    {"name": "Cafés", "slug": "cafes", "icon": "Coffee", "description": "Cozy bakeries, specialty roasters, and scenic spots", "display_order": 2},
    {"name": "Restaurants", "slug": "restaurants", "icon": "Utensils", "description": "Authentic dining, local eateries, and fine cuisine", "display_order": 3},
    {"name": "Shopping", "slug": "shopping", "icon": "ShoppingBag", "description": "Local bazaars, crafts, and commercial high streets", "display_order": 4},
    {"name": "Nature", "slug": "nature", "icon": "Trees", "description": "Hills, viewpoints, lakes, and trekking trails", "display_order": 5},
    {"name": "Hotels", "slug": "hotels", "icon": "Building2", "description": "Heritage stays, boutique suites, and scenic resorts", "display_order": 6},
    {"name": "Events", "slug": "events", "icon": "Calendar", "description": "Cultural festivals, live music, and exhibits", "display_order": 7},
    {"name": "Transport", "slug": "transport", "icon": "Train", "description": "Railway stations, metro transit, and ropeways", "display_order": 8},
    {"name": "Important Places", "slug": "important-places", "icon": "Compass", "description": "Civic landmarks, municipal centers, and libraries", "display_order": 9},
    {"name": "Hospitals", "slug": "hospitals", "icon": "Cross", "description": "Medical centers and 24/7 emergency clinics", "display_order": 10},
]

# Rich places for Shimla and Delhi
SHIMLA_PLACES = [
    {
        "name": "The Ridge & Christ Church",
        "slug": "the-ridge-christ-church",
        "category_slug": "attractions",
        "description": "Open pedestrian cultural plaza offering panoramic views of the Pir Panjal range and housing the historic neo-Gothic Christ Church built in 1857 with stained-glass windows.",
        "address": "The Ridge, Mall Road, Shimla",
        "latitude": 31.1044,
        "longitude": 77.1751,
        "price_level": 1,
        "estimated_cost": 0.0,
        "avg_visit_duration_mins": 60,
        "opening_time": "08:00",
        "closing_time": "21:00",
        "rating": 4.8,
        "review_count": 3200,
        "tags": ["historical", "viewpoint", "colonial", "pedestrian", "free entry"],
        "images": ["https://images.unsplash.com/photo-1597074866923-dc0589150358?auto=format&fit=crop&w=800&q=75"],
        "child_friendly": True,
        "family_friendly": True,
        "is_popular": True,
        "seasonal_notes": "Vibrant during summer evenings and snowfall periods in winter."
    },
    {
        "name": "Viceregal Lodge (Rashtrapati Niwas)",
        "slug": "viceregal-lodge",
        "category_slug": "attractions",
        "description": "Magnificent Jacobethan British estate on Observatory Hill that served as residence for British Viceroys. Houses the Indian Institute of Advanced Study, surrounded by manicured botanical gardens.",
        "address": "Observatory Hill, Boileauganj, Shimla",
        "latitude": 31.1028,
        "longitude": 77.1408,
        "price_level": 2,
        "estimated_cost": 150.0,
        "avg_visit_duration_mins": 90,
        "opening_time": "10:00",
        "closing_time": "17:00",
        "rating": 4.7,
        "review_count": 2100,
        "tags": ["historical", "heritage", "museum", "botanical garden", "architecture"],
        "images": ["https://images.unsplash.com/photo-1566837945700-30057527ade0?auto=format&fit=crop&w=800&q=75"],
        "child_friendly": True,
        "family_friendly": True,
        "is_popular": True,
        "seasonal_notes": "Closed on Mondays. Guided interior tours every 30 minutes."
    },
    {
        "name": "Café Simla Times",
        "slug": "cafe-simla-times",
        "category_slug": "cafes",
        "description": "Bohemian rooftop café with vibrant hand-painted murals, wood-fired artisanal pizza, mountain sunset vista, and specialty crafted coffees.",
        "address": "Mall Road, Near Hotel Willow Banks, Shimla",
        "latitude": 31.1039,
        "longitude": 77.1728,
        "price_level": 2,
        "estimated_cost": 450.0,
        "avg_visit_duration_mins": 60,
        "opening_time": "11:00",
        "closing_time": "22:30",
        "rating": 4.6,
        "review_count": 1450,
        "tags": ["café", "rooftop", "pizza", "coffee", "sunset view"],
        "images": ["https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=800&q=75"],
        "child_friendly": True,
        "family_friendly": True,
        "is_popular": True,
        "seasonal_notes": "Outdoor seating is heated in winter months."
    },
    {
        "name": "Wake & Bake Café",
        "slug": "wake-and-bake-cafe",
        "category_slug": "cafes",
        "description": "Cozy wooden 2-storey bistro overlooking Mall Road. Famous for freshly baked French crepes, organic South Indian filter coffee, and hearty breakfast platters.",
        "address": "The Mall, Opposite Town Hall, Shimla",
        "latitude": 31.1042,
        "longitude": 77.1743,
        "price_level": 2,
        "estimated_cost": 300.0,
        "avg_visit_duration_mins": 50,
        "opening_time": "09:00",
        "closing_time": "22:00",
        "rating": 4.5,
        "review_count": 980,
        "tags": ["café", "breakfast", "crepes", "coffee", "mall road view"],
        "images": ["https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=800&q=75"],
        "child_friendly": True,
        "family_friendly": True,
        "is_popular": True,
        "seasonal_notes": "Window tables fill up fast during morning breakfast hours."
    },
    {
        "name": "Jakhoo Temple & Ropeway",
        "slug": "jakhoo-temple",
        "category_slug": "attractions",
        "description": "Ancient temple dedicated to Lord Hanuman atop Jakhoo Hill (highest peak in Shimla at 2,455m). Features a 108-foot statue and a thrilling 6-minute aerial ropeway from the Ridge.",
        "address": "Jakhoo Hill, Shimla",
        "latitude": 31.1009,
        "longitude": 77.1852,
        "price_level": 2,
        "estimated_cost": 500.0,  # includes ropeway return ticket
        "avg_visit_duration_mins": 75,
        "opening_time": "07:00",
        "closing_time": "20:00",
        "rating": 4.6,
        "review_count": 2800,
        "tags": ["temple", "ropeway", "highest peak", "nature", "viewpoint"],
        "images": ["https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=800&q=75"],
        "child_friendly": True,
        "family_friendly": True,
        "is_popular": True,
        "seasonal_notes": "Keep spectacles and loose items safe from playful resident macaques."
    },
    {
        "name": "Cecil Restaurant by Oberoi",
        "slug": "cecil-restaurant",
        "category_slug": "restaurants",
        "description": "Refined heritage fine dining in a grand colonial ballroom with chandeliers and teak floors, serving classic Himachali specialties (Madra, Chha Gosht) and continental classics.",
        "address": "Chaura Maidan, Shimla",
        "latitude": 31.1031,
        "longitude": 77.1520,
        "price_level": 4,
        "estimated_cost": 1800.0,
        "avg_visit_duration_mins": 80,
        "opening_time": "12:30",
        "closing_time": "23:00",
        "rating": 4.9,
        "review_count": 820,
        "tags": ["fine dining", "heritage", "himachali", "luxury", "romantic"],
        "images": ["https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=75"],
        "child_friendly": True,
        "family_friendly": True,
        "is_popular": False,
        "seasonal_notes": "Prior table reservation recommended for dinner."
    },
    {
        "name": "Himachali Rasoi",
        "slug": "himachali-rasoi",
        "category_slug": "restaurants",
        "description": "Authentic traditional kitchen on Mall Road dedicated to heritage recipes. Renowned for serving the authentic Himachali Kangri Dham on traditional brass plates.",
        "address": "56 Middle Bazaar, Near Mall Road, Shimla",
        "latitude": 31.1040,
        "longitude": 77.1738,
        "price_level": 1,
        "estimated_cost": 250.0,
        "avg_visit_duration_mins": 55,
        "opening_time": "12:00",
        "closing_time": "21:30",
        "rating": 4.8,
        "review_count": 2100,
        "tags": ["authentic", "himachali", "dham", "traditional food", "budget friendly"],
        "images": ["https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=800&q=75"],
        "child_friendly": True,
        "family_friendly": True,
        "is_popular": True,
        "seasonal_notes": "Very popular at lunch; try Sepu Badi and Khatta."
    },
    {
        "name": "Ashiana & Goofa",
        "slug": "ashiana-and-goofa",
        "category_slug": "restaurants",
        "description": "Circular heritage pavilion restaurant operated by HPTDC directly on The Ridge, offering sweeping valley views, north Indian fare, and Himachali trout.",
        "address": "The Ridge, Shimla",
        "latitude": 31.1046,
        "longitude": 77.1748,
        "price_level": 2,
        "estimated_cost": 380.0,
        "avg_visit_duration_mins": 60,
        "opening_time": "10:00",
        "closing_time": "22:00",
        "rating": 4.5,
        "review_count": 1300,
        "tags": ["ridge view", "indian food", "hptdc", "family dining", "scenic"],
        "images": ["https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=75"],
        "child_friendly": True,
        "family_friendly": True,
        "is_popular": True,
        "seasonal_notes": "Outdoor gazebos offer direct views of the Christ Church."
    },
    {
        "name": "Lakkar Bazaar",
        "slug": "lakkar-bazaar",
        "category_slug": "shopping",
        "description": "Famous traditional marketplace adjacent to the Ridge, renowned for wooden handcrafted souvenirs, Himachali wool shawls, walking sticks, and steaming hot Kullu siddu.",
        "address": "Lakkar Bazaar, Adjoining The Ridge, Shimla",
        "latitude": 31.1062,
        "longitude": 77.1770,
        "price_level": 1,
        "estimated_cost": 250.0,
        "avg_visit_duration_mins": 60,
        "opening_time": "10:00",
        "closing_time": "20:30",
        "rating": 4.4,
        "review_count": 1600,
        "tags": ["shopping", "handicrafts", "wooden crafts", "street food", "local market"],
        "images": ["https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=75"],
        "child_friendly": True,
        "family_friendly": True,
        "is_popular": True,
        "seasonal_notes": "Great place to sample authentic hot steamed Himachali Siddu."
    },
    {
        "name": "Kalka-Shimla Toy Train Station",
        "slug": "kalka-shimla-toy-train",
        "category_slug": "transport",
        "description": "UNESCO World Heritage narrow-gauge mountain railway terminal built in 1903, meandering across 102 tunnels and over 800 bridges through deodar pine valleys.",
        "address": "Railway Station, Cart Road, Shimla",
        "latitude": 31.1030,
        "longitude": 77.1650,
        "price_level": 1,
        "estimated_cost": 75.0,
        "avg_visit_duration_mins": 45,
        "opening_time": "06:00",
        "closing_time": "20:00",
        "rating": 4.8,
        "review_count": 4500,
        "tags": ["unesco", "heritage train", "transit", "scenic railway", "toy train"],
        "images": ["https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=800&q=75"],
        "child_friendly": True,
        "family_friendly": True,
        "is_popular": True,
        "seasonal_notes": "Advance booking via IRCTC strongly recommended."
    }
]

DELHI_PLACES = [
    {
        "name": "Qutub Minar Complex",
        "slug": "qutub-minar",
        "category_slug": "attractions",
        "description": "UNESCO World Heritage site featuring the 72.5m fluted red sandstone minaret built in 1192, the rust-resistant 4th-century iron pillar, and ancient Indo-Islamic arches.",
        "address": "Mehrauli, New Delhi",
        "latitude": 28.5245,
        "longitude": 77.1855,
        "price_level": 1,
        "estimated_cost": 50.0,
        "avg_visit_duration_mins": 75,
        "opening_time": "07:00",
        "closing_time": "18:00",
        "rating": 4.7,
        "review_count": 8900,
        "tags": ["unesco", "historical", "monument", "architecture", "garden"],
        "images": ["https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=800&q=75"],
        "child_friendly": True,
        "family_friendly": True,
        "is_popular": True,
        "seasonal_notes": "Pleasant in morning sunlight; evening illumination is stunning."
    },
    {
        "name": "Humayun's Tomb",
        "slug": "humayuns-tomb",
        "category_slug": "attractions",
        "description": "Sublime Mughal garden tomb constructed in 1570 that served as architectural blueprint for the Taj Mahal, set in geometric Persian Charbagh water gardens.",
        "address": "Mathura Road, Nizamuddin East, New Delhi",
        "latitude": 28.5933,
        "longitude": 77.2507,
        "price_level": 1,
        "estimated_cost": 50.0,
        "avg_visit_duration_mins": 75,
        "opening_time": "06:00",
        "closing_time": "18:00",
        "rating": 4.8,
        "review_count": 7600,
        "tags": ["unesco", "mughal", "heritage", "charbagh", "gardens"],
        "images": ["https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=800&q=75"],
        "child_friendly": True,
        "family_friendly": True,
        "is_popular": True,
        "seasonal_notes": "Best visited during golden hour before sunset."
    },
    {
        "name": "Café Lota",
        "slug": "cafe-lota",
        "category_slug": "cafes",
        "description": "Open-air artisanal café nestled inside the National Crafts Museum, celebrated for inventive regional Indian delicacies, filter coffee, and apple jalebi.",
        "address": "National Crafts Museum, Bhairon Marg, Pragati Maidan, New Delhi",
        "latitude": 28.6145,
        "longitude": 77.2415,
        "price_level": 2,
        "estimated_cost": 550.0,
        "avg_visit_duration_mins": 60,
        "opening_time": "08:00",
        "closing_time": "21:30",
        "rating": 4.6,
        "review_count": 3100,
        "tags": ["café", "regional food", "artisanal", "museum café", "outdoor"],
        "images": ["https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=800&q=75"],
        "child_friendly": True,
        "family_friendly": True,
        "is_popular": True,
        "seasonal_notes": "Pair with a walk through the National Crafts Museum."
    },
    {
        "name": "Karim's (Jama Masjid)",
        "slug": "karims-jama-masjid",
        "category_slug": "restaurants",
        "description": "Legendary historic Mughlai culinary institution founded in 1913 near Jama Masjid, famed for slow-cooked mutton burra kebabs, nihari, and butter naan.",
        "address": "Gali Kababian, Jama Masjid, Old Delhi",
        "latitude": 28.6508,
        "longitude": 77.2334,
        "price_level": 2,
        "estimated_cost": 400.0,
        "avg_visit_duration_mins": 50,
        "opening_time": "11:00",
        "closing_time": "23:30",
        "rating": 4.5,
        "review_count": 6200,
        "tags": ["mughlai", "old delhi", "kebabs", "historic eatery", "authentic"],
        "images": ["https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=75"],
        "child_friendly": True,
        "family_friendly": True,
        "is_popular": True,
        "seasonal_notes": "Old Delhi alleys are crowded; accessible via Chawri Bazar or Jama Masjid Metro."
    }
]

CITY_DOCUMENTS = [
    {
        "city_name": "Shimla",
        "title": "Shimla Tourism & Heritage Conservation Official Guide",
        "source_type": "official_tourism",
        "source_url": "https://himachaltourism.gov.in/shimla-guide",
        "content": """Official Tourism Guide - Shimla Municipal Corporation & Department of Tourism Himachal Pradesh.
        
1. The Mall Road & The Ridge Regulations:
The Ridge and Mall Road are strictly designated pedestrian-only zones. No motor vehicles are permitted except emergency ambulances. This ensures a pollution-free and safe walking environment for families, elders, and young children. Horse rides are available on the Ridge with government-fixed rates (₹100 for a 15-minute guided loop).

2. Viceregal Lodge (Rashtrapati Niwas) & Child Suitability:
Is Viceregal Lodge suitable for a family with children? Yes, highly suitable. The outer estate features vast manicured lawns, botanical gardens, and gentle paved pathways ideal for strollers and children to walk freely. 
Entry Tickets: The grounds/gardens ticket costs ₹50 per adult, while children under 10 enter the gardens for free. Guided internal heritage tour tickets cost ₹150 for adults and ₹75 for students and children (valid ID required). Photography is permitted on the outer lawns, but indoor photography inside the historical council room is prohibited. The facility provides clean public restrooms and a cafeteria serving snacks.

3. Jakhoo Hill & Ropeway:
Jakhoo Ropeway is a modern Swiss-engineered aerial tramway connecting the Ridge to Jakhoo Temple in 6 minutes. Round trip ticket is ₹500 for adults and ₹400 for children (3-12 years). Children under 3 travel free. Visitors with children are advised not to carry open food items or plastic bags openly, as wild rhesus macaques frequent the hilltop.

4. Budget Considerations:
A visitor can comfortably explore Shimla on ₹1,500 to ₹2,000 per day. Walking the Ridge, Christ Church, Scandal Point, and Lakkar Bazaar is completely free. Budget meals and hearty Himachali thalis range from ₹150 to ₹350. Local municipal buses connect Cart Road to Boileauganj for ₹15 to ₹25."""
    },
    {
        "city_name": "Shimla",
        "title": "Shimla Transport, Toy Train & Weather Advisory",
        "source_type": "transport",
        "source_url": "https://nr.indianrailways.gov.in/kalka-shimla",
        "content": """Kalka-Shimla UNESCO Mountain Railway & City Transit Advisory.

1. UNESCO Kalka-Shimla Toy Train:
Built in 1903, this 96-kilometer narrow-gauge marvel ascends through 102 operational tunnels. Trains like the Shivalik Deluxe Express and Himalayan Queen depart Kalka early morning. Ticket rates range from ₹70 (General Second Class) to ₹550 (Deluxe Chair Car). Tickets must be reserved via IRCTC 30 to 120 days in advance during peak summer and snow seasons.

2. Seasonal Weather & Clothing Advisory:
- Summer (April - June): Temperatures range between 15°C and 25°C. Light cottons during the day; a light jacket or cardigan is necessary after 6:00 PM as mountain breeze cools quickly.
- Monsoon (July - August): Moderate to heavy rainfall. Carry sturdy umbrellas and anti-slip walking shoes.
- Winter (December - February): Temperatures range from -2°C to 12°C. Heavy woolens, thermals, and insulated boots required. Snowfall is common in late December and January."""
    },
    {
        "city_name": "Delhi",
        "title": "Delhi Heritage & Tourism Public Handbook",
        "source_type": "official_tourism",
        "source_url": "https://delhitourism.gov.in/handbook",
        "content": """Delhi Tourism and Transportation Development Corporation Official Handbook.

1. Monuments & Accessibility:
Delhi's top monuments including Qutub Minar and Humayun's Tomb are UNESCO World Heritage sites managed by the Archaeological Survey of India (ASI). Both monuments feature ramp access for wheelchairs and strollers, manicured lawns, and clean drinking water facilities.
Ticketing: ASI online e-tickets offer a ₹5 discount. Indian citizens ₹50, SAARC visitors ₹50, Foreign nationals ₹600. Entry is free for children below 15 years with age proof.

2. Transit Recommendations:
Delhi Metro is the fastest, cleanest, and most reliable transit system. Tourist Metro smart cards provide unlimited rides for 1 day (₹200 including ₹50 refundable deposit) or 3 days (₹500). Air-conditioned coaches have dedicated ladies' coaches and elderly/differently-abled seats."""
    }
]

async def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 1. Seed Categories
        category_map = {}
        for cat in CATEGORIES_DATA:
            existing = db.query(Category).filter(Category.slug == cat["slug"]).first()
            if not existing:
                c = Category(**cat)
                db.add(c)
                db.flush()
                category_map[cat["slug"]] = c.id
            else:
                category_map[cat["slug"]] = existing.id

        # 2. Seed Cities
        city_map = {}
        for cdata in CITIES_DATA:
            existing = db.query(City).filter(City.slug == cdata["slug"]).first()
            if not existing:
                city = City(**cdata)
                db.add(city)
                db.flush()
                city_map[cdata["slug"]] = city.id
            else:
                city_map[cdata["slug"]] = existing.id

        # 3. Seed Places for Shimla
        shimla_id = city_map.get("shimla")
        if shimla_id:
            for pdata in SHIMLA_PLACES:
                cslug = pdata.pop("category_slug")
                cat_id = category_map.get(cslug, category_map.get("attractions"))
                pdata["city_id"] = shimla_id
                pdata["category_id"] = cat_id
                
                existing = db.query(Place).filter(Place.slug == pdata["slug"]).first()
                if not existing:
                    p = Place(**pdata)
                    db.add(p)

        # 4. Seed Places for Delhi
        delhi_id = city_map.get("delhi")
        if delhi_id:
            for pdata in DELHI_PLACES:
                cslug = pdata.pop("category_slug")
                cat_id = category_map.get(cslug, category_map.get("attractions"))
                pdata["city_id"] = delhi_id
                pdata["category_id"] = cat_id

                existing = db.query(Place).filter(Place.slug == pdata["slug"]).first()
                if not existing:
                    p = Place(**pdata)
                    db.add(p)

        db.commit()

        # 5. Seed City Documents & Generate Chunks + Embeddings
        print("Processing City Documents and generating RAG vector embeddings...")
        for doc_info in CITY_DOCUMENTS:
            city_slug = doc_info["city_name"].lower()
            c_id = city_map.get(city_slug)
            if not c_id:
                continue

            existing_doc = db.query(CityDocument).filter(
                CityDocument.title == doc_info["title"]
            ).first()
            if not existing_doc:
                doc = CityDocument(
                    city_id=c_id,
                    title=doc_info["title"],
                    source_type=doc_info["source_type"],
                    source_url=doc_info.get("source_url"),
                    content=doc_info["content"]
                )
                db.add(doc)
                db.flush()
                
                # Chunk document
                raw_chunks = chunker.chunk_text(
                    doc_info["content"],
                    metadata={"title": doc.title, "source": doc.source_type, "city": doc_info["city_name"]}
                )

                for chunk_item in raw_chunks:
                    # Generate dense semantic vector
                    emb = await embedder.get_embedding(chunk_item["content"])
                    chunk_obj = DocumentChunk(
                        document_id=doc.id,
                        city_id=c_id,
                        chunk_index=chunk_item["chunk_index"],
                        content=chunk_item["content"],
                        metadata_json=chunk_item["metadata"],
                        embedding_json=emb
                    )
                    db.add(chunk_obj)
        
        # 6. Seed Default Demo Users
        admin_email = "admin@planaicity.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash("Admin@PlanCity2026"),
                full_name="Plan AI City Administrator",
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.flush()
            pref = UserPreference(
                user_id=admin_user.id,
                preferred_categories=["attractions", "cafes", "heritage"],
                budget_tier="moderate",
                travel_style="heritage",
                preferred_pace="medium",
                cluster_id=1
            )
            db.add(pref)

        demo_email = "traveler@planaicity.com"
        existing_demo = db.query(User).filter(User.email == demo_email).first()
        if not existing_demo:
            demo_user = User(
                email=demo_email,
                hashed_password=get_password_hash("Traveler2026!"),
                full_name="Aarav Sharma",
                role="user",
                is_active=True
            )
            db.add(demo_user)
            db.flush()
            pref = UserPreference(
                user_id=demo_user.id,
                preferred_categories=["cafes", "historical", "nature"],
                budget_tier="budget",
                travel_style="backpacker",
                preferred_pace="medium",
                cluster_id=0
            )
            db.add(pref)

        db.commit()
        print("Database seeded successfully with cities, places, RAG documents, and demo users!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
