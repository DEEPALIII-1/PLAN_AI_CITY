import React, { useEffect, useState } from 'react';
import { 
  BarChart3, Users, Compass, FileText, Search, IndianRupee, 
  TrendingUp, Award, Layers, Sparkles
} from 'lucide-react';
import { City, CityAnalytics } from '../types';
import { api } from '../services/api';

interface AnalyticsDashboardViewProps {
  currentCity: City | null;
}

export const AnalyticsDashboardView: React.FC<AnalyticsDashboardViewProps> = ({
  currentCity,
}) => {
  const [analytics, setAnalytics] = useState<CityAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, [currentCity]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      if (currentCity) {
        const data = await api.getCityAnalytics(currentCity.id);
        setAnalytics(data);
      } else {
        const data = await api.getOverviewAnalytics();
        setAnalytics(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-slate-400 text-sm">Aggregating city intelligence and ML analytics...</p>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center text-slate-400">
        Analytics unavailable.
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Title */}
      <div className="mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-3">
          <BarChart3 className="w-3.5 h-3.5" />
          <span>Real-time City Metrics & Machine Learning Models</span>
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white mb-2">
          {analytics.city_name} Intelligence Dashboard
        </h2>
        <p className="text-slate-400 text-sm">
          Live analytics across indexed places, visitor preferences, query frequencies, 
          and unsupervised K-Means user persona segmentation.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Total Places</span>
            <Compass className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-black text-white">{analytics.total_places}</div>
          <span className="text-[10px] text-emerald-400 font-semibold">Verified in DB</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">RAG Documents</span>
            <FileText className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-white">{analytics.total_documents}</div>
          <span className="text-[10px] text-slate-400">Official Knowledge</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">AI Itineraries</span>
            <Sparkles className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-white">{analytics.total_itineraries_generated}</div>
          <span className="text-[10px] text-indigo-300">Generated & Optimized</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Queries Analyzed</span>
            <Search className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-black text-white">{analytics.total_queries}</div>
          <span className="text-[10px] text-slate-400">Hybrid & RAG QA</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 col-span-2 sm:col-span-1">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold">Avg Plan Budget</span>
            <IndianRupee className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-black text-emerald-400">₹{analytics.avg_itinerary_budget}</div>
          <span className="text-[10px] text-slate-400">Per Day User Mean</span>
        </div>
      </div>

      {/* Charts & Breakdown Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-8">
        {/* Category Breakdown (7 cols) */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-400" />
            Category Distribution & Average Price
          </h3>

          <div className="space-y-4">
            {analytics.category_distribution.map((cat, idx) => {
              const maxCount = Math.max(...analytics.category_distribution.map(c => c.count), 1);
              const pct = (cat.count / maxCount) * 100;
              return (
                <div key={idx} className="text-xs">
                  <div className="flex items-center justify-between mb-1.5 font-medium">
                    <span className="text-white font-bold">{cat.category}</span>
                    <div className="text-slate-400 flex items-center gap-3">
                      <span>{cat.count} places</span>
                      <span className="text-emerald-400 font-semibold">Avg ₹{cat.avg_price}</span>
                    </div>
                  </div>
                  <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-indigo-600 to-emerald-400 rounded-full transition-all duration-700"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Price Tier Distribution (5 cols) */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-400" />
              Price Range Distribution
            </h3>

            <div className="space-y-4">
              {analytics.price_distribution.map((p, idx) => (
                <div key={idx} className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-bold text-white">{p.tier}</span>
                    <span className="font-extrabold text-emerald-400">{p.percentage}%</span>
                  </div>
                  <div className="text-[11px] text-slate-400 mb-2">
                    {p.place_count} places in this range
                  </div>
                  <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-emerald-500 rounded-full"
                      style={{ width: `${p.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-slate-800 text-[11px] text-slate-400 text-center">
            Calculated over active verified city entries.
          </div>
        </div>
      </div>

      {/* K-Means User Persona Clusters Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 mb-8 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="inline-flex items-center gap-2 text-xs font-bold text-amber-400 mb-1">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Machine Learning Component</span>
            </div>
            <h3 className="text-xl font-extrabold text-white">
              Unsupervised K-Means User Persona Clustering
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Learned clusters segmented from user budget thresholds, pacing preferences, and category affinity vectors.
            </p>
          </div>
          <div className="text-xs font-bold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-3 py-1.5 rounded-full hidden sm:block">
            k = 4 Personas
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {analytics.user_persona_clusters.map((cluster) => (
            <div 
              key={cluster.cluster_id}
              className="bg-slate-950/70 border border-slate-800 hover:border-indigo-500/40 rounded-2xl p-5 flex flex-col justify-between transition-all"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider bg-indigo-500/10 px-2 py-0.5 rounded-md">
                    Cluster {cluster.cluster_id}
                  </span>
                  <span className="text-xs font-black text-white bg-slate-800 px-2 py-0.5 rounded-full">
                    {cluster.percentage}%
                  </span>
                </div>

                <h4 className="text-sm font-bold text-white mb-2 leading-snug">
                  {cluster.persona_name}
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed mb-4">
                  {cluster.description}
                </p>
              </div>

              <div>
                <span className="text-[11px] font-semibold text-slate-300 block mb-1.5">
                  Key Algorithmic Traits:
                </span>
                <div className="flex flex-wrap gap-1">
                  {cluster.key_traits.map((trait, tIdx) => (
                    <span key={tIdx} className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded-md">
                      ✓ {trait}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Top Search Queries & Trending Places */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Queries */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <Search className="w-4 h-4 text-sky-400" />
            Top AI Search & RAG Queries
          </h4>
          <div className="space-y-2.5">
            {analytics.top_search_queries.map((q, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                <span className="text-slate-300 font-medium truncate max-w-xs sm:max-w-md">"{q.query}"</span>
                <span className="text-slate-500 font-bold ml-2 shrink-0">{q.count} queries</span>
              </div>
            ))}
          </div>
        </div>

        {/* Popular places */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <h4 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
            <Award className="w-4 h-4 text-amber-400" />
            Trending Places by Engagement
          </h4>
          <div className="space-y-2.5">
            {analytics.popular_places.map((place, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                <div>
                  <span className="font-bold text-white block">{place.name}</span>
                  <span className="text-[11px] text-slate-400">{place.category}</span>
                </div>
                <div className="text-right">
                  <span className="text-amber-400 font-extrabold block">★ {place.rating}</span>
                  <span className="text-[11px] text-slate-500">{place.reviews} reviews</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
