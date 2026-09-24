import React, { useState, useEffect, useRef } from 'react';
import { Search, Sparkles, Compass, Bot, ArrowRight, MapPin, Landmark, Trees, Mountain } from 'lucide-react';
import { City } from '../types';
import { api } from '../services/api';

interface HeroSectionProps {
  cities: City[];
  currentCity: City | null;
  onSelectCity: (city: City) => void;
  onTriggerPrompt: (prompt: string) => void;
  onExploreClick: () => void;
  onSearchSubmit: (query: string) => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  cities,
  currentCity,
  onSelectCity,
  onTriggerPrompt,
  onExploreClick,
  onSearchSubmit,
}) => {
  const [searchInput, setSearchInput] = useState('');
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeFilter, setActiveFilter] = useState<'all' | 'heritage' | 'hills' | 'villages' | 'coastal'>('all');
  const [resolving, setResolving] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Live Pan-India locality autocomplete
  useEffect(() => {
    const q = searchInput.trim();
    if (q.length < 2) {
      setSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const matches = await api.searchLocalities(q);
        setSuggestions(matches.slice(0, 6));
      } catch (err) {
        setSuggestions([]);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [searchInput]);

  // Click outside listener for suggestions dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setShowSuggestions(false);
      onSearchSubmit(searchInput.trim());
    }
  };

  const handleSelectSuggestion = async (item: any) => {
    setShowSuggestions(false);
    setSearchInput('');
    if (item.id) {
      const found = cities.find(c => c.id === item.id) || item;
      onSelectCity(found);
    } else {
      // Resolve dynamic locality
      setResolving(true);
      try {
        const resolved = await api.resolveLocality(item.name);
        onSelectCity(resolved);
      } catch (e) {
        onSearchSubmit(item.name);
      } finally {
        setResolving(false);
      }
    }
  };

  const filteredCities = cities.filter(c => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'villages') return c.locality_type === 'village' || c.vibe_tags?.some(t => t.toLowerCase().includes('village'));
    if (activeFilter === 'hills') return c.locality_type === 'hill_station' || c.vibe_tags?.some(t => t.toLowerCase().includes('hill') || t.toLowerCase().includes('mountain') || t.toLowerCase().includes('altitude'));
    if (activeFilter === 'coastal') return c.locality_type === 'coastal' || c.vibe_tags?.some(t => t.toLowerCase().includes('beach') || t.toLowerCase().includes('coastal'));
    if (activeFilter === 'heritage') return c.vibe_tags?.some(t => t.toLowerCase().includes('heritage') || t.toLowerCase().includes('temple') || t.toLowerCase().includes('palace') || t.toLowerCase().includes('monument'));
    return true;
  });

  const samplePrompts = [
    `What can I do in ${currentCity?.name || 'Shimla'} in one day under ₹1500?`,
    `Plan 8 hours starting from railway station with historical sights`,
    `Discover living root bridges and eco-trails in Mawlynnong village`,
    `Top spiritual ghats and sunrise boat cruise in Varanasi`,
  ];

  return (
    <div className="relative overflow-hidden pt-8 pb-12 px-4 sm:px-6 lg:px-8 border-b border-slate-800/80 bg-gradient-to-b from-slate-900/60 to-slate-950">
      {/* Background glowing effects */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[650px] h-[300px] bg-gradient-to-r from-indigo-600/15 via-emerald-500/10 to-amber-500/10 blur-3xl -z-10 pointer-events-none" />

      <div className="max-w-4xl mx-auto text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-5">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Pan-India Intelligence: Search Any Indian City, State, Town or Village</span>
        </div>

        {/* Title */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white mb-4">
          Discover all of India.{' '}
          <span className="bg-gradient-to-r from-indigo-400 via-sky-300 to-emerald-400 bg-clip-text text-transparent">
            Plan smarter.
          </span>{' '}
          Travel deeper.
        </h1>

        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto mb-8 font-normal leading-relaxed">
          Search any city, heritage town, or scenic village in India. AI cross-references verified knowledge, 
          optimizes budgets, timings, and routes to craft your personalized itinerary.
        </p>

        {/* Search Omnibox */}
        <div ref={dropdownRef} className="max-w-2xl mx-auto relative mb-6">
          <form onSubmit={handleSearch} className="relative flex items-center">
            <Search className="w-5 h-5 text-indigo-400 absolute left-4 pointer-events-none" />
            <input
              type="text"
              value={searchInput}
              onFocus={() => setShowSuggestions(true)}
              onChange={(e) => {
                setSearchInput(e.target.value);
                setShowSuggestions(true);
              }}
              placeholder="Search any Indian city, state, or village (e.g. Varanasi, Chitkul, Jaipur, Goa)..."
              className="w-full bg-slate-900/90 border border-slate-700/80 focus:border-indigo-500 text-white placeholder-slate-400 text-sm rounded-2xl py-3.5 pl-12 pr-28 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all shadow-inner"
            />
            <button
              type="submit"
              disabled={resolving}
              className="absolute right-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              {resolving ? (
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <span>Explore</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>

          {/* Autocomplete Dropdown */}
          {showSuggestions && (suggestions.length > 0 || searchInput.trim().length >= 2) && (
            <div className="absolute left-0 right-0 top-full mt-2 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden z-50 text-left">
              <div className="p-2 border-b border-slate-800 text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                <span>Pan-India Matches</span>
                <span className="text-[10px] text-emerald-400">All 28 States & Villages</span>
              </div>
              <div className="max-h-60 overflow-y-auto divide-y divide-slate-800/50">
                {suggestions.map((s, idx) => (
                  <div
                    key={idx}
                    onClick={() => handleSelectSuggestion(s)}
                    className="p-3 hover:bg-slate-800/80 cursor-pointer flex items-center justify-between transition-colors group"
                  >
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 group-hover:bg-indigo-500 group-hover:text-white transition-colors">
                        <MapPin className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="font-bold text-white text-xs block group-hover:text-indigo-300">
                          {s.name}
                        </span>
                        <span className="text-[11px] text-slate-400">
                          {s.district ? `${s.district}, ` : ''}{s.state}, India
                        </span>
                      </div>
                    </div>
                    <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                      {s.locality_type || 'City'}
                    </span>
                  </div>
                ))}
                {searchInput.trim().length >= 2 && !suggestions.some(s => s.name?.toLowerCase() === searchInput.trim().toLowerCase()) && (
                  <div
                    onClick={() => handleSelectSuggestion({ name: searchInput.trim() })}
                    className="p-3 hover:bg-indigo-600/20 cursor-pointer flex items-center gap-2 text-indigo-300 transition-colors"
                  >
                    <Sparkles className="w-4 h-4 text-amber-400" />
                    <span className="text-xs font-semibold">
                      Discover & auto-seed &ldquo;{searchInput.trim()}&rdquo; (Any Indian Village / City)
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Region & Destination Filter Tabs */}
        <div className="flex flex-wrap items-center justify-center gap-1.5 mb-4 text-xs">
          {[
            { id: 'all', label: 'All Destinations' },
            { id: 'heritage', label: '🏛️ Heritage Capitals' },
            { id: 'hills', label: '🏔️ Hill Stations' },
            { id: 'villages', label: '🌾 Rural & Border Villages' },
            { id: 'coastal', label: '🏖️ Coastal & Beaches' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveFilter(tab.id as any)}
              className={`px-3 py-1.5 rounded-xl font-semibold text-xs transition-all ${
                activeFilter === tab.id
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'bg-slate-900/60 hover:bg-slate-850 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Destination Pills */}
        <div className="flex flex-wrap items-center justify-center gap-2 text-xs mb-8 max-w-3xl mx-auto">
          {filteredCities.slice(0, 14).map((city) => (
            <button
              key={city.id}
              onClick={() => onSelectCity(city)}
              className={`px-3.5 py-1.5 rounded-full border transition-all flex items-center gap-1.5 ${
                currentCity?.id === city.id
                  ? 'bg-indigo-600 border-indigo-400 text-white font-bold shadow-md shadow-indigo-600/30'
                  : 'bg-slate-900/80 border-slate-800 hover:border-indigo-500/50 text-slate-300 hover:text-white'
              }`}
            >
              <span>{city.name}</span>
              <span className="text-[10px] text-slate-400 font-normal">({city.state})</span>
              {city.locality_type === 'village' && (
                <span className="text-[9px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.2 rounded-full font-bold">
                  Village
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-3 mb-8">
          <button
            onClick={onExploreClick}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-3 rounded-xl shadow-lg shadow-indigo-600/25 transition-all hover:scale-105 text-sm"
          >
            <Compass className="w-4 h-4" />
            Explore {currentCity?.name || 'City'}
          </button>
          <button
            onClick={() => onTriggerPrompt(`What can I do in ${currentCity?.name || 'Shimla'} in one day under ₹1500?`)}
            className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 font-semibold px-6 py-3 rounded-xl transition-all hover:scale-105 text-sm"
          >
            <Bot className="w-4 h-4 text-emerald-400" />
            Ask AI Assistant
          </button>
        </div>

        {/* Quick prompt chips */}
        <div className="flex flex-wrap justify-center gap-2 max-w-3xl mx-auto">
          {samplePrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => onTriggerPrompt(prompt)}
              className="text-xs bg-slate-900/70 hover:bg-slate-850 border border-slate-800 hover:border-indigo-500/50 text-slate-300 hover:text-white px-3 py-1.5 rounded-lg text-left transition-all flex items-center gap-1.5"
            >
              <Sparkles className="w-3 h-3 text-amber-400 shrink-0" />
              <span className="truncate max-w-xs">{prompt}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
