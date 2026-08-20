import React, { useState, useMemo, useRef, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import { submitComplaint } from '../api';
import SLACountdown from './SLACountdown';
import { 
  Send, 
  MapPin, 
  CheckCircle2, 
  Sparkles, 
  AlertTriangle, 
  BrainCircuit, 
  ArrowRight, 
  RefreshCw,
  User,
  Tag,
  FileText,
  Search,
  Clock
} from 'lucide-react';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

function MapRecenter({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center && center[0] && center[1]) {
      map.flyTo(center, 16, { animate: true, duration: 1.2 });
    }
  }, [center, map]);
  return null;
}

function DraggableLocationMarker({ position, setPosition, setLocationName }) {
  const markerRef = useRef(null);

  useMapEvents({
    click(e) {
      const { lat, lng } = e.latlng;
      setPosition({ lat, lng });
      setLocationName(`Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`);
    },
  });

  const eventHandlers = useMemo(
    () => ({
      dragend() {
        const marker = markerRef.current;
        if (marker != null) {
          const latLng = marker.getLatLng();
          setPosition({ lat: latLng.lat, lng: latLng.lng });
          setLocationName(`Lat: ${latLng.lat.toFixed(5)}, Lng: ${latLng.lng.toFixed(5)}`);
        }
      },
    }),
    [setPosition, setLocationName],
  );

  return (
    <Marker
      draggable={true}
      eventHandlers={eventHandlers}
      position={[position.lat, position.lng]}
      ref={markerRef}
    />
  );
}

