import math
from typing import List, Dict, Any, Tuple

class MapAgent:
    """
    Handles geospatial routing, distances, travel duration estimates,
    and sequence optimization (Traveling Salesperson / Nearest Neighbor).
    """

    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2.0) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    def estimate_travel_time_mins(self, distance_km: float, mode: str = "walk_cab") -> int:
        """
        Estimates transit minutes considering city terrain:
        - Walking: ~4 km/h (15 min/km)
        - Cab / Auto: ~25 km/h in hill/urban traffic (2.5 min/km + 5 min waiting)
        - Metro / Bus: ~20 km/h (3 min/km + 10 min stop time)
        """
        if distance_km <= 0.8:
            return max(5, int(distance_km * 15))  # Walk
        elif mode == "walking":
            return int(distance_km * 16)
        elif mode == "public_transit":
            return int(distance_km * 3.5 + 8)
        else:  # Cab / Auto
            return max(8, int(distance_km * 2.8 + 6))

    def optimize_route_sequence(
        self,
        start_coord: Tuple[float, float],
        places: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Greedy Nearest-Neighbor heuristic to arrange places in an optimal geographical loop/chain.
        Prevents zigzagging across the city.
        """
        if not places:
            return []

        remaining = list(places)
        ordered = []
        current_lat, current_lng = start_coord

        while remaining:
            # Find nearest remaining place
            nearest_idx = 0
            best_dist = float("inf")
            for idx, p in enumerate(remaining):
                d = self.haversine_km(current_lat, current_lng, p["latitude"], p["longitude"])
                if d < best_dist:
                    best_dist = d
                    nearest_idx = idx

            chosen = remaining.pop(nearest_idx)
            chosen["travel_distance_km"] = round(best_dist, 2)
            chosen["travel_time_mins"] = self.estimate_travel_time_mins(best_dist)
            ordered.append(chosen)

            current_lat = chosen["latitude"]
            current_lng = chosen["longitude"]

        return ordered

map_agent = MapAgent()
