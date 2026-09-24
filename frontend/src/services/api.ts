import {
  City, Category, Place, ItineraryPlan, RAGQueryResponse,
  AgentChatResponse, CityAnalytics, UserProfile
} from '../types';

const API_BASE = '/api/v1';

async function safeParseJson(res: Response, fallback: any = null): Promise<any> {
  try {
    const text = await res.text();
    if (!text || !text.trim()) return fallback;
    return JSON.parse(text);
  } catch {
    return fallback;
  }
}

function getAuthHeader(): HeadersInit {
  const token = localStorage.getItem('plan_ai_token');
  return token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
}

export const api = {
  // Pan-India Cities, Towns & Villages
  async getCities(): Promise<City[]> {
    const res = await fetch(`${API_BASE}/cities/`);
    if (!res.ok) throw new Error('Failed to load cities');
    return (await safeParseJson(res, [])) as City[];
  },

  async getCity(idOrSlug: string | number): Promise<any> {
    const res = await fetch(`${API_BASE}/cities/${idOrSlug}`);
    if (!res.ok) throw new Error('Failed to load city details');
    return safeParseJson(res, null);
  },

  async searchLocalities(q: string): Promise<any[]> {
    const res = await fetch(`${API_BASE}/cities/search?q=${encodeURIComponent(q)}`);
    if (!res.ok) return [];
    return (await safeParseJson(res, [])) as any[];
  },

  async resolveLocality(query: string): Promise<City> {
    const res = await fetch(`${API_BASE}/cities/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    if (!res.ok) {
      const err = await safeParseJson(res, {});
      throw new Error(err.detail || 'Failed to resolve locality');
    }
    return safeParseJson(res, null);
  },

  async getAllStates(): Promise<string[]> {
    const res = await fetch(`${API_BASE}/cities/states`);
    if (!res.ok) return [];
    const data = await safeParseJson(res, { states: [] });
    return data.states || [];
  },

  // Categories & Places
  async getCategories(): Promise<Category[]> {
    const res = await fetch(`${API_BASE}/places/categories`);
    if (!res.ok) throw new Error('Failed to load categories');
    return res.json();
  },

  async getPlaces(params: {
    city_id?: number;
    category_slug?: string;
    max_price?: number;
    child_friendly?: boolean;
    is_popular?: boolean;
    search?: string;
  } = {}): Promise<Place[]> {
    const query = new URLSearchParams();
    if (params.city_id) query.append('city_id', params.city_id.toString());
    if (params.category_slug) query.append('category_slug', params.category_slug);
    if (params.max_price !== undefined) query.append('max_price', params.max_price.toString());
    if (params.child_friendly !== undefined) query.append('child_friendly', params.child_friendly.toString());
    if (params.is_popular !== undefined) query.append('is_popular', params.is_popular.toString());
    if (params.search) query.append('search', params.search);

    const res = await fetch(`${API_BASE}/places/?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to load places');
    return res.json();
  },

  async createPlace(data: any): Promise<Place> {
    const res = await fetch(`${API_BASE}/places/`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to create place');
    }
    return res.json();
  },

  // Hybrid Search
  async search(q: string, cityId?: number): Promise<any> {
    const query = new URLSearchParams({ q });
    if (cityId) query.append('city_id', cityId.toString());
    const res = await fetch(`${API_BASE}/search/?${query.toString()}`);
    if (!res.ok) throw new Error('Search failed');
    return res.json();
  },

  // RAG Question Answering
  async ragQuery(query: string, cityId?: number): Promise<RAGQueryResponse> {
    const res = await fetch(`${API_BASE}/rag/query`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: JSON.stringify({ query, city_id: cityId, top_k: 4 }),
    });
    if (!res.ok) throw new Error('RAG query failed');
    return res.json();
  },

  // Multi-Agent Chat
  async chatWithAgents(message: string, cityId?: number): Promise<AgentChatResponse> {
    const res = await fetch(`${API_BASE}/agents/chat`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: JSON.stringify({ message, city_id: cityId }),
    });
    if (!res.ok) throw new Error('Agent chat failed');
    return res.json();
  },

  // AI Itinerary Planner
  async planItinerary(data: {
    city_id: number;
    budget: number;
    available_hours: number;
    start_time: string;
    start_location: string;
    interests: string[];
    pace: string;
    group_size: number;
  }): Promise<ItineraryPlan> {
    const res = await fetch(`${API_BASE}/itinerary/plan`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Itinerary generation failed');
    return res.json();
  },

  async saveItinerary(data: any): Promise<any> {
    const res = await fetch(`${API_BASE}/itinerary/save`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to save itinerary');
    return res.json();
  },

  async getSavedItineraries(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/itinerary/saved`, {
      headers: getAuthHeader(),
    });
    if (!res.ok) return [];
    return res.json();
  },

  // ML Recommendations
  async getRecommendations(cityId: number, interests: string[] = [], budgetTier = 'moderate'): Promise<any> {
    const res = await fetch(`${API_BASE}/recommendations/`, {
      method: 'POST',
      headers: getAuthHeader(),
      body: JSON.stringify({ city_id: cityId, interests, budget_tier: budgetTier, limit: 6 }),
    });
    if (!res.ok) throw new Error('Failed to fetch recommendations');
    return res.json();
  },

  // City Analytics & K-Means Clusters
  async getCityAnalytics(cityId: number): Promise<CityAnalytics> {
    const res = await fetch(`${API_BASE}/analytics/city/${cityId}`);
    if (!res.ok) throw new Error('Failed to load city analytics');
    return res.json();
  },

  async getOverviewAnalytics(): Promise<CityAnalytics> {
    const res = await fetch(`${API_BASE}/analytics/overview`);
    if (!res.ok) throw new Error('Failed to load analytics overview');
    return res.json();
  },

  // Auth & Profile
  async login(email: string, password: string): Promise<any> {
    let res: Response;
    try {
      res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password }),
      });
    } catch (networkErr: any) {
      throw new Error('Cannot reach backend server. Please make sure the backend is running on port 8000.');
    }

    if (!res.ok) {
      const err = await safeParseJson(res, {});
      let detail = err.detail || err.message || (res.status === 401 ? 'Incorrect email or password.' : `Server error (${res.status})`);
      throw new Error(detail);
    }

    const data = await safeParseJson(res, null);
    if (!data || !data.access_token) {
      throw new Error('Invalid authentication response from server.');
    }
    localStorage.setItem('plan_ai_token', data.access_token);
    return data;
  },

  async register(
    email: string,
    password: string,
    fullName: string,
    phoneNumber?: string,
    homeCity?: string,
    homeState?: string
  ): Promise<any> {
    let res: Response;
    try {
      res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.trim(),
          password,
          full_name: fullName,
          phone_number: phoneNumber || undefined,
          home_city: homeCity || undefined,
          home_state: homeState || undefined,
        }),
      });
    } catch (networkErr: any) {
      throw new Error('Cannot reach backend server. Please make sure the backend is running on port 8000.');
    }

    if (!res.ok) {
      const err = await safeParseJson(res, {});
      let detail = err.detail || err.message || `Registration failed (${res.status})`;
      throw new Error(detail);
    }

    const data = await safeParseJson(res, null);
    if (!data || !data.access_token) {
      throw new Error('Invalid registration response from server.');
    }
    localStorage.setItem('plan_ai_token', data.access_token);
    return data;
  },

  async getProfile(): Promise<UserProfile | null> {
    const token = localStorage.getItem('plan_ai_token');
    if (!token) return null;
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: getAuthHeader(),
      });
      if (!res.ok) return null;
      return safeParseJson(res, null);
    } catch {
      return null;
    }
  },

  async updateProfile(data: any): Promise<UserProfile> {
    const res = await fetch(`${API_BASE}/auth/profile`, {
      method: 'PUT',
      headers: getAuthHeader(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await safeParseJson(res, {});
      throw new Error(err.detail || 'Failed to update profile');
    }
    return safeParseJson(res, null);
  },

  logout() {
    localStorage.removeItem('plan_ai_token');
  }
};
