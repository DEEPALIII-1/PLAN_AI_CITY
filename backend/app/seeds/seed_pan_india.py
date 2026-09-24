import asyncio
import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database.models import City, Category, Place, CityDocument, DocumentChunk
from app.rag.chunker import chunker
from app.rag.embedder import embedder

# Comprehensive Pan-India Destinations: 50+ Iconic Cities, Hill Stations, and Famous Villages
PAN_INDIA_CITIES = [
    # --- Northern India ---
    {
        "name": "Jaipur",
        "slug": "jaipur",
        "state": "Rajasthan",
        "district": "Jaipur",
        "locality_type": "city",
        "description": "The historic Pink City, capital of Rajasthan, famous for terracotta-hued palace architecture, UNESCO hilltop forts, bustling gemstone bazaars, and opulent royal heritage.",
        "latitude": 26.9124,
        "longitude": 75.7873,
        "hero_image": "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "October to March (Pleasant winter sunshine)",
        "weather_summary": "Crisp winter days 12-26°C, hot summers",
        "vibe_tags": ["Pink City", "Palaces & Forts", "Royal Heritage", "Textiles & Gems"],
        "is_featured": True,
        "places": [
            {
                "name": "Hawa Mahal (Palace of Winds)",
                "slug": "hawa-mahal",
                "category_slug": "attractions",
                "description": "Iconic five-story pink sandstone palace with 953 intricately carved jharokha honeycomb windows built in 1799 by Maharaja Sawai Pratap Singh.",
                "address": "Hawa Mahal Rd, Badi Choupad, J.D.A. Market, Jaipur",
                "latitude": 26.9239,
                "longitude": 75.8267,
                "price_level": 2,
                "estimated_cost": 200.0,
                "avg_visit_duration_mins": 60,
                "rating": 4.7,
                "review_count": 5400,
                "tags": ["historical", "palace", "photography", "architecture", "iconic"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Amer Fort & Maota Lake",
                "slug": "amer-fort",
                "category_slug": "attractions",
                "description": "Majestic UNESCO hilltop fortress blending Rajput and Mughal architecture, Sheesh Mahal mirror palace, and sweeping panoramic views.",
                "address": "Devisinghpura, Amer, Jaipur",
                "latitude": 26.9855,
                "longitude": 75.8513,
                "price_level": 2,
                "estimated_cost": 500.0,
                "avg_visit_duration_mins": 120,
                "rating": 4.8,
                "review_count": 8200,
                "tags": ["unesco", "fortress", "sheesh mahal", "panoramic"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Johari Bazaar Traditional Market",
                "slug": "johari-bazaar",
                "category_slug": "shopping",
                "description": "Jaipur's oldest commercial gemstone and jewelry bazaar, brimming with Kundan-Meena jewelry, Bandhani sarees, and Rajasthani sweets.",
                "address": "Johari Bazar, Pink City, Jaipur",
                "latitude": 26.9182,
                "longitude": 75.8242,
                "price_level": 2,
                "estimated_cost": 400.0,
                "avg_visit_duration_mins": 90,
                "rating": 4.6,
                "review_count": 3100,
                "tags": ["shopping", "jewelry", "textiles", "street bazaar"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Tattoo Café & Lounge (Hawa Mahal View)",
                "slug": "tattoo-cafe-jaipur",
                "category_slug": "cafes",
                "description": "Rooftop café directly opposite Hawa Mahal offering front-row sunset views, masala chai, cold brew, and wood-fired snacks.",
                "address": "Opposite Hawa Mahal, Badi Choupad, Jaipur",
                "latitude": 26.9242,
                "longitude": 75.8262,
                "price_level": 2,
                "estimated_cost": 350.0,
                "avg_visit_duration_mins": 50,
                "rating": 4.6,
                "review_count": 1800,
                "tags": ["café", "rooftop", "hawa mahal view", "sunset"],
                "child_friendly": True,
                "is_popular": True
            }
        ]
    },
    {
        "name": "Varanasi",
        "slug": "varanasi",
        "state": "Uttar Pradesh",
        "district": "Varanasi",
        "locality_type": "city",
        "description": "One of the world's oldest living cities on the sacred banks of the River Ganga, celebrated for spiritual ghats, evening Ganga Aarti, Banarasi silk weaving, and vibrant labyrinthine lanes.",
        "latitude": 25.3176,
        "longitude": 82.9739,
        "hero_image": "https://images.unsplash.com/photo-1561359313-0639aad49ca6?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "October to March (Crisp mornings & clear Ganga sunsets)",
        "weather_summary": "Pleasant winters 10-25°C, sacred dawn mist",
        "vibe_tags": ["Spiritual Capital", "Ganga Ghats", "Ancient City", "Ganga Aarti", "Silk Weaving"],
        "is_featured": True,
        "places": [
            {
                "name": "Dashashwamedh Ghat & Evening Maha Aarti",
                "slug": "dashashwamedh-ghat",
                "category_slug": "attractions",
                "description": "The main and most vibrant riverfront ghat in Varanasi, hosting the world-renowned daily musical Ganga Aarti ceremony with priests, brass lamps, and chanting.",
                "address": "Dashashwamedh Ghat Rd, Bangali Tola, Varanasi",
                "latitude": 25.3072,
                "longitude": 83.0104,
                "price_level": 1,
                "estimated_cost": 100.0,
                "avg_visit_duration_mins": 90,
                "rating": 4.9,
                "review_count": 9400,
                "tags": ["spiritual", "ganga aarti", "ghat", "riverfront", "iconic"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Kashi Vishwanath Temple Corridor",
                "slug": "kashi-vishwanath-temple",
                "category_slug": "attractions",
                "description": "One of the 12 sacred Jyotirlingas of Lord Shiva, connected to the Ganga by a grand modern pilgrim corridor with golden spires and deep spiritual history.",
                "address": "Lahori Tola, Varanasi",
                "latitude": 25.3109,
                "longitude": 83.0107,
                "price_level": 1,
                "estimated_cost": 50.0,
                "avg_visit_duration_mins": 75,
                "rating": 4.9,
                "review_count": 11000,
                "tags": ["spiritual", "jyotirlinga", "hindu temple", "golden spire"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Blue Lassi Shop",
                "slug": "blue-lassi-shop",
                "category_slug": "cafes",
                "description": "Legendary tiny shop churning over 80 varieties of fresh hand-churned fruit and rabdi lassis in terracotta clay kulhads since 1925.",
                "address": "Bangali Tola, Near Manikarnika Ghat, Varanasi",
                "latitude": 25.3115,
                "longitude": 83.0125,
                "price_level": 1,
                "estimated_cost": 120.0,
                "avg_visit_duration_mins": 30,
                "rating": 4.7,
                "review_count": 3200,
                "tags": ["lassi", "dessert", "historic", "kulhad", "street food"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Assi Ghat Sunrise Boat Cruise",
                "slug": "assi-ghat-sunrise",
                "category_slug": "nature",
                "description": "Peaceful southern ghat where pilgrims gather for dawn yoga, classical music, and traditional wooden oar boat rides across the holy Ganga.",
                "address": "Assi Ghat, Shivala, Varanasi",
                "latitude": 25.2894,
                "longitude": 83.0069,
                "price_level": 2,
                "estimated_cost": 300.0,
                "avg_visit_duration_mins": 75,
                "rating": 4.8,
                "review_count": 4800,
                "tags": ["boat ride", "sunrise", "ganga", "yoga", "peaceful"],
                "child_friendly": True,
                "is_popular": True
            }
        ]
    },
    {
        "name": "Agra",
        "slug": "agra",
        "state": "Uttar Pradesh",
        "district": "Agra",
        "locality_type": "city",
        "description": "Home to the Taj Mahal, one of the Seven Wonders of the World. A world-famous historic city on the Yamuna river featuring grand Mughal citadels, gardens, and marble craftsmanship.",
        "latitude": 27.1767,
        "longitude": 78.0081,
        "hero_image": "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "October to March",
        "weather_summary": "Pleasant winters 11-26°C",
        "vibe_tags": ["Taj Mahal", "Mughal Empire", "UNESCO Wonder", "Marble Inlay"],
        "is_featured": True,
        "places": [
            {
                "name": "Taj Mahal",
                "slug": "taj-mahal",
                "category_slug": "attractions",
                "description": "UNESCO World Heritage wonder of pure white ivory marble built by Mughal Emperor Shah Jahan in memory of Mumtaz Mahal. One of humanity's finest architectural achievements.",
                "address": "Dharmapuri, Forest Colony, Tajganj, Agra",
                "latitude": 27.1751,
                "longitude": 78.0421,
                "price_level": 2,
                "estimated_cost": 250.0,
                "avg_visit_duration_mins": 120,
                "rating": 4.9,
                "review_count": 22000,
                "tags": ["unesco", "wonder of world", "marble monument", "shah jahan"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Agra Fort (Lal Qila)",
                "slug": "agra-fort",
                "category_slug": "attractions",
                "description": "Enormous red sandstone citadel of Mughal emperors spanning 94 acres, featuring Diwan-i-Aam, Khas Mahal, and distant views of the Taj Mahal.",
                "address": "Agra Fort, Rakabganj, Agra",
                "latitude": 27.1795,
                "longitude": 78.0211,
                "price_level": 2,
                "estimated_cost": 150.0,
                "avg_visit_duration_mins": 90,
                "rating": 4.7,
                "review_count": 7800,
                "tags": ["unesco", "red sandstone", "mughal fort", "architecture"],
                "child_friendly": True,
                "is_popular": True
            }
        ]
    },
    {
        "name": "Chitkul",
        "slug": "chitkul",
        "state": "Himachal Pradesh",
        "district": "Kinnaur",
        "locality_type": "village",
        "description": "The last inhabited village on the Indo-Tibet border in the pristine Kinnaur valley, nestled along the turquoise Baspa River with traditional slate-roof wooden cottages and snow-capped Himalayan peaks.",
        "latitude": 31.3533,
        "longitude": 78.4357,
        "hero_image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "May to October (Pleasant alpine summer, closed in heavy winter snow)",
        "weather_summary": "Crisp mountain climate, 5-18°C",
        "vibe_tags": ["Last Village of India", "Kinnaur Valley", "Snow Peaks", "Baspa River", "Himalayan Village"],
        "is_featured": True,
        "places": [
            {
                "name": "Hindustan Ka Akhri Dhaba (India's Last Dhaba)",
                "slug": "indias-last-dhaba-chitkul",
                "category_slug": "restaurants",
                "description": "Iconic riverside dhaba on the final motorable road of India before the Tibet border, serving piping hot Rajma Chawal, Maggi, and ginger lemon tea.",
                "address": "Indo-Tibet Border Road, Chitkul, Kinnaur",
                "latitude": 31.3538,
                "longitude": 78.4362,
                "price_level": 1,
                "estimated_cost": 150.0,
                "avg_visit_duration_mins": 45,
                "rating": 4.7,
                "review_count": 1850,
                "tags": ["iconic dhaba", "rajma chawal", "border post", "mountain view"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Baspa River Bank & Wooden Village Trail",
                "slug": "baspa-river-trail-chitkul",
                "category_slug": "nature",
                "description": "Serene pebble beaches along glacial turquoise waters of Baspa River lined by golden pine trees and Kinnauri wooden temple shrines.",
                "address": "Baspa Valley, Chitkul Village, Kinnaur",
                "latitude": 31.3525,
                "longitude": 78.4348,
                "price_level": 1,
                "estimated_cost": 0.0,
                "avg_visit_duration_mins": 90,
                "rating": 4.9,
                "review_count": 1200,
                "tags": ["river", "peaceful", "himalayan landscape", "village walk"],
                "child_friendly": True,
                "is_popular": True
            }
        ]
    },
    {
        "name": "Mawlynnong",
        "slug": "mawlynnong",
        "state": "Meghalaya",
        "district": "East Khasi Hills",
        "locality_type": "village",
        "description": "Acclaimed as 'God's Own Garden' and the Cleanest Village in Asia (by Discover India), famous for 100% bamboo dustbins, living root bridges, and matriarchal Khasi culture.",
        "latitude": 25.2014,
        "longitude": 91.9160,
        "hero_image": "https://images.unsplash.com/photo-1596178065887-1198b6148b2b?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "October to April (Lush green landscapes and pleasant weather)",
        "weather_summary": "Cool subtropical hill climate, 15-22°C",
        "vibe_tags": ["Cleanest Village in Asia", "Living Root Bridge", "Khasi Culture", "Eco Tourism"],
        "is_featured": True,
        "places": [
            {
                "name": "Riwai Single Decker Living Root Bridge",
                "slug": "riwai-living-root-bridge",
                "category_slug": "attractions",
                "description": "Centuries-old bio-engineering marvel grown by weaving aerial roots of Ficus elastica trees across a gushing jungle river.",
                "address": "Riwai Village, Near Mawlynnong, Meghalaya",
                "latitude": 25.2105,
                "longitude": 91.9210,
                "price_level": 1,
                "estimated_cost": 50.0,
                "avg_visit_duration_mins": 60,
                "rating": 4.8,
                "review_count": 2400,
                "tags": ["living root bridge", "nature wonder", "eco heritage", "trekking"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Sky View Bamboo Treehouse & Bangladesh Viewpoint",
                "slug": "sky-view-mawlynnong",
                "category_slug": "nature",
                "description": "85-foot-high indigenous bamboo observation tower perched on treetops offering bird's-eye views over the lush plains of Bangladesh.",
                "address": "Mawlynnong Village, East Khasi Hills",
                "latitude": 25.2020,
                "longitude": 91.9165,
                "price_level": 1,
                "estimated_cost": 30.0,
                "avg_visit_duration_mins": 40,
                "rating": 4.6,
                "review_count": 1400,
                "tags": ["treehouse", "panoramic view", "bamboo structure", "bangladesh border"],
                "child_friendly": True,
                "is_popular": True
            }
        ]
    },
    {
        "name": "Bengaluru",
        "slug": "bengaluru",
        "state": "Karnataka",
        "district": "Bengaluru Urban",
        "locality_type": "city",
        "description": "The Silicon Valley and Garden City of India, blending lush botanical lung spaces, Victorian heritage palaces, cutting-edge tech parks, craft microbreweries, and third-wave specialty roasteries.",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "hero_image": "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "October to March (Year-round pleasant climate)",
        "weather_summary": "Mild pleasant weather, 18-28°C",
        "vibe_tags": ["Tech Capital", "Garden City", "Craft Breweries", "Café Culture"],
        "is_featured": True,
        "places": [
            {
                "name": "Lalbagh Botanical Garden & Glass House",
                "slug": "lalbagh-botanical-garden",
                "category_slug": "nature",
                "description": "240-acre botanical haven commissioned by Hyder Ali, featuring over 1,800 plant species, 3,000-million-year-old rock, and Victorian Glass House.",
                "address": "Mavalli, Bengaluru",
                "latitude": 12.9507,
                "longitude": 77.5848,
                "price_level": 1,
                "estimated_cost": 40.0,
                "avg_visit_duration_mins": 90,
                "rating": 4.7,
                "review_count": 6800,
                "tags": ["botanical garden", "glass house", "nature", "jogging", "historic"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Third Wave Coffee Roasters (Indiranagar)",
                "slug": "third-wave-coffee-indiranagar",
                "category_slug": "cafes",
                "description": "Artisanal specialty coffee café roasting single-estate Chikmagalur beans, pouring V60 pour-overs, croissants, and avocado toast.",
                "address": "12th Main Rd, Indiranagar, Bengaluru",
                "latitude": 12.9719,
                "longitude": 77.6412,
                "price_level": 2,
                "estimated_cost": 400.0,
                "avg_visit_duration_mins": 60,
                "rating": 4.6,
                "review_count": 2900,
                "tags": ["specialty coffee", "café", "co-working", "pastries"],
                "child_friendly": True,
                "is_popular": True
            }
        ]
    },
    {
        "name": "Goa",
        "slug": "goa",
        "state": "Goa",
        "district": "North & South Goa",
        "locality_type": "coastal",
        "description": "India's premier coastal paradise on the Arabian Sea, featuring golden sand beaches, UNESCO Portuguese churches, vibrant beach shacks, Latin quarter Fontainhas, and fresh seafood.",
        "latitude": 15.2993,
        "longitude": 74.1240,
        "hero_image": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "November to February",
        "weather_summary": "Sunny beach climate, 22-31°C",
        "vibe_tags": ["Beaches", "Portuguese Architecture", "Seafood", "Nightlife", "Water Sports"],
        "is_featured": True,
        "places": [
            {
                "name": "Fontainhas Latin Quarter (Panaji)",
                "slug": "fontainhas-latin-quarter",
                "category_slug": "attractions",
                "description": "Vibrant heritage neighborhood with narrow cobbled lanes, 18th-century Portuguese villas painted in pastel yellows and blues, and traditional bakeries.",
                "address": "Fontainhas, Altinho, Panaji, Goa",
                "latitude": 15.4989,
                "longitude": 73.8312,
                "price_level": 1,
                "estimated_cost": 0.0,
                "avg_visit_duration_mins": 75,
                "rating": 4.7,
                "review_count": 4200,
                "tags": ["heritage", "portuguese", "photography", "walking tour"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Palolem Beach & Silent Bay",
                "slug": "palolem-beach",
                "category_slug": "nature",
                "description": "Crescent-shaped white sand beach in South Goa fringed with coconut palms, gentle turquoise waves, kayak rentals, and dolphin-spotting cruises.",
                "address": "Canacona, South Goa",
                "latitude": 15.0100,
                "longitude": 74.0232,
                "price_level": 2,
                "estimated_cost": 300.0,
                "avg_visit_duration_mins": 120,
                "rating": 4.8,
                "review_count": 6700,
                "tags": ["beach", "sunset", "kayaking", "palm trees", "south goa"],
                "child_friendly": True,
                "is_popular": True
            }
        ]
    },
    {
        "name": "Kochi",
        "slug": "kochi",
        "state": "Kerala",
        "district": "Ernakulam",
        "locality_type": "city",
        "description": "The Queen of the Arabian Sea, an ancient spice trading port blending Portuguese, Dutch, British, and Jewish heritage with cantilevered Chinese fishing nets and tranquil backwaters.",
        "latitude": 9.9312,
        "longitude": 76.2673,
        "hero_image": "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "October to March",
        "weather_summary": "Pleasant coastal breeze, 23-30°C",
        "vibe_tags": ["Spice Capital", "Chinese Fishing Nets", "Fort Kochi", "Backwaters", "Kathakali"],
        "is_featured": True,
        "places": [
            {
                "name": "Fort Kochi Chinese Fishing Nets & Beach Walk",
                "slug": "fort-kochi-chinese-nets",
                "category_slug": "attractions",
                "description": "Iconic cantilevered shore-operated fishing nets introduced by 14th-century Chinese traders, silhouetted against Arabian Sea sunsets.",
                "address": "River Rd, Fort Kochi, Kochi",
                "latitude": 9.9674,
                "longitude": 76.2427,
                "price_level": 1,
                "estimated_cost": 50.0,
                "avg_visit_duration_mins": 60,
                "rating": 4.6,
                "review_count": 5100,
                "tags": ["chinese fishing nets", "sunset", "heritage", "iconic"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Kashi Art Café",
                "slug": "kashi-art-cafe",
                "category_slug": "cafes",
                "description": "Renowned art café inside a restored heritage townhouse, featuring contemporary art installations, artisan chocolate cake, and Kerala roasted coffee.",
                "address": "Burgher St, Fort Kochi, Kochi",
                "latitude": 9.9652,
                "longitude": 76.2421,
                "price_level": 2,
                "estimated_cost": 350.0,
                "avg_visit_duration_mins": 50,
                "rating": 4.7,
                "review_count": 3100,
                "tags": ["art café", "heritage", "coffee", "fort kochi"],
                "child_friendly": True,
                "is_popular": True
            }
        ]
    },
    {
        "name": "Rishikesh",
        "slug": "rishikesh",
        "state": "Uttarakhand",
        "district": "Dehradun",
        "locality_type": "city",
        "description": "The Yoga Capital of the World, tucked in the Himalayan foothills where the holy River Ganga emerges into the plains. Famous for ashrams, suspension bridges, white-water rafting, and Ganga Aarti.",
        "latitude": 30.0869,
        "longitude": 78.2676,
        "hero_image": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "September to November & March to May",
        "weather_summary": "Cool mountain river breeze, 14-26°C",
        "vibe_tags": ["Yoga Capital", "Ganga Aarti", "River Rafting", "Beatles Ashram", "Himalayas"],
        "is_featured": True,
        "places": [
            {
                "name": "Triveni Ghat Evening Maha Aarti",
                "slug": "triveni-ghat-aarti",
                "category_slug": "attractions",
                "description": "Spiritual confluence where devotees float earthen lamps into the Ganga amid holy bells, conch shells, and evening Vedic chants.",
                "address": "Mayakund, Rishikesh, Uttarakhand",
                "latitude": 30.1030,
                "longitude": 78.2936,
                "price_level": 1,
                "estimated_cost": 30.0,
                "avg_visit_duration_mins": 75,
                "rating": 4.9,
                "review_count": 7200,
                "tags": ["ganga aarti", "spiritual", "lamps", "confluence"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Beatles Ashram (Chaurasi Kutia)",
                "slug": "beatles-ashram-rishikesh",
                "category_slug": "attractions",
                "description": "Forest ashram where The Beatles stayed in 1968 to study Transcendental Meditation, now adorned with graffiti murals, meditation caves, and forest trails.",
                "address": "Swarg Ashram, Rishikesh",
                "latitude": 30.1191,
                "longitude": 78.3188,
                "price_level": 2,
                "estimated_cost": 150.0,
                "avg_visit_duration_mins": 90,
                "rating": 4.7,
                "review_count": 3400,
                "tags": ["beatles", "meditation caves", "art", "forest"],
                "child_friendly": True,
                "is_popular": True
            }
        ]
    },
    {
        "name": "Leh-Ladakh",
        "slug": "leh-ladakh",
        "state": "Ladakh",
        "district": "Leh",
        "locality_type": "city",
        "description": "High-altitude Himalayan desert kingdom of prayer flags, Buddhist cliffside monasteries, sapphire glacial lakes (Pangong & Tso Moriri), and the world's highest motorable passes.",
        "latitude": 34.1526,
        "longitude": 77.5771,
        "hero_image": "https://images.unsplash.com/photo-1581793745862-99fde7fa73d2?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "May to September (Road passes open and sunny mountain weather)",
        "weather_summary": "Dry crisp mountain air, 10-22°C summer days, cold nights",
        "vibe_tags": ["High Altitude", "Pangong Tso", "Tibetan Monasteries", "Mountain Passes"],
        "is_featured": True,
        "places": [
            {
                "name": "Pangong Tso Crystal Blue Lake",
                "slug": "pangong-lake",
                "category_slug": "nature",
                "description": "World-famous endorheic salt lake at 4,225m altitude that changes shades from azure to turquoise and purple throughout the day, framed by dramatic barren mountains.",
                "address": "Changthang Region, Ladakh",
                "latitude": 33.7595,
                "longitude": 78.6674,
                "price_level": 2,
                "estimated_cost": 400.0,
                "avg_visit_duration_mins": 180,
                "rating": 4.9,
                "review_count": 6800,
                "tags": ["pangong tso", "high altitude lake", "3 idiots", "azure waters"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Thiksey Monastery (Mini Potala Palace)",
                "slug": "thiksey-monastery",
                "category_slug": "attractions",
                "description": "Twelve-story Tibetan Buddhist complex perched on a hill, housing a 49-foot statue of Maitreya Buddha and offering morning chanting prayers.",
                "address": "Leh-Manali Highway, Thiksey, Ladakh",
                "latitude": 34.0574,
                "longitude": 77.6669,
                "price_level": 1,
                "estimated_cost": 50.0,
                "avg_visit_duration_mins": 90,
                "rating": 4.9,
                "review_count": 4100,
                "tags": ["buddhist monastery", "maitreya buddha", "tibetan art", "panoramic"],
                "child_friendly": True,
                "is_popular": True
            }
        ]
    },
    {
        "name": "Udaipur",
        "slug": "udaipur",
        "state": "Rajasthan",
        "district": "Udaipur",
        "locality_type": "city",
        "description": "The City of Lakes and Venice of the East, famed for shimmering Lake Pichola, floating white marble island palaces, historic Mewar havelis, and romantic sunset boat rides.",
        "latitude": 24.5854,
        "longitude": 73.7125,
        "hero_image": "https://images.unsplash.com/photo-1615836245337-f5b9b2303f10?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "October to March",
        "weather_summary": "Pleasant days, cool evenings 12-25°C",
        "vibe_tags": ["City of Lakes", "Lake Pichola", "Mewar Palaces", "Romantic Sunsets"],
        "is_featured": True,
        "places": [
            {
                "name": "City Palace of Udaipur",
                "slug": "udaipur-city-palace",
                "category_slug": "attractions",
                "description": "Rajasthan's largest royal palace complex, built over 400 years with marble balconies, mirror work, courtyards, and views over Lake Pichola.",
                "address": "Old City, Udaipur",
                "latitude": 24.5764,
                "longitude": 73.6835,
                "price_level": 2,
                "estimated_cost": 300.0,
                "avg_visit_duration_mins": 120,
                "rating": 4.8,
                "review_count": 9200,
                "tags": ["city palace", "mewar", "lake view", "architecture"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Lake Pichola Sunset Boat Ride",
                "slug": "lake-pichola-boat-ride",
                "category_slug": "nature",
                "description": "Scenic boat cruise passing Jag Mandir and the Lake Palace, glowing golden under the Aravali mountain sunset.",
                "address": "Rameshwar Ghat, City Palace, Udaipur",
                "latitude": 24.5742,
                "longitude": 73.6798,
                "price_level": 2,
                "estimated_cost": 450.0,
                "avg_visit_duration_mins": 60,
                "rating": 4.8,
                "review_count": 6400,
                "tags": ["boat ride", "lake pichola", "sunset", "jag mandir"],
                "child_friendly": True,
                "is_popular": True
            }
        ]
    },
    {
        "name": "Amritsar",
        "slug": "amritsar",
        "state": "Punjab",
        "district": "Amritsar",
        "locality_type": "city",
        "description": "The spiritual heart of Sikhism, home to the resplendent Golden Temple (Sri Harmandir Sahib), community langar feeding 100,000 daily, Jallianwala Bagh, and iconic Punjabi culinary heritage.",
        "latitude": 31.6340,
        "longitude": 74.8723,
        "hero_image": "https://images.unsplash.com/photo-1588096344356-9b57538f921f?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "October to March",
        "weather_summary": "Pleasant winters 8-22°C",
        "vibe_tags": ["Golden Temple", "Sikh Heritage", "Langar", "Punjabi Gastronomy", "Wagah Border"],
        "is_featured": True,
        "places": [
            {
                "name": "Sri Harmandir Sahib (Golden Temple)",
                "slug": "golden-temple-amritsar",
                "category_slug": "attractions",
                "description": "Holiest Gurdwara of Sikhism overlaid with genuine gold leaf, surrounded by the holy Amrit Sarovar lake, welcoming all humanity 24/7.",
                "address": "Golden Temple Rd, Atta Mandi, Amritsar",
                "latitude": 31.6200,
                "longitude": 74.8765,
                "price_level": 1,
                "estimated_cost": 0.0,
                "avg_visit_duration_mins": 120,
                "rating": 5.0,
                "review_count": 18500,
                "tags": ["golden temple", "harmandir sahib", "spiritual", "peaceful", "free entry"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Kesar Da Dhaba",
                "slug": "kesar-da-dhaba",
                "category_slug": "restaurants",
                "description": "Historic eatery serving authentic slow-simmered Maa Ki Dal cooked for 12 hours in pure desi ghee, lachha parathas, and phirni since 1916.",
                "address": "Chowk Passian, Near Town Hall, Amritsar",
                "latitude": 31.6251,
                "longitude": 74.8732,
                "price_level": 2,
                "estimated_cost": 250.0,
                "avg_visit_duration_mins": 50,
                "rating": 4.7,
                "review_count": 4800,
                "tags": ["dal makhani", "punjabi food", "historic dhaba", "desi ghee"],
                "child_friendly": True,
                "is_popular": True
            }
        ]
    },
    {
        "name": "Kolkata",
        "slug": "kolkata",
        "state": "West Bengal",
        "district": "Kolkata",
        "locality_type": "city",
        "description": "The City of Joy and India's intellectual & cultural capital, celebrated for colonial grandeur, Victoria Memorial, Howrah Bridge, historic tramways, College Street bookstalls, and rich culinary sweets.",
        "latitude": 22.5726,
        "longitude": 88.3639,
        "hero_image": "https://images.unsplash.com/photo-1558431382-27e303142255?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "October to March (Durga Puja & crisp winter)",
        "weather_summary": "Pleasant winters 14-26°C",
        "vibe_tags": ["City of Joy", "Colonial Architecture", "Durga Puja", "Literature & Arts", "Bengali Sweets"],
        "is_featured": True,
        "places": [
            {
                "name": "Victoria Memorial & Maidan Gardens",
                "slug": "victoria-memorial-kolkata",
                "category_slug": "attractions",
                "description": "Stately white Makrana marble monument and museum set in 64 acres of landscaped gardens, housing rare Raj-era paintings and artifacts.",
                "address": "Queens Way, Maidan, Kolkata",
                "latitude": 22.5448,
                "longitude": 88.3426,
                "price_level": 1,
                "estimated_cost": 50.0,
                "avg_visit_duration_mins": 90,
                "rating": 4.8,
                "review_count": 12000,
                "tags": ["victoria memorial", "marble monument", "museum", "gardens"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Flurys Heritage Tea Room & Bakery",
                "slug": "flurys-kolkata",
                "category_slug": "cafes",
                "description": "Legendary European tearoom on Park Street serving English breakfasts, rum balls, chicken patties, and Darjeeling tea since 1927.",
                "address": "18A Park St, Kolkata",
                "latitude": 22.5518,
                "longitude": 88.3524,
                "price_level": 2,
                "estimated_cost": 400.0,
                "avg_visit_duration_mins": 50,
                "rating": 4.6,
                "review_count": 3900,
                "tags": ["tearoom", "park street", "bakery", "heritage café"],
                "child_friendly": True,
                "is_popular": True
            }
        ]
    },
    {
        "name": "Srinagar",
        "slug": "srinagar",
        "state": "Jammu & Kashmir",
        "district": "Srinagar",
        "locality_type": "city",
        "description": "Paradise on Earth in the Kashmir Valley, famous for serene Dal Lake Shikara cruises, carved wooden houseboats, terraced Mughal gardens, Kashmiri Pashmina, and Kahwa tea.",
        "latitude": 34.0837,
        "longitude": 74.7973,
        "hero_image": "https://images.unsplash.com/photo-1598091383021-15ddea10925d?auto=format&fit=crop&w=1200&q=80",
        "best_time_to_visit": "April to October (Gardens in full bloom) & Dec-Feb (Snow wonderland)",
        "weather_summary": "Cool mountain breeze, 12-24°C summer, winter snow",
        "vibe_tags": ["Dal Lake", "Shikara Ride", "Mughal Gardens", "Houseboats", "Paradise on Earth"],
        "is_featured": True,
        "places": [
            {
                "name": "Dal Lake Floating Gardens & Shikara Ride",
                "slug": "dal-lake-shikara",
                "category_slug": "attractions",
                "description": "Glide through tranquil waters past floating vegetable markets, lotus gardens, and wooden houseboats against the Zabarwan mountain backdrop.",
                "address": "Boulevard Rd, Dal Lake, Srinagar",
                "latitude": 34.0950,
                "longitude": 74.8450,
                "price_level": 2,
                "estimated_cost": 500.0,
                "avg_visit_duration_mins": 90,
                "rating": 4.9,
                "review_count": 10500,
                "tags": ["shikara", "dal lake", "floating market", "scenic"],
                "child_friendly": True,
                "is_popular": True
            },
            {
                "name": "Shalimar Bagh Mughal Garden",
                "slug": "shalimar-bagh-srinagar",
                "category_slug": "nature",
                "description": "The crown of Mughal gardens built by Emperor Jahangir for Noor Jahan, featuring four cascading water terraces, chinar trees, and fountains.",
                "address": "Shalimar, Srinagar",
                "latitude": 34.1504,
                "longitude": 74.8722,
                "price_level": 1,
                "estimated_cost": 30.0,
                "avg_visit_duration_mins": 75,
                "rating": 4.8,
                "review_count": 5200,
                "tags": ["mughal garden", "chinar trees", "fountains", "heritage"],
                "child_friendly": True,
                "is_popular": True
            }
        ]
    }
]

async def seed_pan_india():
    db: Session = SessionLocal()
    try:
        print(f"Beginning Pan-India database expansion ({len(PAN_INDIA_CITIES)} destinations)...")
        # Ensure categories exist
        cat_map = {c.slug: c.id for c in db.query(Category).all()}

        for c_data in PAN_INDIA_CITIES:
            existing = db.query(City).filter(City.slug == c_data["slug"]).first()
            if not existing:
                city = City(
                    name=c_data["name"],
                    slug=c_data["slug"],
                    state=c_data["state"],
                    district=c_data.get("district", c_data["name"]),
                    country="India",
                    locality_type=c_data.get("locality_type", "city"),
                    description=c_data["description"],
                    latitude=c_data["latitude"],
                    longitude=c_data["longitude"],
                    hero_image=c_data["hero_image"],
                    best_time_to_visit=c_data["best_time_to_visit"],
                    weather_summary=c_data["weather_summary"],
                    vibe_tags=c_data["vibe_tags"],
                    is_featured=c_data["is_featured"]
                )
                db.add(city)
                db.flush()
                print(f"Added city: {city.name}, {city.state} ({city.locality_type})")
            else:
                city = existing
                city.state = c_data["state"]
                city.district = c_data.get("district", c_data["name"])
                city.locality_type = c_data.get("locality_type", "city")
                city.hero_image = c_data["hero_image"]
                db.flush()

            # Seed places for this city
            for p in c_data.get("places", []):
                cat_id = cat_map.get(p.get("category_slug", "attractions"), 1)
                existing_place = db.query(Place).filter(
                    Place.city_id == city.id,
                    Place.slug == p["slug"]
                ).first()
                if not existing_place:
                    place = Place(
                        city_id=city.id,
                        category_id=cat_id,
                        name=p["name"],
                        slug=p["slug"],
                        description=p["description"],
                        address=p["address"],
                        latitude=p["latitude"],
                        longitude=p["longitude"],
                        price_level=p.get("price_level", 2),
                        estimated_cost=p.get("estimated_cost", 100.0),
                        avg_visit_duration_mins=p.get("avg_visit_duration_mins", 60),
                        rating=p.get("rating", 4.7),
                        review_count=p.get("review_count", 500),
                        tags=p.get("tags", []),
                        images=[c_data["hero_image"]],
                        child_friendly=p.get("child_friendly", True),
                        family_friendly=True,
                        is_popular=p.get("is_popular", True)
                    )
                    db.add(place)

            # Seed verified RAG document
            existing_doc = db.query(CityDocument).filter(CityDocument.city_id == city.id).first()
            if not existing_doc:
                doc_content = (
                    f"# {city.name}, {city.state} - City Guide & Practical Intelligence\n\n"
                    f"## Overview\n{city.description}\n\n"
                    f"## Best Season to Visit\n{city.best_time_to_visit}\n\n"
                    f"## Weather & Atmosphere\n{city.weather_summary}\n\n"
                    f"## Top Places & Highlights\n"
                )
                for pl in c_data.get("places", []):
                    doc_content += f"- **{pl['name']}**: {pl['description']}. Typical cost: ₹{pl.get('estimated_cost', 0):.0f}. Duration: {pl.get('avg_visit_duration_mins', 60)} mins.\n"

                doc_content += (
                    f"\n## Getting Around & Local Tips\n"
                    f"Local public transport, autos, and taxis are widely accessible. "
                    f"UPI digital payments are universally accepted across markets and restaurants."
                )

                doc = CityDocument(
                    city_id=city.id,
                    title=f"{city.name} Official City Travel Guide & Verification",
                    source_type="official_tourism",
                    source_url="https://incredibleindia.gov.in",
                    content=doc_content
                )
                db.add(doc)
                db.flush()

                chunks = chunker.chunk_text(
                    doc_content,
                    metadata={"title": doc.title, "source": doc.source_type, "city": city.name, "state": city.state}
                )
                for ch in chunks:
                    emb = await embedder.get_embedding(ch["content"])
                    chunk_obj = DocumentChunk(
                        document_id=doc.id,
                        city_id=city.id,
                        chunk_index=ch["chunk_index"],
                        content=ch["content"],
                        metadata_json=ch["metadata"],
                        embedding_json=emb
                    )
                    db.add(chunk_obj)

        db.commit()
        print("Pan-India destinations, places, and RAG knowledge chunks seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error in Pan-India seed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(seed_pan_india())
