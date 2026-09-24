import numpy as np
from sklearn.cluster import KMeans
from typing import List, Dict, Any, Optional

PERSONAS = [
    {
        "cluster_id": 0,
        "persona_name": "Budget Backpacker & Student Explorer",
        "description": "Prefers cost-effective journeys, scenic lookouts, heritage walks, transit options, and cozy pocket-friendly cafés.",
        "key_traits": ["Low budget focus", "Fast/Walking pace", "Scenic & Cultural highlights", "Independent exploration"],
        "recommended_categories": ["Attractions", "Cafés", "Nature", "Transport"]
    },
    {
        "cluster_id": 1,
        "persona_name": "Cultural Heritage & History Enthusiast",
        "description": "Seeks historical depth, colonial architecture, ancient temples, museums, and traditional culinary heritage.",
        "key_traits": ["Historical monuments", "Guided museums", "Medium budget", "Rich local storytelling"],
        "recommended_categories": ["Attractions", "Important Places", "Events", "Restaurants"]
    },
    {
        "cluster_id": 2,
        "persona_name": "Culinary & Café Connoisseur",
        "description": "Driven by gastronomical delights, specialty roasteries, scenic dining spots, and local street flavors.",
        "key_traits": ["Food discovery", "Artisanal coffee", "Moderate to Luxury spending", "Atmospheric dining"],
        "recommended_categories": ["Cafés", "Restaurants", "Shopping"]
    },
    {
        "cluster_id": 3,
        "persona_name": "Family & Comfort Explorer",
        "description": "Prioritizes child-friendly amenities, relaxed pacing, spacious attractions, safe transit, and group dining.",
        "key_traits": ["Child-friendly", "Relaxed pacing", "Comfortable transit", "Family amenities"],
        "recommended_categories": ["Nature", "Hotels", "Restaurants", "Attractions"]
    }
]

class UserClusterer:
    def __init__(self, n_clusters: int = 4):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        self._initialize_centroids()

    def _initialize_centroids(self):
        # Anchor synthetic centroids corresponding to the 4 personas:
        # Features: [Budget Tier (1-3), Pace (1-3), Culture (0-1), Food (0-1), Nature (0-1)]
        initial_centroids = np.array([
            [1.0, 3.0, 0.4, 0.4, 0.8],  # 0: Budget Backpacker
            [2.0, 2.0, 0.9, 0.3, 0.2],  # 1: Heritage & History
            [2.5, 1.5, 0.2, 0.9, 0.3],  # 2: Culinary & Cafe
            [2.0, 1.0, 0.4, 0.5, 0.6],  # 3: Family & Comfort
        ], dtype=np.float64)

        # Fit model on prototype dataset
        np.random.seed(42)
        samples = []
        for c in initial_centroids:
            noise = np.random.normal(0, 0.1, size=(25, 5))
            samples.append(np.clip(c + noise, 0.0, 3.0).astype(np.float64))
        X = np.vstack(samples).astype(np.float64)
        self.kmeans.fit(X)

    def predict_persona(
        self,
        budget_tier: str = "moderate",
        pace: str = "medium",
        interests: List[str] = []
    ) -> Dict[str, Any]:
        """
        Predicts which persona cluster a user belongs to based on preferences.
        """
        budget_map = {"budget": 1.0, "moderate": 2.0, "luxury": 3.0}
        pace_map = {"relaxed": 1.0, "medium": 2.0, "packed": 3.0}

        b_val = budget_map.get(budget_tier.lower(), 2.0)
        p_val = pace_map.get(pace.lower(), 2.0)

        interests_str = " ".join([i.lower() for i in interests])
        culture_val = 0.8 if any(k in interests_str for k in ["history", "heritage", "monument", "temple"]) else 0.2
        food_val = 0.9 if any(k in interests_str for k in ["food", "cafe", "restaurant", "culinary"]) else 0.3
        nature_val = 0.8 if any(k in interests_str for k in ["nature", "mountain", "hill", "trek", "scenic"]) else 0.3

        features = np.array([[b_val, p_val, culture_val, food_val, nature_val]], dtype=np.float64)
        cluster_idx = int(self.kmeans.predict(features)[0])

        return PERSONAS[cluster_idx]

    def get_all_clusters_info(self) -> List[Dict[str, Any]]:
        # Proportions across user population simulation
        percentages = [28.5, 24.0, 26.5, 21.0]
        result = []
        for idx, p in enumerate(PERSONAS):
            item = dict(p)
            item["percentage"] = percentages[idx]
            result.append(item)
        return result

user_clusterer = UserClusterer()
