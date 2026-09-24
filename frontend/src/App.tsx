import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { HeroSection } from './components/HeroSection';
import { ExploreView } from './components/ExploreView';
import { TripPlannerView } from './components/TripPlannerView';
import { AIChatAssistantView } from './components/AIChatAssistantView';
import { AnalyticsDashboardView } from './components/AnalyticsDashboardView';
import { AuthModal } from './components/AuthModal';
import { City, Category, Place, UserProfile } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [cities, setCities] = useState<City[]>([]);
  const [currentCity, setCurrentCity] = useState<City | null>(null);
  const [categories, setCategories] = useState<Category[]>([]);
  const [places, setPlaces] = useState<Place[]>([]);
  const [activeTab, setActiveTab] = useState<'explore' | 'planner' | 'chat' | 'analytics'>('explore');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [activePrompt, setActivePrompt] = useState<string | undefined>(undefined);
  const [catalogSearchQuery, setCatalogSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  // 1. Initial Load: Cities, Categories, User Profile
  useEffect(() => {
    const initApp = async () => {
      try {
        const [citiesData, categoriesData] = await Promise.all([
          api.getCities(),
          api.getCategories(),
        ]);
        setCities(citiesData);
        if (citiesData.length > 0) {
          // Default to Shimla or first featured city
          const featured = citiesData.find(c => c.slug === 'shimla') || citiesData[0];
          setCurrentCity(featured);
        }
        setCategories(categoriesData);

        const user = await api.getProfile();
        setProfile(user);
      } catch (err) {
        console.error('Initialization error:', err);
      } finally {
        setLoading(false);
      }
    };
    initApp();
  }, []);

  // 2. Load Places when currentCity or selectedCategory changes
  useEffect(() => {
    if (!currentCity) return;
    const loadPlaces = async () => {
      try {
        const data = await api.getPlaces({
          city_id: currentCity.id,
          category_slug: selectedCategory || undefined,
        });
        setPlaces(data);
      } catch (err) {
        console.error('Failed to load places:', err);
      }
    };
    loadPlaces();
  }, [currentCity, selectedCategory]);

  const handleSelectCity = (city: City) => {
    setCurrentCity(city);
    setSelectedCategory(null);
    setCatalogSearchQuery('');
  };

  const handleTriggerPrompt = (prompt: string) => {
    setActivePrompt(prompt);
    setActiveTab('chat');
  };

  const handleSearchSubmit = async (query: string) => {
    const cleanQ = query.trim().toLowerCase();
    // 1. Direct match on existing city name, slug, or state
    const matchedCity = cities.find(c => 
      c.name.toLowerCase() === cleanQ || 
      c.slug.toLowerCase() === cleanQ ||
      (c.state && c.state.toLowerCase() === cleanQ)
    );
    if (matchedCity) {
      setCurrentCity(matchedCity);
      setCatalogSearchQuery('');
      setActiveTab('explore');
      return;
    }

    // 2. Try resolving via Pan-India locality resolver if it looks like a city/village
    if (cleanQ.length >= 3 && !cleanQ.includes('how') && !cleanQ.includes('what') && !cleanQ.includes('where')) {
      try {
        const resolved = await api.resolveLocality(query.trim());
        if (resolved && resolved.id) {
          setCities(prev => {
            if (prev.some(c => c.id === resolved.id)) return prev;
            return [resolved, ...prev];
          });
          setCurrentCity(resolved);
          setCatalogSearchQuery('');
          setActiveTab('explore');
          return;
        }
      } catch (err) {
        // Fallback to in-catalog search
      }
    }

    setCatalogSearchQuery(query);
    setActiveTab('explore');
    setTimeout(() => {
      const el = document.getElementById('explore-catalog');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }, 50);
  };

  const handlePlaceCreated = (newPlace: Place) => {
    setPlaces(prev => [newPlace, ...prev]);
  };

  const handleAskAIAboutPlace = (placeName: string) => {
    handleTriggerPrompt(`Tell me verified details, opening hours, ticket costs, and child-friendliness for ${placeName} in ${currentCity?.name}.`);
  };

  const handleAddPlaceToPlanner = (place: Place) => {
    setActiveTab('planner');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-400">
        <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4" />
        <h2 className="text-xl font-bold text-white mb-1">PLAN AI CITY</h2>
        <p className="text-xs">Connecting to City Intelligence Platform...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      {/* Top Navbar */}
      <Navbar
        cities={cities}
        currentCity={currentCity}
        onSelectCity={handleSelectCity}
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        profile={profile}
        onOpenAuth={() => setIsAuthOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1">
        {activeTab === 'explore' && (
          <div>
            <HeroSection
              cities={cities}
              currentCity={currentCity}
              onSelectCity={handleSelectCity}
              onTriggerPrompt={handleTriggerPrompt}
              onExploreClick={() => {
                const el = document.getElementById('explore-catalog');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
              }}
              onSearchSubmit={handleSearchSubmit}
            />
            <div id="explore-catalog">
              <ExploreView
                currentCity={currentCity}
                categories={categories}
                places={places}
                selectedCategory={selectedCategory}
                onSelectCategory={setSelectedCategory}
                onAskAIAboutPlace={handleAskAIAboutPlace}
                onAddPlaceToPlanner={handleAddPlaceToPlanner}
                onPlaceCreated={handlePlaceCreated}
                searchQuery={catalogSearchQuery}
                onSearchChange={setCatalogSearchQuery}
              />
            </div>
          </div>
        )}

        {activeTab === 'planner' && (
          <TripPlannerView
            currentCity={currentCity}
            onAskAIQuestion={handleTriggerPrompt}
          />
        )}

        {activeTab === 'chat' && (
          <AIChatAssistantView
            currentCity={currentCity}
            initialPrompt={activePrompt}
          />
        )}

        {activeTab === 'analytics' && (
          <AnalyticsDashboardView
            currentCity={currentCity}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-slate-950 border-t border-slate-900 py-8 px-4 sm:px-6 lg:px-8 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-extrabold text-white text-sm">PLAN AI CITY</span>
            <span>— RAG-Powered City Intelligence & Personalized Planning Platform</span>
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <span>FastAPI + Next.js/React</span>
            <span>•</span>
            <span>Hybrid BM25 + Vector RRF</span>
            <span>•</span>
            <span>Multi-Agent Swarm</span>
          </div>
        </div>
      </footer>

      {/* Auth & Profile Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        profile={profile}
        onProfileUpdated={setProfile}
      />
    </div>
  );
};
