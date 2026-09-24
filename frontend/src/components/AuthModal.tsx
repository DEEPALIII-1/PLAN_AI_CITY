import React, { useState } from 'react';
import { 
  X, User, Lock, Mail, Sparkles, LogOut, CheckCircle, 
  Phone, MapPin, Eye, EyeOff, ShieldCheck, Calendar, UserCheck
} from 'lucide-react';
import { UserProfile } from '../types';
import { api } from '../services/api';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  profile: UserProfile | null;
  onProfileUpdated: (p: UserProfile | null) => void;
}

const POPULAR_STATES = [
  "Uttar Pradesh", "Himachal Pradesh", "Delhi NCR", "Rajasthan", "Maharashtra",
  "Karnataka", "Kerala", "Goa", "Uttarakhand", "Punjab", "West Bengal",
  "Tamil Nadu", "Gujarat", "Meghalaya", "Jammu and Kashmir", "Ladakh"
];

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  profile,
  onProfileUpdated,
}) => {
  const [activeMode, setActiveMode] = useState<'signin' | 'register'>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [fullName, setFullName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [homeCity, setHomeCity] = useState('');
  const [homeState, setHomeState] = useState('Uttar Pradesh');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Profile Edit state
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [editName, setEditName] = useState(profile?.full_name || profile?.profile?.full_name || '');
  const [editPhone, setEditPhone] = useState(profile?.profile?.phone_number || '');
  const [editCity, setEditCity] = useState(profile?.profile?.home_city || '');
  const [editState, setEditState] = useState(profile?.profile?.home_state || '');
  const [editBio, setEditBio] = useState(profile?.profile?.bio || '');

  // Preference state
  const [budgetTier, setBudgetTier] = useState(profile?.preference?.budget_tier || 'moderate');
  const [travelStyle, setTravelStyle] = useState(profile?.preference?.travel_style || 'solo');
  const [pace, setPace] = useState(profile?.preference?.preferred_pace || 'medium');
  const [savedSuccess, setSavedSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (activeMode === 'register') {
        await api.register(email, password, fullName, phoneNumber, homeCity, homeState);
      } else {
        await api.login(email, password);
      }
      const p = await api.getProfile();
      onProfileUpdated(p);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify details.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = async (demoEmail: string, demoPass: string) => {
    setError(null);
    setLoading(true);
    try {
      await api.login(demoEmail, demoPass);
      const p = await api.getProfile();
      onProfileUpdated(p);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Demo login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfileChanges = async () => {
    setLoading(true);
    try {
      const updated = await api.updateProfile({
        full_name: editName,
        phone_number: editPhone,
        home_city: editCity,
        home_state: editState,
        bio: editBio,
        budget_tier: budgetTier,
        travel_style: travelStyle,
        preferred_pace: pace,
      });
      onProfileUpdated(updated);
      setIsEditingProfile(false);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 2500);
    } catch (err: any) {
      setError(err.message || 'Update failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    api.logout();
    onProfileUpdated(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl max-h-[90vh] overflow-y-auto">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg"
        >
          <X className="w-5 h-5" />
        </button>

        {profile ? (
          /* Profile & Account Details View */
          <div>
            <div className="flex items-center gap-4 mb-6 pb-4 border-b border-slate-800">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-emerald-400 flex items-center justify-center text-white font-extrabold text-2xl shadow-lg shadow-indigo-600/30">
                {profile.full_name ? profile.full_name[0].toUpperCase() : 'U'}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-xl font-bold text-white">{profile.full_name || 'Traveler'}</h3>
                  <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-bold uppercase flex items-center gap-1">
                    <UserCheck className="w-3 h-3" />
                    Verified User
                  </span>
                </div>
                <span className="text-xs text-slate-400 block">{profile.email}</span>
                {profile.profile?.home_city && (
                  <span className="text-[11px] text-indigo-400 flex items-center gap-1 mt-0.5">
                    <MapPin className="w-3 h-3" />
                    {profile.profile.home_city}{profile.profile.home_state ? `, ${profile.profile.home_state}` : ''}
                  </span>
                )}
              </div>
            </div>

            {/* Profile Info Cards from user_profiles table */}
            <div className="grid grid-cols-2 gap-3 mb-5">
              <div className="bg-slate-950/60 border border-slate-800 rounded-2xl p-3">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block mb-1">
                  Database Table
                </span>
                <p className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  user_profiles (Synced)
                </p>
              </div>

              <div className="bg-slate-950/60 border border-slate-800 rounded-2xl p-3">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block mb-1">
                  Contact Phone
                </span>
                <p className="text-xs font-semibold text-white">
                  {profile.profile?.phone_number || 'Not provided'}
                </p>
              </div>
            </div>

            {/* Persona Cluster Badge */}
            <div className="bg-slate-950/60 border border-slate-800 rounded-2xl p-4 mb-5 text-xs">
              <span className="text-[10px] font-bold text-amber-400 uppercase tracking-wider block mb-1">
                K-Means Persona Segment:
              </span>
              <p className="font-bold text-white text-sm">
                {profile.preference?.cluster_id === 0 && '🎒 Budget Backpacker & Student'}
                {profile.preference?.cluster_id === 1 && '🏛️ Cultural Heritage Enthusiast'}
                {profile.preference?.cluster_id === 2 && '☕ Culinary & Café Connoisseur'}
                {profile.preference?.cluster_id === 3 && '👨‍👩‍👧 Family & Leisure Explorer'}
                {profile.preference?.cluster_id === undefined && '🌟 Explorer'}
              </p>
              <p className="text-slate-400 text-[11px] mt-1">
                City search and itinerary recommendations are automatically tailored to your profile.
              </p>
            </div>

            {/* Edit Profile Form Toggle */}
            {isEditingProfile ? (
              <div className="space-y-3 mb-5 bg-slate-950/80 border border-slate-800 p-4 rounded-2xl">
                <h4 className="font-bold text-white text-xs uppercase tracking-wider mb-2">
                  Update Account Profile (user_profiles table)
                </h4>
                <div>
                  <label className="text-[11px] text-slate-400 block mb-1">Full Name</label>
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="text-[11px] text-slate-400 block mb-1">Phone Number</label>
                  <input
                    type="text"
                    value={editPhone}
                    onChange={(e) => setEditPhone(e.target.value)}
                    placeholder="+91 98765 43210"
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Home City</label>
                    <input
                      type="text"
                      value={editCity}
                      onChange={(e) => setEditCity(e.target.value)}
                      placeholder="e.g. Lucknow"
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Home State</label>
                    <input
                      type="text"
                      value={editState}
                      onChange={(e) => setEditState(e.target.value)}
                      placeholder="e.g. Uttar Pradesh"
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-[11px] text-slate-400 block mb-1">Traveler Bio</label>
                  <textarea
                    rows={2}
                    value={editBio}
                    onChange={(e) => setEditBio(e.target.value)}
                    placeholder="Tell AI your travel interests..."
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div className="flex gap-2 pt-2">
                  <button
                    onClick={handleSaveProfileChanges}
                    disabled={loading}
                    className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 rounded-xl text-xs transition-all"
                  >
                    Save Changes to DB
                  </button>
                  <button
                    onClick={() => setIsEditingProfile(false)}
                    className="px-3 bg-slate-800 hover:bg-slate-750 text-slate-300 rounded-xl text-xs"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => setIsEditingProfile(true)}
                className="w-full mb-4 bg-slate-800 hover:bg-slate-750 border border-slate-700 text-slate-300 hover:text-white py-2 rounded-xl text-xs font-semibold transition-colors"
              >
                ✏️ Edit Account Profile Details
              </button>
            )}

            {savedSuccess && (
              <div className="mb-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs p-3 rounded-xl flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                <span>Account profile details saved successfully to database!</span>
              </div>
            )}

            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 text-xs font-semibold text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 py-2.5 rounded-xl border border-rose-500/20 transition-all"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign Out</span>
            </button>
          </div>
        ) : (
          /* Login / Register Form with Prominent Mode Tabs */
          <div>
            {/* Top Mode Tabs */}
            <div className="flex bg-slate-800/80 p-1.5 rounded-2xl mb-6 border border-slate-700">
              <button
                type="button"
                onClick={() => { setActiveMode('signin'); setError(null); }}
                className={`flex-1 py-2.5 text-xs font-bold rounded-xl transition-all ${
                  activeMode === 'signin'
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                🔑 Sign In
              </button>
              <button
                type="button"
                onClick={() => { setActiveMode('register'); setError(null); }}
                className={`flex-1 py-2.5 text-xs font-bold rounded-xl transition-all ${
                  activeMode === 'register'
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                ✍️ Create New Account (Register)
              </button>
            </div>

            <div className="mb-5">
              <h3 className="text-xl font-extrabold text-white mb-1">
                {activeMode === 'register' ? 'Register New Plan AI City Account' : 'Sign In to Your Account'}
              </h3>
              <p className="text-xs text-slate-400">
                {activeMode === 'register'
                  ? 'Your profile information will be safely stored in the user_profiles database table.'
                  : 'Enter your credentials to access saved plans and Pan-India intelligence.'}
              </p>
            </div>

            {error && (
              <div className="mb-4 bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs p-3 rounded-xl flex items-center justify-between">
                <span>{error}</span>
                {activeMode === 'signin' && (
                  <button
                    type="button"
                    onClick={() => { setActiveMode('register'); setError(null); }}
                    className="ml-2 font-bold underline text-indigo-300 hover:text-white"
                  >
                    Register instead
                  </button>
                )}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-3.5 mb-6">
              {activeMode === 'register' && (
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Full Name</label>
                  <div className="relative flex items-center">
                    <User className="w-4 h-4 text-slate-500 absolute left-3" />
                    <input
                      type="text"
                      required
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Deepali Prajapati"
                      className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl pl-9 pr-3 py-2.5 text-xs focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Email Address</label>
                <div className="relative flex items-center">
                  <Mail className="w-4 h-4 text-slate-500 absolute left-3" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="deepaliprajapti47@gmail.com"
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl pl-9 pr-3 py-2.5 text-xs focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Password</label>
                <div className="relative flex items-center">
                  <Lock className="w-4 h-4 text-slate-500 absolute left-3" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl pl-9 pr-10 py-2.5 text-xs focus:outline-none focus:border-indigo-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 text-slate-500 hover:text-slate-300"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {activeMode === 'register' && (
                <>
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">
                      Phone Number <span className="text-slate-500 font-normal">(Optional)</span>
                    </label>
                    <div className="relative flex items-center">
                      <Phone className="w-4 h-4 text-slate-500 absolute left-3" />
                      <input
                        type="tel"
                        value={phoneNumber}
                        onChange={(e) => setPhoneNumber(e.target.value)}
                        placeholder="+91 98765 43210"
                        className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl pl-9 pr-3 py-2.5 text-xs focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-xs font-semibold text-slate-300 block mb-1">Home City</label>
                      <input
                        type="text"
                        value={homeCity}
                        onChange={(e) => setHomeCity(e.target.value)}
                        placeholder="e.g. Lucknow / Delhi"
                        className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-3 py-2.5 text-xs focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-semibold text-slate-300 block mb-1">Home State</label>
                      <select
                        value={homeState}
                        onChange={(e) => setHomeState(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 text-white rounded-xl px-2 py-2.5 text-xs focus:outline-none focus:border-indigo-500 cursor-pointer"
                      >
                        {POPULAR_STATES.map((s) => (
                          <option key={s} value={s} className="bg-slate-900 text-white">
                            {s}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded-xl transition-all shadow-md shadow-indigo-600/30 text-xs flex items-center justify-center gap-2"
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : activeMode === 'register' ? (
                  <span>Register & Store Profile in Database</span>
                ) : (
                  <span>Sign In</span>
                )}
              </button>
            </form>

            {/* Quick Demo Logins */}
            <div className="pt-4 border-t border-slate-800 text-center">
              <span className="text-[11px] text-slate-400 block mb-2 font-medium">Or Use Quick Demo Accounts:</span>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => handleQuickDemo('traveler@planaicity.com', 'Traveler2026!')}
                  className="flex-1 text-[11px] bg-slate-800 hover:bg-slate-750 text-indigo-300 py-2 px-2 rounded-xl border border-slate-700 transition-colors"
                >
                  Demo Traveler
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickDemo('admin@planaicity.com', 'Admin@PlanCity2026')}
                  className="flex-1 text-[11px] bg-slate-800 hover:bg-slate-750 text-emerald-300 py-2 px-2 rounded-xl border border-slate-700 transition-colors"
                >
                  Demo Admin
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
