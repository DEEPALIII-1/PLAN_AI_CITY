import React, { useState } from 'react';
import { 
  Landmark, Coffee, Utensils, ShoppingBag, Trees, Building2, Calendar, 
  Train, Compass, Cross, Star, Clock, IndianRupee, ShieldCheck, Plus, 
  Search, X, CheckCircle, Sparkles
} from 'lucide-react';
import { City, Category, Place } from '../types';
import { api } from '../services/api';

interface ExploreViewProps {
  currentCity: City | null;
  categories: Category[];
  places: Place[];
  selectedCategory: string | null;
  onSelectCategory: (slug: string | null) => void;
  onAskAIAboutPlace: (placeName: string) => void;
  onAddPlaceToPlanner: (place: Place) => void;
  onPlaceCreated?: (newPlace: Place) => void;
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
}

export const ExploreView: React.FC<ExploreViewProps> = ({
  currentCity,
  categories,
  places,
  selectedCategory,
  onSelectCategory,
  onAskAIAboutPlace,
  onAddPlaceToPlanner,
  onPlaceCreated,
  searchQuery = '',
  onSearchChange,
}) => {
  const [localSearch, setLocalSearch] = useState(searchQuery);
  const [maxBudget, setMaxBudget] = useState<number>(2000);
  const [childFriendlyOnly, setChildFriendlyOnly] = useState(false);
  const [popularOnly, setPopularOnly] = useState(false);

  // Add Place Modal State
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [newName, setNewName] = useState('');
  const [newCatId, setNewCatId] = useState<number>(categories[0]?.id || 1);
  const [newDesc, setNewDesc] = useState('');
  const [newAddress, setNewAddress] = useState('');
  const [newCost, setNewCost] = useState<number>(300);
  const [newDuration, setNewDuration] = useState<number>(60);
  const [newChildFriendly, setNewChildFriendly] = useState(true);
  const [newTags, setNewTags] = useState('local, scenic, recommended');
  const [newImageUrl, setNewImageUrl] = useState('');
  const [creating, setCreating] = useState(false);
  const [createSuccess, setCreateSuccess] = useState(false);

  const getCategoryIcon = (iconName: string) => {
    switch (iconName?.toLowerCase()) {
      case 'landmark': return <Landmark className="w-4 h-4" />;
      case 'coffee': return <Coffee className="w-4 h-4" />;
      case 'utensils': return <Utensils className="w-4 h-4" />;
      case 'shoppingbag': return <ShoppingBag className="w-4 h-4" />;
      case 'trees': return <Trees className="w-4 h-4" />;
      case 'building2': return <Building2 className="w-4 h-4" />;
      case 'calendar': return <Calendar className="w-4 h-4" />;
      case 'train': return <Train className="w-4 h-4" />;
      case 'cross': return <Cross className="w-4 h-4" />;
      default: return <Compass className="w-4 h-4" />;
    }
  };

  const handleSearchInput = (val: string) => {
    setLocalSearch(val);
    if (onSearchChange) onSearchChange(val);
  };

  const filteredPlaces = places.filter((p) => {
    // 1. Text Search Filter (name, description, address, tags)
    const q = localSearch.trim().toLowerCase();
    if (q) {
      const matchName = p.name.toLowerCase().includes(q);
      const matchDesc = p.description.toLowerCase().includes(q);
      const matchAddr = p.address.toLowerCase().includes(q);
      const matchTags = (p.tags || []).some(t => t.toLowerCase().includes(q));
      const matchCat = (p.category_name || '').toLowerCase().includes(q);
      if (!matchName && !matchDesc && !matchAddr && !matchTags && !matchCat) {
        return false;
      }
    }

    // 2. Category Filter
    if (selectedCategory && p.category_name?.toLowerCase() !== selectedCategory.toLowerCase()) {
      const cat = categories.find(c => c.slug === selectedCategory);
      if (cat && p.category_name !== cat.name) return false;
    }

    // 3. Constraints Filters
    if (p.estimated_cost > maxBudget) return false;
    if (childFriendlyOnly && !p.child_friendly) return false;
    if (popularOnly && !p.is_popular && p.rating < 4.7) return false;
    return true;
  });

  const handleCreatePlaceSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentCity || !newName.trim()) return;

    setCreating(true);
    try {
      const tagsArray = newTags.split(',').map(t => t.trim()).filter(Boolean);
      const created = await api.createPlace({
        city_id: currentCity.id,
        category_id: Number(newCatId),
        name: newName.trim(),
        description: newDesc.trim() || `Popular local spot in ${currentCity.name}.`,
        address: newAddress.trim() || `${newName}, ${currentCity.name}`,
        estimated_cost: Number(newCost),
        avg_visit_duration_mins: Number(newDuration),
        child_friendly: newChildFriendly,
        tags: tagsArray,
        images: newImageUrl.trim() ? [newImageUrl.trim()] : [
          "https://images.unsplash.com/photo-1597074866923-dc0589150358?auto=format&fit=crop&w=600&q=70"
        ],
        rating: 4.8,
        price_level: newCost <= 300 ? 1 : newCost <= 1000 ? 2 : 3,
        is_popular: true,
      });

      if (onPlaceCreated) onPlaceCreated(created);
      setCreateSuccess(true);
      setTimeout(() => {
        setCreateSuccess(false);
        setIsAddModalOpen(false);
        // Reset form
        setNewName('');
        setNewDesc('');
        setNewAddress('');
        setNewCost(300);
      }, 1500);
    } catch (err: any) {
      alert(err.message || 'Failed to create place');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* City Overview Hero Card */}
      {currentCity && (
        <div className="relative rounded-3xl overflow-hidden mb-8 border border-slate-800 bg-slate-900 shadow-2xl">
          <div className="absolute inset-0">
            {currentCity.hero_image && (
              <img 
                src={currentCity.hero_image} 
                alt={currentCity.name}
                className="w-full h-full object-cover opacity-25 filter blur-[1px]"
              />
            )}
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/80 to-transparent" />
          </div>

          <div className="relative p-6 sm:p-8 lg:p-10 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-0.5 rounded-full">
                {currentCity.locality_type === 'village' ? '🌾 Scenic Village' : currentCity.locality_type === 'coastal' ? '🏖️ Coastal Destination' : '📍 ' + (currentCity.locality_type ? currentCity.locality_type.toUpperCase() : 'CITY')}
              </span>
              <span className="text-xs font-bold text-indigo-300 bg-indigo-500/10 border border-indigo-500/20 px-2.5 py-0.5 rounded-full">
                {currentCity.state}, India
              </span>
              {currentCity.vibe_tags.map((tag, i) => (
                <span key={i} className="text-xs bg-slate-800/80 text-slate-300 px-2.5 py-0.5 rounded-full border border-slate-700">
                  {tag}
                </span>
              ))}
            </div>

            <h2 className="text-3xl sm:text-4xl font-extrabold text-white mb-3">
              Discover {currentCity.name}
            </h2>
            <p className="text-slate-300 text-sm sm:text-base leading-relaxed mb-6">
              {currentCity.description}
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-4 border-t border-slate-800/80 text-xs">
              <div>
                <span className="text-slate-400 block mb-0.5">Best Season:</span>
                <span className="text-white font-medium">{currentCity.best_time_to_visit || 'Year-round'}</span>
              </div>
              <div>
                <span className="text-slate-400 block mb-0.5">Current Climate:</span>
                <span className="text-white font-medium">{currentCity.weather_summary || 'Pleasant'}</span>
              </div>
              <div className="col-span-2 sm:col-span-1">
                <span className="text-slate-400 block mb-0.5">Verified Intelligence:</span>
                <span className="text-emerald-400 font-semibold flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" /> 100% RAG Grounded
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search & Add Your Own Place Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 mb-6">
        {/* Real-time Search Input */}
        <div className="relative flex-1 max-w-xl">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={localSearch}
            onChange={(e) => handleSearchInput(e.target.value)}
            placeholder={`Search ${currentCity?.name || 'city'} places, cafés, restaurants, monuments, or tags...`}
            className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-2xl pl-10 pr-10 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-all shadow-inner"
          />
          {localSearch && (
            <button
              onClick={() => handleSearchInput('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Add Your Own Place Button */}
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white text-xs font-bold px-4 py-2.5 rounded-2xl shadow-md shadow-emerald-600/20 transition-all hover:scale-105 shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>+ Add Your Own Place</span>
        </button>
      </div>

      {/* Category Pills Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-base font-bold text-white tracking-wide uppercase text-xs text-slate-400">
            Categories in {currentCity?.name}
          </h3>
          {(selectedCategory || localSearch) && (
            <button 
              onClick={() => {
                onSelectCategory(null);
                handleSearchInput('');
              }}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
            >
              Clear Filters
            </button>
          )}
        </div>
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          <button
            onClick={() => onSelectCategory(null)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              selectedCategory === null
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/25'
                : 'bg-slate-900 text-slate-300 border border-slate-800 hover:border-slate-700'
            }`}
          >
            <Compass className="w-4 h-4" />
            All Places ({places.length})
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => onSelectCategory(cat.slug)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                selectedCategory === cat.slug
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/25'
                  : 'bg-slate-900 text-slate-300 border border-slate-800 hover:border-slate-700'
              }`}
            >
              {getCategoryIcon(cat.icon)}
              {cat.name}
            </button>
          ))}
        </div>
      </div>

      {/* Interactive Filters Bar */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 mb-8 flex flex-wrap items-center justify-between gap-4 text-xs">
        <div className="flex items-center gap-6">
          {/* Budget slider */}
          <div className="flex items-center gap-3">
            <span className="text-slate-400 font-medium">Max Cost:</span>
            <input 
              type="range" 
              min="0" 
              max="2500" 
              step="100"
              value={maxBudget}
              onChange={(e) => setMaxBudget(Number(e.target.value))}
              className="w-28 sm:w-36 accent-indigo-500 cursor-pointer"
            />
            <span className="font-bold text-white bg-slate-800 px-2 py-1 rounded-md">
              ₹{maxBudget}
            </span>
          </div>

          {/* Child friendly toggle */}
          <label className="flex items-center gap-2 cursor-pointer text-slate-300">
            <input 
              type="checkbox"
              checked={childFriendlyOnly}
              onChange={(e) => setChildFriendlyOnly(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0 w-3.5 h-3.5"
            />
            <span>Child Friendly</span>
          </label>

          {/* Popular toggle */}
          <label className="flex items-center gap-2 cursor-pointer text-slate-300">
            <input 
              type="checkbox"
              checked={popularOnly}
              onChange={(e) => setPopularOnly(e.target.checked)}
              className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0 w-3.5 h-3.5"
            />
            <span>Top Rated (4.7+)</span>
          </label>
        </div>

        <div className="text-slate-400">
          Showing <span className="text-white font-bold">{filteredPlaces.length}</span> of {places.length} places
        </div>
      </div>

      {/* Places Grid */}
      {filteredPlaces.length === 0 ? (
        <div className="text-center py-16 bg-slate-900/40 rounded-3xl border border-slate-800/80">
          <Compass className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h4 className="text-lg font-bold text-white mb-1">No matching places found</h4>
          <p className="text-sm text-slate-400 max-w-md mx-auto mb-4">
            Try searching with a different term, adjusting your budget, or add this place to the city!
          </p>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-4 py-2 rounded-xl transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Add "{localSearch}" to {currentCity?.name}</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPlaces.map((place) => (
            <div 
              key={place.id}
              className="bg-slate-900 border border-slate-800/90 hover:border-indigo-500/50 rounded-2xl overflow-hidden flex flex-col group transition-all duration-300 hover:shadow-xl hover:shadow-indigo-500/10"
            >
              {/* Place Card Image Header */}
              <div className="relative h-48 overflow-hidden bg-slate-800">
                <img 
                  src={place.images[0] || 'https://images.unsplash.com/photo-1597074866923-dc0589150358?auto=format&fit=crop&w=600&q=70'}
                  alt={place.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent" />
                
                {/* Category Badge */}
                <div className="absolute top-3 left-3 bg-slate-950/80 backdrop-blur-md text-slate-200 text-[11px] font-bold px-2.5 py-1 rounded-full border border-slate-700/60">
                  {place.category_name}
                </div>

                {/* Rating Badge */}
                <div className="absolute top-3 right-3 flex items-center gap-1 bg-amber-500/90 text-slate-950 text-xs font-black px-2 py-0.5 rounded-full shadow-md">
                  <Star className="w-3 h-3 fill-slate-950" />
                  <span>{place.rating}</span>
                </div>

                {/* Price Indicator */}
                <div className="absolute bottom-3 left-3 flex items-center gap-1 text-white font-bold text-sm bg-slate-950/85 backdrop-blur-sm px-2.5 py-1 rounded-lg">
                  <IndianRupee className="w-3.5 h-3.5 text-emerald-400" />
                  <span>{place.estimated_cost === 0 ? 'Free Entry' : `₹${place.estimated_cost}`}</span>
                </div>
              </div>

              {/* Content Body */}
              <div className="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <h4 className="text-base font-bold text-white group-hover:text-indigo-300 transition-colors mb-1.5">
                    {place.name}
                  </h4>
                  <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-3">
                    {place.description}
                  </p>

                  <div className="flex items-center gap-4 text-xs text-slate-400 mb-3">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-slate-500" />
                      ~{place.avg_visit_duration_mins} mins
                    </span>
                    <span>•</span>
                    <span>{place.opening_time} - {place.closing_time}</span>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {place.tags.slice(0, 3).map((tag, idx) => (
                      <span key={idx} className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded-md">
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Bottom Actions */}
                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
                  <button
                    onClick={() => onAskAIAboutPlace(place.name)}
                    className="flex-1 text-xs font-semibold bg-slate-800/90 hover:bg-slate-800 text-indigo-300 hover:text-white py-2 rounded-xl border border-slate-700 transition-colors text-center"
                  >
                    Ask AI Details
                  </button>
                  <button
                    onClick={() => onAddPlaceToPlanner(place)}
                    className="text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-2 rounded-xl transition-colors"
                    title="Add to Itinerary Planner"
                  >
                    + Plan
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Your Own Place Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-7 shadow-2xl max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setIsAddModalOpen(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="mb-5">
              <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full uppercase">
                Add Place to {currentCity?.name}
              </span>
              <h3 className="text-xl font-extrabold text-white mt-2">
                Add Your Own Custom Place
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Add a local café, landmark, secret viewpoint, or authentic restaurant. It will immediately appear in searches and AI itinerary planning!
              </p>
            </div>

            {createSuccess ? (
              <div className="p-8 text-center bg-emerald-500/10 border border-emerald-500/20 rounded-2xl text-emerald-400">
                <CheckCircle className="w-12 h-12 mx-auto mb-2 text-emerald-400 animate-bounce" />
                <h4 className="text-base font-bold">Place Added Successfully!</h4>
                <p className="text-xs text-slate-300 mt-1">
                  Your place is now indexed in {currentCity?.name} and ready for AI itinerary generation.
                </p>
              </div>
            ) : (
              <form onSubmit={handleCreatePlaceSubmit} className="space-y-4 text-xs">
                <div>
                  <label className="text-slate-300 font-semibold block mb-1">Place Name *</label>
                  <input
                    type="text"
                    required
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    placeholder="e.g. Hilltop Deodar Roastery"
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-slate-300 font-semibold block mb-1">Category *</label>
                    <select
                      value={newCatId}
                      onChange={(e) => setNewCatId(Number(e.target.value))}
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500"
                    >
                      {categories.map((c) => (
                        <option key={c.id} value={c.id} className="bg-slate-900">
                          {c.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-slate-300 font-semibold block mb-1">Estimated Cost (₹) *</label>
                    <input
                      type="number"
                      required
                      min="0"
                      value={newCost}
                      onChange={(e) => setNewCost(Number(e.target.value))}
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-slate-300 font-semibold block mb-1">Description *</label>
                  <textarea
                    rows={2}
                    required
                    value={newDesc}
                    onChange={(e) => setNewDesc(e.target.value)}
                    placeholder="Describe what makes this place special, atmosphere, food, or views..."
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="text-slate-300 font-semibold block mb-1">Address / Landmark *</label>
                  <input
                    type="text"
                    required
                    value={newAddress}
                    onChange={(e) => setNewAddress(e.target.value)}
                    placeholder="e.g. Near Mall Road, Opp Town Hall"
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-slate-300 font-semibold block mb-1">Avg Visit Duration (mins)</label>
                    <input
                      type="number"
                      min="15"
                      step="15"
                      value={newDuration}
                      onChange={(e) => setNewDuration(Number(e.target.value))}
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2.5 focus:outline-none focus:border-indigo-500"
                    />
                  </div>

                  <div className="flex items-center pt-5">
                    <label className="flex items-center gap-2 cursor-pointer text-slate-300 font-medium">
                      <input
                        type="checkbox"
                        checked={newChildFriendly}
                        onChange={(e) => setNewChildFriendly(e.target.checked)}
                        className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0 w-4 h-4"
                      />
                      <span>Child Friendly</span>
                    </label>
                  </div>
                </div>

                <div>
                  <label className="text-slate-300 font-semibold block mb-1">Tags (comma separated)</label>
                  <input
                    type="text"
                    value={newTags}
                    onChange={(e) => setNewTags(e.target.value)}
                    placeholder="coffee, rooftop, sunset view, cozy"
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <button
                  type="submit"
                  disabled={creating}
                  className="w-full bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white font-bold py-3 rounded-2xl shadow-lg transition-all disabled:opacity-50 text-xs"
                >
                  {creating ? 'Saving Place to City...' : '+ Save and Index Place'}
                </button>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
