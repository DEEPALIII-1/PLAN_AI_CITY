import React, { useState } from 'react';
import { 
  Sparkles, Clock, IndianRupee, MapPin, Footprints, Car, 
  Calendar, ShieldCheck, Bookmark, CheckCircle2, AlertCircle, ArrowRight
} from 'lucide-react';
import { City, ItineraryPlan } from '../types';
import { api } from '../services/api';

interface TripPlannerViewProps {
  currentCity: City | null;
  onViewOnMap?: (places: any[]) => void;
  onAskAIQuestion?: (q: string) => void;
}

export const TripPlannerView: React.FC<TripPlannerViewProps> = ({
  currentCity,
  onAskAIQuestion,
}) => {
  const [budget, setBudget] = useState<number>(2000);
  const [availableHours, setAvailableHours] = useState<number>(8);
  const [startTime, setStartTime] = useState<string>('09:00');
  const [startLocation, setStartLocation] = useState<string>(`${currentCity?.name || 'Shimla'} Railway Station`);
  const [selectedInterests, setSelectedInterests] = useState<string[]>(['cafes', 'historical']);
  const [pace, setPace] = useState<'relaxed' | 'medium' | 'packed'>('medium');
  const [groupSize, setGroupSize] = useState<number>(1);
  const [transportMode, setTransportMode] = useState<string>('walk_cab');

  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState<ItineraryPlan | null>(null);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const interestOptions = [
    { id: 'cafes', label: '☕ Cozy Cafés' },
    { id: 'historical', label: '🏛️ Historical Sites' },
    { id: 'nature', label: '🌲 Scenic Viewpoints' },
    { id: 'food', label: '🍴 Authentic Food' },
    { id: 'shopping', label: '🛍️ Local Bazaars' },
  ];

  const toggleInterest = (id: string) => {
    if (selectedInterests.includes(id)) {
      if (selectedInterests.length > 1) {
        setSelectedInterests(selectedInterests.filter(i => i !== id));
      }
    } else {
      setSelectedInterests([...selectedInterests, id]);
    }
  };

  const handleGeneratePlan = async () => {
    if (!currentCity) return;
    setLoading(true);
    setSavedSuccess(false);
    try {
      const result = await api.planItinerary({
        city_id: currentCity.id,
        budget,
        available_hours: availableHours,
        start_time: startTime,
        start_location: startLocation,
        interests: selectedInterests,
        pace,
        group_size: groupSize,
      });
      setPlan(result);
    } catch (err) {
      console.error(err);
      alert('Could not generate plan. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveItinerary = async () => {
    if (!plan || !currentCity) return;
    try {
      await api.saveItinerary({
        title: plan.title,
        city_id: currentCity.id,
        total_budget: plan.total_budget,
        estimated_cost: plan.estimated_cost,
        duration_hours: plan.duration_hours,
        start_location: plan.start_location,
        interests: selectedInterests,
        pace: plan.pace,
        group_size: plan.group_size,
        itinerary_json: plan,
        ai_reasoning: plan.ai_reasoning,
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3500);
    } catch (err: any) {
      alert(err.message || 'Please sign in to save itineraries to your profile.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Title */}
      <div className="mb-8 max-w-3xl">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-semibold mb-3">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Constraint-Satisfaction AI Engine</span>
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white mb-2">
          Intelligent AI Trip Planner
        </h2>
        <p className="text-slate-400 text-sm sm:text-base">
          Enter your constraints (budget, available time, starting point, and tastes). 
          Our multi-agent optimizer models your schedule, routes, and meals without back-tracking.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Form: Constraints Inputs */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-7 shadow-xl">
          <h3 className="text-base font-bold text-white mb-5 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
            Set Your Constraints
          </h3>

          <div className="space-y-6 text-xs">
            {/* Start Location & Time */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-slate-300 font-semibold block mb-1.5 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-indigo-400" />
                  Starting Point:
                </label>
                <input
                  type="text"
                  value={startLocation}
                  onChange={(e) => setStartLocation(e.target.value)}
                  placeholder="e.g. Railway Station"
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-slate-300 font-semibold block mb-1.5 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-indigo-400" />
                  Departure Time:
                </label>
                <input
                  type="time"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            {/* Budget Slider */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-slate-300 font-semibold flex items-center gap-1.5">
                  <IndianRupee className="w-3.5 h-3.5 text-emerald-400" />
                  Total Budget:
                </label>
                <span className="text-sm font-extrabold text-white bg-slate-800 px-3 py-1 rounded-lg">
                  ₹{budget.toLocaleString()}
                </span>
              </div>
              <input
                type="range"
                min="500"
                max="8000"
                step="250"
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                className="w-full accent-indigo-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                <span>Budget (₹500)</span>
                <span>Standard (₹2,500)</span>
                <span>Luxury (₹8,000)</span>
              </div>
            </div>

            {/* Available Hours Slider */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-slate-300 font-semibold flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-amber-400" />
                  Available Time:
                </label>
                <span className="text-sm font-extrabold text-white bg-slate-800 px-3 py-1 rounded-lg">
                  {availableHours} Hours
                </span>
              </div>
              <input
                type="range"
                min="3"
                max="12"
                step="1"
                value={availableHours}
                onChange={(e) => setAvailableHours(Number(e.target.value))}
                className="w-full accent-indigo-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                <span>Quick Tour (3h)</span>
                <span>Full Day (8h)</span>
                <span>Extended (12h)</span>
              </div>
            </div>

            {/* Interests Chips */}
            <div>
              <label className="text-slate-300 font-semibold block mb-2">
                What interests you? (Select 1 or more)
              </label>
              <div className="flex flex-wrap gap-2">
                {interestOptions.map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => toggleInterest(opt.id)}
                    className={`px-3 py-2 rounded-xl text-xs font-semibold transition-all ${
                      selectedInterests.includes(opt.id)
                        ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                        : 'bg-slate-800 text-slate-400 border border-slate-700 hover:text-white'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Pacing & Travelers */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-slate-300 font-semibold block mb-1.5">Pacing:</label>
                <div className="grid grid-cols-3 gap-1 bg-slate-800 p-1 rounded-xl">
                  {(['relaxed', 'medium', 'packed'] as const).map((p) => (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setPace(p)}
                      className={`capitalize py-1.5 rounded-lg text-[11px] font-bold transition-all ${
                        pace === p ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-slate-300 font-semibold block mb-1.5">Travelers:</label>
                <div className="flex items-center bg-slate-800 border border-slate-700 rounded-xl px-2 py-1">
                  <button
                    type="button"
                    onClick={() => setGroupSize(Math.max(1, groupSize - 1))}
                    className="w-7 h-7 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-bold"
                  >
                    -
                  </button>
                  <span className="flex-1 text-center font-bold text-white text-xs">
                    {groupSize} {groupSize === 1 ? 'Person' : 'People'}
                  </span>
                  <button
                    type="button"
                    onClick={() => setGroupSize(Math.min(6, groupSize + 1))}
                    className="w-7 h-7 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-bold"
                  >
                    +
                  </button>
                </div>
              </div>
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGeneratePlan}
              disabled={loading}
              className="w-full bg-gradient-to-r from-indigo-600 via-indigo-500 to-emerald-500 hover:from-indigo-500 hover:to-emerald-400 text-white font-bold py-3.5 rounded-2xl shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition-all hover:scale-[1.01] disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4 text-amber-300" />
              <span>{loading ? 'Optimizing Route & Budget...' : 'Generate Optimized Plan'}</span>
            </button>
          </div>
        </div>

        {/* Right Output: Schedule & Budget Breakdown */}
        <div className="lg:col-span-7">
          {!plan && !loading && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-10 text-center flex flex-col items-center justify-center min-h-[440px]">
              <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
                <Clock className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Ready to plan your day</h3>
              <p className="text-sm text-slate-400 max-w-md mb-6">
                Adjust your budget and preferences on the left and click "Generate Optimized Plan" 
                to see your time-blocked sequence.
              </p>
              <button
                onClick={handleGeneratePlan}
                className="text-xs font-semibold bg-indigo-600 text-white px-5 py-2.5 rounded-xl hover:bg-indigo-500 transition-colors shadow-md shadow-indigo-600/20"
              >
                Try Example: ₹2,000 in {currentCity?.name || 'Shimla'}
              </button>
            </div>
          )}

          {loading && (
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-12 text-center min-h-[440px] flex flex-col items-center justify-center">
              <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4" />
              <h4 className="text-lg font-bold text-white mb-1">Planning Agent At Work</h4>
              <p className="text-xs text-slate-400 max-w-sm">
                Calculating shortest-sequence geographical routes, matching opening hours, 
                and verifying meal budgets...
              </p>
            </div>
          )}

          {plan && !loading && (
            <div className="space-y-6">
              {/* Plan Header Card */}
              <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl">
                <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 rounded-full">
                      ✓ AI Optimization Complete
                    </span>
                    <h3 className="text-2xl font-extrabold text-white mt-1.5">{plan.title}</h3>
                    <p className="text-xs text-slate-400 mt-0.5">{plan.summary}</p>
                  </div>

                  <button
                    onClick={handleSaveItinerary}
                    className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-4 py-2 rounded-xl border border-slate-700 transition-all"
                  >
                    <Bookmark className="w-3.5 h-3.5 text-indigo-400" />
                    <span>{savedSuccess ? 'Saved to Profile!' : 'Save Plan'}</span>
                  </button>
                </div>

                {/* Budget Meters */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-slate-800 text-xs">
                  <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                    <span className="text-slate-400 block mb-0.5">Budget Allocated</span>
                    <span className="text-base font-extrabold text-white">₹{plan.total_budget}</span>
                  </div>
                  <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                    <span className="text-slate-400 block mb-0.5">Estimated Cost</span>
                    <span className="text-base font-extrabold text-emerald-400">₹{plan.estimated_cost}</span>
                  </div>
                  <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                    <span className="text-slate-400 block mb-0.5">Savings Buffer</span>
                    <span className="text-base font-extrabold text-indigo-300">
                      ₹{Math.max(0, plan.total_budget - plan.estimated_cost)}
                    </span>
                  </div>
                  <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                    <span className="text-slate-400 block mb-0.5">Stops Covered</span>
                    <span className="text-base font-extrabold text-amber-300">{plan.stops.length} Places</span>
                  </div>
                </div>
              </div>

              {/* Sequential Timeline */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 px-1">
                  Sequential Time-Blocked Itinerary
                </h4>

                {plan.stops.map((stop, idx) => (
                  <div key={idx} className="relative">
                    {/* Transit indicator between stops */}
                    {idx > 0 && (
                      <div className="flex items-center gap-2 pl-7 py-1 text-[11px] text-slate-400">
                        <div className="w-1.5 h-6 border-l-2 border-dashed border-indigo-500/40 -my-1" />
                        <span className="bg-slate-900 border border-slate-800 px-2.5 py-0.5 rounded-full flex items-center gap-1.5 text-indigo-300">
                          {stop.travel_mode === 'Walking' ? (
                            <Footprints className="w-3 h-3 text-emerald-400" />
                          ) : (
                            <Car className="w-3 h-3 text-indigo-400" />
                          )}
                          <span>Transit: {stop.travel_mode} (~{stop.travel_from_prev_mins} mins)</span>
                        </span>
                      </div>
                    )}

                    {/* Place card */}
                    <div className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 transition-all">
                      <div className="flex items-start gap-4">
                        <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-extrabold flex items-center justify-center shrink-0 text-sm">
                          {stop.step_number}
                        </div>

                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-md">
                              {stop.time_slot}
                            </span>
                            <span className="text-xs text-slate-400">• {stop.category}</span>
                          </div>

                          <h5 className="text-base font-bold text-white mb-1">
                            {stop.place_name}
                          </h5>
                          <p className="text-xs text-slate-300 mb-2 leading-relaxed">
                            {stop.description}
                          </p>

                          <div className="flex flex-wrap items-center gap-3 text-[11px] text-slate-400">
                            <span className="text-emerald-400 font-semibold">
                              Est. {stop.estimated_cost === 0 ? 'Free' : `₹${stop.estimated_cost}`}
                            </span>
                            <span>•</span>
                            <span>Duration: ~{stop.duration_mins} mins</span>
                            <span>•</span>
                            <span className="text-slate-400">{stop.address}</span>
                          </div>

                          {/* AI tip */}
                          <div className="mt-2 text-[11px] text-indigo-300 bg-indigo-950/40 border border-indigo-900/60 px-2.5 py-1 rounded-lg">
                            💡 {stop.ai_tips}
                          </div>
                        </div>
                      </div>

                      {/* Ask AI CTA */}
                      <button
                        onClick={() => onAskAIQuestion && onAskAIQuestion(`Tell me more about ${stop.place_name} in ${plan.city_name}`)}
                        className="text-[11px] font-semibold text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-xl border border-slate-700 transition-colors shrink-0"
                      >
                        Ask AI Details
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* AI Reasoning & Advisories Card */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 text-xs">
                  <h5 className="font-bold text-white mb-1.5 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                    AI Routing Reasoning:
                  </h5>
                  <p className="text-slate-300 leading-relaxed">
                    {plan.ai_reasoning}
                  </p>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 text-xs">
                  <h5 className="font-bold text-white mb-1.5 flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                    Weather & Crowd Advice:
                  </h5>
                  <p className="text-slate-300 leading-relaxed mb-1">
                    <strong className="text-white">Weather:</strong> {plan.weather_advice}
                  </p>
                  <p className="text-slate-300 leading-relaxed">
                    <strong className="text-white">Crowd & Timing:</strong> {plan.crowd_season_tips}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
