import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { fetchComplaints } from '../api';
import SLACountdown from './SLACountdown';
import { 
  Search, 
  MapPin, 
  Sparkles, 
  Filter, 
  Clock, 
  Users, 
  CheckCircle2, 
  Eye, 
  RefreshCw,
  AlertTriangle,
  BrainCircuit,
  X,
  Flame,
  UserCheck
} from 'lucide-react';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export default function CitizenBrowseFeed({ setActiveTab, currentUser, onOpenAuth }) {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');

  const categories = ['All', 'Road', 'Water', 'Waste', 'Streetlight', 'Drainage', 'Safety', 'Other'];

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchComplaints({
        q: search,
        category,
        status: statusFilter
      });
      setComplaints(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [category, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadData();
  };

  return (
    <div className="space-y-8 pb-12">
      
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-gray-800">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 dark:bg-indigo-500/20 border border-indigo-500/30 text-indigo-600 dark:text-indigo-300 text-xs font-semibold mb-2">
            <Users className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
            <span>Citizen Community Public Feed</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">Browse Public & Nearby Complaints</h1>
          <p className="text-slate-600 dark:text-gray-400 text-sm mt-1">Explore reported civic issues in your area, track 48h resolution SLA deadlines, and check community urgency.</p>
        </div>

        <div className="flex items-center space-x-3 self-start sm:self-auto">
          <button
            onClick={() => setActiveTab('submit')}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold text-xs shadow-lg shadow-indigo-500/30 hover:scale-[1.02] transition-all flex items-center space-x-1.5"
          >
            <span>+ Report New Issue</span>
          </button>
        </div>
      </div>

      {/* FILTER CONTROL BAR */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-200 dark:border-gray-800 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          
          <form onSubmit={handleSearchSubmit} className="md:col-span-2 relative">
            <Search className="w-4 h-4 text-slate-400 dark:text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by landmark, area, issue title..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white dark:bg-gray-900 border border-slate-300 dark:border-gray-700 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 shadow-sm"
            />
          </form>

          <div>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl bg-white dark:bg-gray-900 border border-slate-300 dark:border-gray-700 text-xs text-slate-900 dark:text-white focus:outline-none shadow-sm"
            >
              {categories.map(c => <option key={c} value={c}>Domain: {c}</option>)}
            </select>
          </div>

          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl bg-white dark:bg-gray-900 border border-slate-300 dark:border-gray-700 text-xs text-slate-900 dark:text-white focus:outline-none shadow-sm"
            >
              <option value="All">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="In Progress">In Progress</option>
              <option value="OVERDUE">OVERDUE</option>
              <option value="Resolved">Resolved ✓</option>
            </select>
          </div>

        </div>
      </div>

      {/* COMPLAINTS GRID CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full text-center py-16 space-y-3">
            <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin mx-auto" />
            <p className="text-xs text-slate-500 dark:text-gray-400">Loading public community complaints...</p>
          </div>
        ) : complaints.length === 0 ? (
          <div className="col-span-full text-center py-16 glass-panel rounded-2xl border border-slate-200 dark:border-gray-800">
            <MapPin className="w-10 h-10 text-slate-400 mx-auto mb-2" />
            <p className="text-sm font-bold text-slate-900 dark:text-white">No complaints found matching your search</p>
            <p className="text-xs text-slate-500 dark:text-gray-400 mt-1">Try clearing filters or search for another landmark.</p>
          </div>
        ) : (
          complaints.map((item) => (
            <div 
              key={item.id} 
              className="glass-card p-5 rounded-2xl border border-slate-200 dark:border-gray-800 hover:border-indigo-500/50 space-y-4 shadow-sm hover:shadow-lg transition-all flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-500/20 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-500/30">
                    {item.category}
                  </span>

                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    item.priority_level === 'Critical' ? 'bg-red-500/20 text-red-600 dark:text-red-400 border border-red-500/40' :
                    item.priority_level === 'High' ? 'bg-amber-500/20 text-amber-700 dark:text-amber-400 border border-amber-500/40' :
                    'bg-blue-500/20 text-blue-700 dark:text-blue-300'
                  }`}>
                    Urgency: {item.priority_score}/100
                  </span>
                </div>

                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white line-clamp-1">{item.title}</h3>
                  <p className="text-xs text-slate-500 dark:text-gray-400 mt-1 flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                    <span className="truncate">{item.location}</span>
                  </p>
                </div>

                <p className="text-xs text-slate-600 dark:text-gray-300 line-clamp-2 leading-relaxed">
                  {item.description}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-200 dark:border-gray-800 flex items-center justify-between gap-2">
                <SLACountdown 
                  deadlineAt={item.deadline_at} 
                  status={item.status}
                  createdAt={item.created_at}
                  resolvedAt={item.resolved_at}
                  escalationLevel={item.escalation_level}
                />

                <button
                  onClick={() => setSelectedComplaint(item)}
                  className="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-gray-800 text-slate-700 dark:text-gray-300 hover:bg-indigo-600 hover:text-white text-xs font-semibold transition-colors flex items-center gap-1"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>Inspect</span>
                </button>
              </div>

            </div>
          ))
        )}
      </div>

      {/* COMPLAINT INSPECT MODAL */}
      {selectedComplaint && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-200 dark:border-gray-700 max-w-2xl w-full max-h-[90vh] overflow-y-auto space-y-6 relative shadow-2xl">
            
            <button
              onClick={() => setSelectedComplaint(null)}
              className="absolute top-6 right-6 p-2 rounded-xl bg-slate-100 dark:bg-gray-800 text-slate-500 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Header */}
            <div className="space-y-2 border-b border-slate-200 dark:border-gray-800 pb-4 pr-8">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-500/10 px-2.5 py-0.5 rounded-full border border-indigo-200 dark:border-indigo-500/20">
                  {selectedComplaint.category} Domain
                </span>
                <span className="text-xs text-slate-500 dark:text-gray-400">• Reported by {selectedComplaint.name}</span>
              </div>
              <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white">{selectedComplaint.title}</h2>
              <p className="text-xs text-slate-600 dark:text-gray-300 mt-1 flex items-center gap-1">
                <MapPin className="w-4 h-4 text-emerald-600 dark:text-emerald-400" /> {selectedComplaint.location}
              </p>
            </div>

            {/* Details & AI insights */}
            <div className="space-y-3">
              <p className="text-xs text-slate-800 dark:text-gray-200 bg-slate-100 dark:bg-gray-900 p-3 rounded-xl border border-slate-200 dark:border-gray-800 leading-relaxed">
                {selectedComplaint.description}
              </p>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div className="glass-card p-3 rounded-xl">
                  <p className="text-[10px] text-slate-500 dark:text-gray-400">AI Priority Score</p>
                  <p className="text-xs font-bold text-red-600 dark:text-red-400 mt-0.5">{selectedComplaint.priority_score}/100 ({selectedComplaint.priority_level})</p>
                </div>
                <div className="glass-card p-3 rounded-xl">
                  <p className="text-[10px] text-slate-500 dark:text-gray-400">Severity Level</p>
                  <p className="text-xs font-bold text-slate-900 dark:text-white mt-0.5">{selectedComplaint.severity}</p>
                </div>
                <div className="glass-card p-3 rounded-xl">
                  <p className="text-[10px] text-slate-500 dark:text-gray-400">Cosine Duplicate Match</p>
                  <p className="text-xs font-bold text-amber-600 dark:text-amber-400 mt-0.5">{selectedComplaint.similarity_score}%</p>
                </div>
              </div>
            </div>

            {/* Map Snippet */}
            <div className="h-40 w-full rounded-xl overflow-hidden border border-slate-200 dark:border-gray-700">
              <MapContainer
                center={[selectedComplaint.latitude, selectedComplaint.longitude]}
                zoom={14}
                scrollWheelZoom={false}
                style={{ height: '100%', width: '100%' }}
              >
                <TileLayer
                  attribution='&copy; OpenStreetMap'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <Marker position={[selectedComplaint.latitude, selectedComplaint.longitude]} />
              </MapContainer>
            </div>

            {/* 48h SLA Status */}
            <div className="p-4 rounded-xl bg-slate-100 dark:bg-gray-900 border border-slate-200 dark:border-gray-800 flex items-center justify-between">
              <div>
                <p className="text-xs font-bold text-slate-900 dark:text-white">48-Hour Resolution SLA Status</p>
                <p className="text-[11px] text-slate-500 dark:text-gray-400 mt-0.5">Municipal action window deadline</p>
              </div>
              <SLACountdown 
                deadlineAt={selectedComplaint.deadline_at} 
                status={selectedComplaint.status}
                createdAt={selectedComplaint.created_at}
                resolvedAt={selectedComplaint.resolved_at}
                escalationLevel={selectedComplaint.escalation_level}
              />
            </div>

            {/* Resolution Proof Showcase if Resolved */}
            {selectedComplaint.status === 'Resolved' && selectedComplaint.resolution_photo && (
              <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-300 dark:border-emerald-800/60 space-y-2">
                <div className="flex items-center space-x-2 text-emerald-700 dark:text-emerald-400 text-xs font-bold">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Authority Resolution Proof Photo & Note</span>
                </div>
                <img 
                  src={selectedComplaint.resolution_photo} 
                  alt="Proof" 
                  className="w-full h-36 object-cover rounded-lg border border-emerald-300 dark:border-emerald-800"
                />
                <p className="text-xs text-slate-800 dark:text-gray-200 italic">"{selectedComplaint.resolution_note || 'Completed by municipal unit.'}"</p>
              </div>
            )}

          </div>
        </div>
      )}

    </div>
  );
}
