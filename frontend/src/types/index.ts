export interface City {
  id: number;
  name: string;
  slug: string;
  state: string;
  district?: string;
  country: string;
  locality_type?: string; // "city", "town", "village", "coastal", "hill_station"
  description: string;
  latitude: number;
  longitude: number;
  hero_image?: string;
  best_time_to_visit?: string;
  weather_summary?: string;
  vibe_tags: string[];
  is_featured: boolean;
  places_count?: number;
  events_count?: number;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  icon: string;
  description?: string;
}

export interface Place {
  id: number;
  city_id: number;
  category_id: number;
  name: string;
  slug: string;
  description: string;
  address: string;
  latitude: number;
  longitude: number;
  price_level: number;
  estimated_cost: number;
  avg_visit_duration_mins: number;
  opening_time: string;
  closing_time: string;
  rating: number;
  review_count: number;
  tags: string[];
  images: string[];
  child_friendly: boolean;
  family_friendly: boolean;
  accessibility: boolean;
  is_popular: boolean;
  seasonal_notes?: string;
  category_name?: string;
  city_name?: string;
  distance_km?: number;
}

export interface ItineraryStop {
  step_number: number;
  time_slot: string;
  type: string;
  place_id?: number;
  place_name: string;
  category: string;
  description: string;
  estimated_cost: number;
  duration_mins: number;
  latitude: number;
  longitude: number;
  address: string;
  travel_from_prev_mins: number;
  travel_mode: string;
  travel_distance_km: number;
  ai_tips: string;
  rag_sources: string[];
}

export interface ItineraryPlan {
  city_id: number;
  city_name: string;
  title: string;
  summary: string;
  total_budget: number;
  estimated_cost: number;
  duration_hours: number;
  start_location: string;
  pace: string;
  group_size: number;
  stops: ItineraryStop[];
  budget_breakdown: Record<string, number>;
  weather_advice: string;
  crowd_season_tips: string;
  ai_reasoning: string;
  saved_itinerary_id?: number;
}

export interface RAGCitation {
  document_id: number;
  title: string;
  source_type: string;
  source_url?: string;
  snippet: string;
  relevance_score: number;
}

export interface RAGQueryResponse {
  query: string;
  answer: string;
  citations: RAGCitation[];
  confidence_score: number;
  retrieval_method: string;
  model_used: string;
}

export interface AgentStep {
  agent_name: string;
  action_taken: string;
  summary_output: string;
  confidence: number;
}

export interface AgentChatResponse {
  reply: string;
  intent_detected: string;
  agents_involved: string[];
  agent_steps: AgentStep[];
  citations: RAGCitation[];
  suggested_places: Array<{
    id?: number;
    name: string;
    category?: string;
    rating?: number;
    cost?: number;
  }>;
  suggested_actions: string[];
}

export interface UserPersonaCluster {
  cluster_id: number;
  persona_name: string;
  description: string;
  percentage: number;
  key_traits: string[];
}

export interface CityAnalytics {
  city_id?: number;
  city_name?: string;
  total_places: number;
  total_events: number;
  total_documents: number;
  total_itineraries_generated: number;
  total_queries: number;
  avg_itinerary_budget: number;
  category_distribution: Array<{ category: string; count: number; avg_price: number }>;
  price_distribution: Array<{ tier: string; percentage: number; place_count: number }>;
  user_persona_clusters: UserPersonaCluster[];
  top_search_queries: Array<{ query: string; count: number }>;
  popular_places: Array<{ id: number; name: string; category: string; rating: number; cost: number; reviews: number }>;
}

export interface UserProfileDetail {
  id: number;
  full_name?: string;
  email: string;
  phone_number?: string;
  home_city?: string;
  home_state?: string;
  country?: string;
  bio?: string;
  preferred_language?: string;
  account_status?: string;
  total_itineraries_created?: number;
  total_places_explored?: number;
  last_login_at?: string;
  created_at?: string;
}

export interface UserProfile {
  id: number;
  email: string;
  full_name?: string;
  role: string;
  profile?: UserProfileDetail;
  preference?: {
    preferred_categories: string[];
    budget_tier: string;
    travel_style: string;
    preferred_pace: string;
    cluster_id?: number;
  };
}
