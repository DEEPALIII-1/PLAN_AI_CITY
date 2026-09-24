import React from 'react';
import { Compass, Sparkles, MapPin, BarChart3, Bot, User, Sun } from 'lucide-react';
import { City, UserProfile } from '../types';

interface NavbarProps {
  cities: City[];
  currentCity: City | null;
  onSelectCity: (city: City) => void;
  activeTab: 'explore' | 'planner' | 'chat' | 'analytics';
  onSelectTab: (tab: 'explore' | 'planner' | 'chat' | 'analytics') => void;
  profile: UserProfile | null;
  onOpenAuth: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  cities,
  currentCity,
  onSelectCity,
  activeTab,
  onSelectTab,
  profile,
  onOpenAuth,
}) => {
  return (
    <header className="sticky top-0 z-50 bg-slate-950/85 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & City Selector */}
          <div className="flex items-center gap-6">
            <div 
              onClick={() => onSelectTab('explore')}
              className="flex items-center gap-2 cursor-pointer group"
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
                <Compass className="w-6 h-6 text-white" />
              </div>
              <div>
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-300 bg-clip-text text-transparent">
                  PLAN AI CITY
                </span>
                <span className="hidden sm:inline-block text-[10px] text-indigo-400 font-semibold uppercase tracking-wider block">
                  City Intelligence
                </span>
              </div>
            </div>

            {/* City Switcher */}
            {cities.length > 0 && currentCity && (
              <div className="relative flex items-center bg-slate-900 border border-slate-800 rounded-full px-3 py-1.5 hover:border-slate-700 transition-colors">
                <MapPin className="w-3.5 h-3.5 text-emerald-400 mr-2" />
                <select
                  value={currentCity.id}
                  onChange={(e) => {
                    const found = cities.find(c => c.id === Number(e.target.value));
                    if (found) onSelectCity(found);
                  }}
                  className="bg-transparent text-sm font-semibold text-white focus:outline-none cursor-pointer pr-4"
                >
                  {cities.map(c => (
                    <option key={c.id} value={c.id} className="bg-slate-900 text-white">
                      {c.name}, {c.state} {c.locality_type === 'village' ? '🌾 (Village)' : ''}
                    </option>
                  ))}
                </select>
                {currentCity.weather_summary && (
                  <div className="hidden lg:flex items-center ml-2 pl-2 border-l border-slate-800 text-[11px] text-slate-400">
                    <Sun className="w-3 h-3 text-amber-400 mr-1" />
                    <span>{currentCity.weather_summary.split(',')[0]}</span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800/80">
            <button
              onClick={() => onSelectTab('explore')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'explore'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              <Compass className="w-3.5 h-3.5" />
              Explore City
            </button>
            <button
              onClick={() => onSelectTab('planner')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'planner'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              AI Trip Planner
            </button>
            <button
              onClick={() => onSelectTab('chat')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'chat'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              <Bot className="w-3.5 h-3.5 text-emerald-400" />
              RAG Assistant
            </button>
            <button
              onClick={() => onSelectTab('analytics')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'analytics'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5 text-indigo-400" />
              City Intelligence
            </button>
          </nav>

          {/* User Profile / Auth */}
          <div className="flex items-center gap-3">
            {profile ? (
              <button
                onClick={onOpenAuth}
                className="flex items-center gap-2.5 bg-slate-900 border border-slate-800 hover:border-slate-700 py-1.5 px-3 rounded-full text-xs font-medium text-slate-200 transition-colors"
              >
                <div className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold">
                  {profile.full_name ? profile.full_name[0] : 'U'}
                </div>
                <span className="hidden sm:inline font-semibold">{profile.full_name || profile.email}</span>
                {profile.preference?.budget_tier && (
                  <span className="text-[10px] bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-full font-semibold">
                    {profile.preference.travel_style || profile.preference.budget_tier}
                  </span>
                )}
              </button>
            ) : (
              <button
                onClick={onOpenAuth}
                className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white text-xs font-semibold px-4 py-2 rounded-full shadow-sm shadow-indigo-600/30 transition-all hover:scale-[1.02]"
              >
                <User className="w-3.5 h-3.5" />
                <span>Sign In</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