export default function ComplaintForm({ setActiveTab }) {
  const [formData, setFormData] = useState({
    name: '',
    title: '',
    category: 'Road',
    location: '',
    description: ''
  });

  const [mapPosition, setMapPosition] = useState({ lat: 12.3124, lng: 76.6512 });
  const [searchQuery, setSearchQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [aiResult, setAiResult] = useState(null);

  const categories = ['Road', 'Water', 'Waste', 'Streetlight', 'Drainage', 'Safety', 'Other'];

  const handleLocationSearch = async (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (!searchQuery.trim()) return;
    
    setSearching(true);
    setSearchResults([]);
    try {
      const queryStr = searchQuery.includes(',') ? searchQuery : `${searchQuery}, Mysuru, Karnataka, India`;
      const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(queryStr)}`);
      const data = await res.json();
      
      if (data && data.length > 0) {
        setSearchResults(data.slice(0, 4));
        const first = data[0];
        const newLat = parseFloat(first.lat);
        const newLng = parseFloat(first.lon);
        setMapPosition({ lat: newLat, lng: newLng });
        
        const shortName = first.display_name.split(',')[0] + ', ' + (first.display_name.split(',')[1] || '');
        setFormData(prev => ({ ...prev, location: prev.location || shortName.trim() }));
      } else {
        const fallbackRes = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery)}`);
        const fallbackData = await fallbackRes.json();
        if (fallbackData && fallbackData.length > 0) {
          setSearchResults(fallbackData.slice(0, 4));
          const first = fallbackData[0];
          const newLat = parseFloat(first.lat);
          const newLng = parseFloat(first.lon);
          setMapPosition({ lat: newLat, lng: newLng });
        } else {
          alert('Location not found. Try dragging the blue map marker pin directly to your exact spot.');
        }
      }
    } catch (err) {
      console.error("Geocoding search failed:", err);
      alert('Geocoding search failed. You can directly drag the pin on the map.');
    } finally {
      setSearching(false);
    }
  };

  const selectSearchResult = (item) => {
    const newLat = parseFloat(item.lat);
    const newLng = parseFloat(item.lon);
    setMapPosition({ lat: newLat, lng: newLng });
    const shortName = item.display_name.split(',')[0] + ', ' + (item.display_name.split(',')[1] || '');
    setFormData(prev => ({ ...prev, location: shortName.trim() }));
    setSearchResults([]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.title || !formData.description) {
      setError('Please fill in all required fields.');
      return;
    }

    setError('');
    setLoading(true);

    const payload = {
      name: formData.name,
      title: formData.title,
      category: formData.category,
      location: formData.location || `Lat ${mapPosition.lat.toFixed(5)}, Lng ${mapPosition.lng.toFixed(5)}`,
      latitude: mapPosition.lat,
      longitude: mapPosition.lng,
      description: formData.description
    };

    try {
      const response = await submitComplaint(payload);
      setAiResult(response);
    } catch (err) {
      setError(err.message || 'Failed to submit complaint. Make sure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      name: '',
      title: '',
      category: 'Road',
      location: '',
      description: ''
    });
    setAiResult(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 dark:bg-indigo-500/20 border border-indigo-500/30 text-indigo-600 dark:text-indigo-300 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Real-time AI NLP & 48-Hour SLA Countdown</span>
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">Report a Civic Issue</h1>
        <p className="text-slate-600 dark:text-gray-400 text-sm max-w-lg mx-auto">
          Search your location, drag the map marker pin, or use zoom in/out controls to pinpoint the exact spot.
        </p>
      </div>

      {/* Main Form Container */}
      {!aiResult ? (
        <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-200 dark:border-gray-800 shadow-xl relative">
          
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-500/10 dark:bg-red-950/50 border border-red-500/30 dark:border-red-800 text-red-600 dark:text-red-300 text-sm flex items-center space-x-3">
              <AlertTriangle className="w-5 h-5 text-red-500 dark:text-red-400 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Citizen Name & Title */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-gray-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <User className="w-4 h-4 text-indigo-600 dark:text-indigo-400" /> Submitter Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Aarav Sharma"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl bg-white dark:bg-gray-900/80 border border-slate-300 dark:border-gray-700 text-slate-900 dark:text-white text-sm placeholder-slate-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition-colors shadow-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-gray-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <Tag className="w-4 h-4 text-indigo-600 dark:text-indigo-400" /> Complaint Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Broken Pothole near College Gate 2"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl bg-white dark:bg-gray-900/80 border border-slate-300 dark:border-gray-700 text-slate-900 dark:text-white text-sm placeholder-slate-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition-colors shadow-sm"
                />
              </div>
            </div>

            {/* Category & Ward Location */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-gray-300 uppercase tracking-wider mb-2">
                  Category Domain *
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl bg-white dark:bg-gray-900 border border-slate-300 dark:border-gray-700 text-slate-900 dark:text-white text-sm focus:outline-none focus:border-indigo-500 transition-colors shadow-sm"
                >
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-gray-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <MapPin className="w-4 h-4 text-indigo-600 dark:text-indigo-400" /> Location Name / Ward
                </label>
                <input
                  type="text"
                  placeholder="e.g. Main Campus Road, Ward 12"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl bg-white dark:bg-gray-900/80 border border-slate-300 dark:border-gray-700 text-slate-900 dark:text-white text-sm placeholder-slate-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition-colors shadow-sm"
                />
              </div>
            </div>

            {/* Interactive Leaflet Location Picker with Search & Drag */}
            <div className="space-y-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <label className="text-xs font-semibold text-slate-700 dark:text-gray-300 uppercase tracking-wider flex items-center gap-1.5">
                  <MapPin className="w-4 h-4 text-emerald-600 dark:text-emerald-400" /> Exact Map Location (Click or Drag Pin)
                </label>

                {/* Location Search Input & Button */}
                <div className="flex items-center space-x-2 relative">
                  <input
                    type="text"
                    placeholder="Search place/city/landmark..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleLocationSearch(e);
                      }
                    }}
                    className="px-3.5 py-1.5 rounded-xl bg-white dark:bg-gray-900 border border-slate-300 dark:border-gray-700 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 shadow-sm w-48 sm:w-60"
                  />
                  <button
                    type="button"
                    onClick={handleLocationSearch}
                    disabled={searching}
                    className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-md flex items-center gap-1 shrink-0"
                  >
                    <Search className="w-3.5 h-3.5" />
                    <span>{searching ? 'Locating...' : 'Search'}</span>
                  </button>
                </div>
              </div>

              {/* Multiple Search Results Dropdown List */}
              {searchResults.length > 0 && (
                <div className="bg-white dark:bg-gray-900 border border-slate-200 dark:border-gray-800 rounded-xl p-2 space-y-1 shadow-lg text-xs">
                  <p className="text-[10px] font-bold text-slate-500 dark:text-gray-400 px-2">Select exact match location:</p>
                  {searchResults.map((item, idx) => (
                    <div
                      key={idx}
                      onClick={() => selectSearchResult(item)}
                      className="p-2 rounded-lg hover:bg-indigo-50 dark:hover:bg-gray-800 cursor-pointer text-slate-800 dark:text-gray-200 flex items-center justify-between transition-colors"
                    >
                      <span className="truncate pr-2 font-medium">{item.display_name}</span>
                      <span className="text-[10px] font-mono text-indigo-600 dark:text-indigo-400 shrink-0">Select →</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Coordinates Badge */}
              <div className="flex items-center justify-between text-xs font-mono text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/40 p-2.5 rounded-xl border border-indigo-200 dark:border-indigo-800/40">
                <span>📍 Captured Coordinates:</span>
                <span className="font-bold">Lat: {mapPosition.lat.toFixed(5)}, Lng: {mapPosition.lng.toFixed(5)}</span>
              </div>

              {/* Leaflet Map */}
              <div className="h-72 w-full rounded-xl overflow-hidden border border-slate-300 dark:border-gray-700 shadow-inner relative">
                <MapContainer
                  center={[mapPosition.lat, mapPosition.lng]}
                  zoom={15}
                  minZoom={4}
                  maxZoom={19}
                  scrollWheelZoom={true}
                  doubleClickZoom={true}
                  zoomControl={true}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  <MapRecenter center={[mapPosition.lat, mapPosition.lng]} />
                  <DraggableLocationMarker 
                    position={mapPosition} 
                    setPosition={setMapPosition}
                    setLocationName={(name) => {
                      if (!formData.location) setFormData(prev => ({ ...prev, location: name }));
                    }}
                  />
                </MapContainer>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-gray-400">💡 Drag the blue map marker or click anywhere to capture exact latitude & longitude.</p>
            </div>

            {/* Description */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-gray-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <FileText className="w-4 h-4 text-indigo-600 dark:text-indigo-400" /> Description & Details *
              </label>
              <textarea
                required
                rows={4}
                placeholder="Describe the issue, hazard level, landmark context..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-4 py-3 rounded-xl bg-white dark:bg-gray-900/80 border border-slate-300 dark:border-gray-700 text-slate-900 dark:text-white text-sm placeholder-slate-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 transition-colors shadow-sm"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-4 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white font-bold text-base shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:scale-[1.01] transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  <span>AI Engine Vector Processing...</span>
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  <span>Submit & Trigger AI Analysis</span>
                </>
              )}
            </button>

          </form>

        </div>
      ) : (

        /* AI RESULT MODAL CARD */
        <div className="glass-panel p-6 sm:p-8 rounded-2xl border-2 border-indigo-500/50 shadow-2xl space-y-6 animate-in fade-in zoom-in-95 duration-300">
          
          {/* Header */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-slate-200 dark:border-gray-800 gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white shadow-lg">
                <BrainCircuit className="w-7 h-7" />
              </div>
              <div>
                <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">AI Intelligence Analysis Result</span>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white">{aiResult.title}</h2>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="bg-indigo-50 dark:bg-indigo-950/60 px-4 py-2 rounded-xl border border-indigo-200 dark:border-indigo-800/60 text-right">
                <p className="text-[10px] text-slate-500 dark:text-gray-400 font-medium">Priority Score</p>
                <p className="text-2xl font-black text-indigo-600 dark:text-indigo-300">{aiResult.priority_score}<span className="text-xs text-slate-400">/100</span></p>
              </div>
            </div>
          </div>

          {/* 48-Hour SLA Timer Bar */}
          <div className="p-4 rounded-xl bg-slate-100 dark:bg-gray-900/90 border border-slate-200 dark:border-gray-800 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Clock className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <div>
                <p className="text-xs font-bold text-slate-900 dark:text-white">Resolution SLA Deadline</p>
                <p className="text-[11px] text-slate-500 dark:text-gray-400">48-Hour Municipal Action Window</p>
              </div>
            </div>
            <SLACountdown 
              deadlineAt={aiResult.deadline_at} 
              status={aiResult.status}
              createdAt={aiResult.created_at}
              escalationLevel={aiResult.escalation_level}
            />
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="glass-card p-4 rounded-xl">
              <p className="text-xs text-slate-500 dark:text-gray-400">Category AI Match</p>
              <p className="text-base font-bold text-indigo-600 dark:text-indigo-300 mt-1">{aiResult.category}</p>
            </div>

            <div className="glass-card p-4 rounded-xl">
              <p className="text-xs text-slate-500 dark:text-gray-400">Severity</p>
              <span className={`inline-block mt-1 text-xs font-bold px-2.5 py-1 rounded-full ${
                aiResult.severity === 'Critical' ? 'bg-red-500/20 text-red-600 dark:text-red-300 border border-red-500/40' :
                aiResult.severity === 'High' ? 'bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/40' :
                'bg-blue-500/20 text-blue-700 dark:text-blue-300 border border-blue-500/40'
              }`}>
                {aiResult.severity}
              </span>
            </div>

            <div className="glass-card p-4 rounded-xl">
              <p className="text-xs text-slate-500 dark:text-gray-400">Duplicate Match</p>
              <p className={`text-base font-bold mt-1 ${aiResult.similarity_score >= 50 ? 'text-amber-600 dark:text-amber-400' : 'text-emerald-600 dark:text-emerald-400'}`}>
                {aiResult.similarity_score}%
              </p>
            </div>

            <div className="glass-card p-4 rounded-xl">
              <p className="text-xs text-slate-500 dark:text-gray-400">Tone Sentiment</p>
              <p className="text-base font-bold text-slate-800 dark:text-gray-200 mt-1">{aiResult.sentiment}</p>
            </div>
          </div>

          {/* Duplicate Alert */}
          {aiResult.similarity_score >= 50.0 && (
            <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 text-amber-800 dark:text-amber-200 text-xs sm:text-sm flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
              <div>
                <strong className="font-bold text-amber-900 dark:text-amber-300">Potential Duplicate Flagged ({aiResult.similarity_score}% Cosine Match):</strong>
                <p className="mt-0.5 opacity-90">
                  Detected existing incident in database with similar description. Community urgency score boosted.
                </p>
              </div>
            </div>
          )}

          {/* AI Recommendation */}
          <div className="p-5 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800/60 space-y-2">
            <div className="flex items-center space-x-2 text-indigo-700 dark:text-indigo-300 font-semibold text-xs uppercase tracking-wider">
              <Sparkles className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <span>AI Municipal Action Recommendation</span>
            </div>
            <p className="text-sm text-slate-800 dark:text-gray-100 font-medium leading-relaxed">
              "{aiResult.recommendation}"
            </p>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-200 dark:border-gray-800">
            <button
              onClick={handleReset}
              className="w-full sm:w-auto px-5 py-2.5 rounded-xl glass-card text-slate-700 dark:text-gray-300 text-xs font-semibold hover:bg-slate-100 dark:hover:bg-gray-800 transition-colors flex items-center justify-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Submit Another Complaint</span>
            </button>

            <div className="flex items-center space-x-3 w-full sm:w-auto">
              <button
                onClick={() => setActiveTab('map')}
                className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl bg-indigo-50 dark:bg-indigo-600/30 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/40 hover:bg-indigo-100 dark:hover:bg-indigo-600/50 text-xs font-semibold transition-colors flex items-center justify-center space-x-2"
              >
                <MapPin className="w-4 h-4" />
                <span>View on Map</span>
              </button>

              <button
                onClick={() => setActiveTab('dashboard')}
                className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl bg-indigo-600 text-white hover:bg-indigo-500 text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2"
              >
                <span>Dashboard Analytics</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
