import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import L from 'leaflet';
import { fetchComplaints, updateComplaintStatus, resolveComplaint } from '../api';
import SLACountdown from './SLACountdown';
import { 
  Search, 
  Filter, 
  Sparkles, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  MapPin, 
  Eye, 
  X, 
  RefreshCw,
  BrainCircuit,
  User,
  ArrowUpDown,
  Tag,
  ShieldAlert,
  Camera,
  FileCheck,
  Check
} from 'lucide-react';

const sampleProofPhotos = [
  { label: 'Road Paved', url: 'https://images.unsplash.com/photo-1590674899484-d5640e854abe?auto=format&fit=crop&w=600&q=80' },
  { label: 'Pipe Sealed', url: 'https://images.unsplash.com/photo-1584992236310-6edddc08acff?auto=format&fit=crop&w=600&q=80' },
  { label: 'Light Fixed', url: 'https://images.unsplash.com/photo-1508873696983-2df515122519?auto=format&fit=crop&w=600&q=80' },
  { label: 'Waste Cleared', url: 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=600&q=80' }
];

export default function ComplaintManagement({ setActiveTab }) {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [updatingId, setUpdatingId] = useState(null);

  const [resolutionForm, setResolutionForm] = useState({
    resolved_by: 'Eng. Ramesh V (Ward Officer)',
    resolution_note: '',
    resolution_photo: sampleProofPhotos[0].url
  });
  const [resolving, setResolving] = useState(false);

  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');
  const [priority, setPriority] = useState('All');
  const [status, setStatus] = useState('All');
  const [sortBy, setSortBy] = useState('priority_desc');

  const categories = ['All', 'Road', 'Water', 'Waste', 'Streetlight', 'Drainage', 'Safety', 'Other'];
  const priorityLevels = ['All', 'Critical', 'High', 'Medium', 'Low'];
  const statusLevels = ['All', 'Pending', 'In Progress', 'OVERDUE', 'Resolved'];

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchComplaints({
        q: search,
        category,
        priority,
        status
      });

      let sorted = [...data];
      if (sortBy === 'priority_desc') {
        sorted.sort((a, b) => b.priority_score - a.priority_score);
      } else if (sortBy === 'newest') {
        sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      } else if (sortBy === 'oldest') {
        sorted.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
      } else if (sortBy === 'similarity_desc') {
        sorted.sort((a, b) => b.similarity_score - a.similarity_score);
      }

      setComplaints(sorted);

      if (selectedComplaint) {
        const updated = sorted.find(c => c.id === selectedComplaint.id);
        if (updated) setSelectedComplaint(updated);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [category, priority, status, sortBy]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadData();
  };

  const handleStatusUpdate = async (id, newStatus) => {
    setUpdatingId(id);
    try {
      await updateComplaintStatus(id, newStatus);
      await loadData();
    } catch (err) {
      alert(`Status update failed: ${err.message}`);
    } finally {
      setUpdatingId(null);
    }
  };

  const handleAuthorityResolveSubmit = async (e) => {
    e.preventDefault();
    if (!selectedComplaint) return;
    
    setResolving(true);
    try {
      const updated = await resolveComplaint(selectedComplaint.id, {
        status: 'Resolved',
        resolution_photo: resolutionForm.resolution_photo || sampleProofPhotos[0].url,
        resolution_note: resolutionForm.resolution_note || 'Issue inspected, repaired and verified by municipal authority.',
        resolved_by: resolutionForm.resolved_by || 'Ward Officer'
      });
      setSelectedComplaint(updated);
      await loadData();
    } catch (err) {
      alert(`Resolution failed: ${err.message}`);
    } finally {
      setResolving(false);
    }
  };

  const handlePhotoFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setResolutionForm(prev => ({ ...prev, resolution_photo: reader.result }));
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-gray-800 light:border-slate-200">
        <div>
          <h1 className="text-3xl font-extrabold text-white light:text-slate-900 tracking-tight">Admin Portal & Resolution Hub</h1>
          <p className="text-gray-400 light:text-slate-600 text-sm mt-1">Audit complaints, track 48h SLA timers, monitor escalations, and upload resolution proof photos.</p>
        </div>

        <button
          onClick={loadData}
          className="px-4 py-2 rounded-xl glass-card text-xs font-semibold text-gray-300 light:text-slate-700 hover:bg-gray-800 light:hover:bg-slate-200 transition-colors flex items-center space-x-2 self-start sm:self-auto shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* FILTER CONTROL BAR */}
      <div className="glass-panel p-4 rounded-2xl border border-gray-800 light:border-slate-200 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          
          <form onSubmit={handleSearchSubmit} className="md:col-span-2 relative">
            <Search className="w-4 h-4 text-gray-400 light:text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search title, citizen name, location..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-gray-900 light:bg-white border border-gray-700 light:border-slate-300 text-xs text-white light:text-slate-900 placeholder-gray-500 light:placeholder-slate-400 focus:outline-none focus:border-indigo-500 shadow-sm"
            />
          </form>

          <div>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl bg-gray-900 light:bg-white border border-gray-700 light:border-slate-300 text-xs text-white light:text-slate-900 focus:outline-none shadow-sm"
            >
              {categories.map(c => <option key={c} value={c}>Cat: {c}</option>)}
            </select>
          </div>

          <div>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl bg-gray-900 light:bg-white border border-gray-700 light:border-slate-300 text-xs text-white light:text-slate-900 focus:outline-none shadow-sm"
            >
              {priorityLevels.map(p => <option key={p} value={p}>Prio: {p}</option>)}
            </select>
          </div>

          <div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-3 py-2.5 rounded-xl bg-gray-900 light:bg-white border border-gray-700 light:border-slate-300 text-xs text-white light:text-slate-900 focus:outline-none shadow-sm"
            >
              <option value="priority_desc">Sort: Highest Priority</option>
              <option value="newest">Sort: Newest First</option>
              <option value="oldest">Sort: Oldest First</option>
              <option value="similarity_desc">Sort: Max Similarity</option>
            </select>
          </div>

        </div>
      </div>

      {/* COMPLAINTS TABLE */}
      <div className="glass-panel rounded-2xl border border-gray-800 light:border-slate-200 overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-gray-300 light:text-slate-700">
            
            <thead className="bg-gray-900/90 light:bg-slate-100 text-gray-400 light:text-slate-600 font-semibold uppercase tracking-wider border-b border-gray-800 light:border-slate-200">
              <tr>
                <th className="py-3.5 px-4">Issue Details</th>
                <th className="py-3.5 px-4">Category</th>
                <th className="py-3.5 px-4 text-center">Priority</th>
                <th className="py-3.5 px-4">48h SLA Timer & Escalation</th>
                <th className="py-3.5 px-4">Status Action</th>
                <th className="py-3.5 px-4 text-right">Details</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-gray-800/80 light:divide-slate-200">
              {complaints.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-gray-500 light:text-slate-500">
                    No complaints match the selected filters.
                  </td>
                </tr>
              ) : (
                complaints.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-800/40 light:hover:bg-slate-100/60 transition-colors">
                    
                    {/* Title & Location */}
                    <td className="py-3.5 px-4">
                      <div>
                        <span className="font-bold text-white light:text-slate-900 text-sm line-clamp-1">{item.title}</span>
                        <div className="flex items-center space-x-2 text-gray-400 light:text-slate-500 text-[11px] mt-0.5">
                          <span className="flex items-center gap-1"><User className="w-3 h-3 text-indigo-400 light:text-indigo-600" /> {item.name}</span>
                          <span>•</span>
                          <span className="flex items-center gap-1"><MapPin className="w-3 h-3 text-emerald-400 light:text-emerald-600" /> {item.location}</span>
                        </div>
                      </div>
                    </td>

                    {/* Category */}
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-1 rounded-full bg-indigo-500/10 light:bg-indigo-50 text-indigo-300 light:text-indigo-700 border border-indigo-500/20 light:border-indigo-200 font-medium text-[11px]">
                        {item.category}
                      </span>
                    </td>

                    {/* Priority Score */}
                    <td className="py-3.5 px-4 text-center">
                      <span className={`px-2.5 py-0.5 rounded-full font-bold text-[11px] ${
                        item.priority_level === 'Critical' ? 'bg-red-500/20 text-red-400 light:text-red-600 border border-red-500/40' :
                        item.priority_level === 'High' ? 'bg-amber-500/20 text-amber-400 light:text-amber-700 border border-amber-500/40' :
                        'bg-blue-500/20 text-blue-300 light:text-blue-700'
                      }`}>
                        {item.priority_score} / 100
                      </span>
                    </td>

                    {/* SLA Timer */}
                    <td className="py-3.5 px-4">
                      <SLACountdown 
                        deadlineAt={item.deadline_at} 
                        status={item.status}
                        createdAt={item.created_at}
                        resolvedAt={item.resolved_at}
                        escalationLevel={item.escalation_level}
                      />
                    </td>

                    {/* Status Pill Select */}
                    <td className="py-3.5 px-4">
                      <select
                        disabled={updatingId === item.id}
                        value={item.status}
                        onChange={(e) => handleStatusUpdate(item.id, e.target.value)}
                        className={`px-3 py-1.5 rounded-xl text-xs font-bold focus:outline-none transition-colors shadow-sm ${
                          item.status === 'Pending' ? 'bg-amber-950/60 light:bg-amber-100 text-amber-300 light:text-amber-800 border border-amber-800 light:border-amber-300' :
                          item.status === 'In Progress' ? 'bg-indigo-950/60 light:bg-indigo-100 text-indigo-300 light:text-indigo-800 border border-indigo-800 light:border-indigo-300' :
                          item.status === 'OVERDUE' || item.status === 'ESCALATED' ? 'bg-red-950/60 light:bg-red-100 text-red-300 light:text-red-800 border border-red-800 light:border-red-300' :
                          'bg-emerald-950/60 light:bg-emerald-100 text-emerald-300 light:text-emerald-800 border border-emerald-800 light:border-emerald-300'
                        }`}
                      >
                        <option value="Pending">Pending</option>
                        <option value="In Progress">In Progress</option>
                        <option value="OVERDUE">OVERDUE</option>
                        <option value="Resolved">Resolved</option>
                      </select>
                    </td>

                    {/* Detail Trigger */}
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => setSelectedComplaint(item)}
                        className="px-3 py-1.5 rounded-xl bg-indigo-600 text-white font-semibold hover:bg-indigo-500 transition-colors flex items-center space-x-1 ml-auto shadow-sm"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspect</span>
                      </button>
                    </td>

                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* FULL DETAILS DEMO SCREEN MODAL */}
      {selectedComplaint && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-gray-700 light:border-slate-200 max-w-3xl w-full max-h-[92vh] overflow-y-auto space-y-6 relative shadow-2xl">
            
            <button
              onClick={() => setSelectedComplaint(null)}
              className="absolute top-6 right-6 p-2 rounded-xl bg-gray-800 light:bg-slate-100 text-gray-400 light:text-slate-500 hover:text-white light:hover:text-slate-900 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            {/* SECTION 1: Complaint Information */}
            <div className="space-y-3 border-b border-gray-800 light:border-slate-200 pb-4 pr-10">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-bold text-indigo-400 light:text-indigo-700 bg-indigo-500/10 light:bg-indigo-50 px-3 py-0.5 rounded-full border border-indigo-500/20 light:border-indigo-200">
                  Incident ID #{selectedComplaint.id}
                </span>
                <span className="text-xs text-gray-400 light:text-slate-500">• Submitted by {selectedComplaint.name}</span>
                <span className="text-xs text-gray-400 light:text-slate-500">• {new Date(selectedComplaint.created_at).toLocaleString()}</span>
              </div>
              <h2 className="text-2xl font-extrabold text-white light:text-slate-900">{selectedComplaint.title}</h2>
              <p className="text-xs text-gray-200 light:text-slate-800 bg-gray-900/60 light:bg-slate-100 p-3 rounded-xl border border-gray-800 light:border-slate-200 leading-relaxed">
                {selectedComplaint.description}
              </p>
            </div>

            {/* SECTION 2: 📍 Exact Map Location */}
            <div className="space-y-2">
              <h3 className="text-xs font-bold text-gray-300 light:text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-emerald-400 light:text-emerald-600" /> 📍 Exact Map Location & Coordinates
              </h3>
              
              <div className="flex items-center justify-between text-xs font-mono text-indigo-300 light:text-indigo-700 bg-gray-900 light:bg-slate-100 p-2.5 rounded-xl border border-gray-800 light:border-slate-200">
                <span>{selectedComplaint.location}</span>
                <span className="font-bold">Lat: {selectedComplaint.latitude.toFixed(5)}, Lng: {selectedComplaint.longitude.toFixed(5)}</span>
              </div>

              <div className="h-44 w-full rounded-xl overflow-hidden border border-gray-700 light:border-slate-300">
                <MapContainer
                  center={[selectedComplaint.latitude, selectedComplaint.longitude]}
                  zoom={15}
                  scrollWheelZoom={false}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  <Marker position={[selectedComplaint.latitude, selectedComplaint.longitude]} />
                </MapContainer>
              </div>
            </div>

            {/* SECTION 3 & 4: AI Analysis & Priority Score */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-gray-300 light:text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <BrainCircuit className="w-4 h-4 text-indigo-400 light:text-indigo-600" /> 🤖 AI Engine Analysis & 🔥 Priority Score
              </h3>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="glass-card p-3 rounded-xl">
                  <p className="text-[10px] text-gray-400 light:text-slate-500">Category Domain</p>
                  <p className="text-xs font-bold text-indigo-300 light:text-indigo-700 mt-0.5">{selectedComplaint.category}</p>
                </div>
                <div className="glass-card p-3 rounded-xl">
                  <p className="text-[10px] text-gray-400 light:text-slate-500">Priority Score</p>
                  <p className="text-xs font-bold text-red-400 light:text-red-600 mt-0.5">{selectedComplaint.priority_score} / 100 ({selectedComplaint.priority_level})</p>
                </div>
                <div className="glass-card p-3 rounded-xl">
                  <p className="text-[10px] text-gray-400 light:text-slate-500">Duplicate Match</p>
                  <p className="text-xs font-bold text-amber-400 light:text-amber-600 mt-0.5">{selectedComplaint.similarity_score}%</p>
                </div>
                <div className="glass-card p-3 rounded-xl">
                  <p className="text-[10px] text-gray-400 light:text-slate-500">Severity & Tone</p>
                  <p className="text-xs font-bold text-gray-200 light:text-slate-800 mt-0.5">{selectedComplaint.severity} • {selectedComplaint.sentiment}</p>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-indigo-950/40 light:bg-indigo-50 border border-indigo-800/50 light:border-indigo-200 text-xs text-gray-200 light:text-slate-800 leading-relaxed">
                <strong className="text-indigo-300 light:text-indigo-700">AI Dispatch Recommendation:</strong> "{selectedComplaint.recommendation}"
              </div>
            </div>

            {/* SECTION 5 & 6: SLA Timer & Escalation History */}
            <div className="p-4 rounded-xl bg-gray-900/90 light:bg-slate-100 border border-gray-800 light:border-slate-200 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center space-x-2">
                  <Clock className="w-5 h-5 text-indigo-400 light:text-indigo-600" />
                  <div>
                    <h4 className="text-xs font-bold text-white light:text-slate-900">⏱ 48-Hour Resolution SLA Countdown</h4>
                    <p className="text-[11px] text-gray-400 light:text-slate-500">Deadline: {new Date(selectedComplaint.deadline_at).toLocaleString()}</p>
                  </div>
                </div>

                <SLACountdown 
                  deadlineAt={selectedComplaint.deadline_at} 
                  status={selectedComplaint.status}
                  createdAt={selectedComplaint.created_at}
                  resolvedAt={selectedComplaint.resolved_at}
                  escalationLevel={selectedComplaint.escalation_level}
                />
              </div>

              <div className="p-3 rounded-lg bg-gray-950/80 light:bg-white border border-gray-800 light:border-slate-200 flex items-center justify-between text-xs">
                <span className="text-gray-400 light:text-slate-600 flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4 text-amber-500" /> Escalation Tier:
                </span>
                <span className={`font-bold px-2.5 py-0.5 rounded-full ${
                  selectedComplaint.escalation_level.includes('Level 3') ? 'bg-red-500/20 text-red-400 light:text-red-600 border border-red-500/40' :
                  selectedComplaint.escalation_level.includes('Level 2') ? 'bg-amber-500/20 text-amber-300 light:text-amber-700 border border-amber-500/40' :
                  'bg-indigo-500/20 text-indigo-300 light:text-indigo-700'
                }`}>
                  {selectedComplaint.escalation_level}
                </span>
              </div>
            </div>

            {/* SECTION 7: Resolution Proof Workflow */}
            <div className="space-y-3 pt-2">
              <h3 className="text-xs font-bold text-gray-300 light:text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                <FileCheck className="w-4 h-4 text-emerald-400 light:text-emerald-600" /> 📷 Authority Resolution & Proof Workflow
              </h3>

              {selectedComplaint.status === 'Resolved' ? (
                
                <div className="p-5 rounded-2xl bg-emerald-950/20 light:bg-emerald-50 border-2 border-emerald-500/40 space-y-4">
                  <div className="flex items-center justify-between border-b border-emerald-800/40 light:border-emerald-200 pb-3">
                    <div className="flex items-center space-x-2 text-emerald-400 light:text-emerald-700 font-bold text-sm">
                      <CheckCircle2 className="w-5 h-5" />
                      <span>Resolved ✓</span>
                    </div>
                    <span className="text-xs text-emerald-300 light:text-emerald-700 font-mono">
                      {selectedComplaint.resolved_at ? new Date(selectedComplaint.resolved_at).toLocaleString() : 'Resolved'}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {selectedComplaint.resolution_photo && (
                      <div className="space-y-1">
                        <p className="text-[11px] font-semibold text-gray-400 light:text-slate-600">📷 Resolution Proof Photo:</p>
                        <img 
                          src={selectedComplaint.resolution_photo} 
                          alt="Resolution Proof" 
                          className="w-full h-40 object-cover rounded-xl border border-emerald-800/60 light:border-emerald-300 shadow-md"
                        />
                      </div>
                    )}

                    <div className="space-y-3 text-xs">
                      <div>
                        <p className="text-gray-400 light:text-slate-600 font-medium">Resolution Notes:</p>
                        <p className="text-gray-200 light:text-slate-800 font-medium mt-1 bg-gray-900/80 light:bg-white p-3 rounded-xl border border-gray-800 light:border-slate-200 leading-relaxed">
                          "{selectedComplaint.resolution_note || 'Issue completed by ward unit.'}"
                        </p>
                      </div>

                      <div>
                        <p className="text-gray-400 light:text-slate-600 font-medium">Resolved By Authority:</p>
                        <p className="text-emerald-300 light:text-emerald-700 font-bold mt-0.5">
                          {selectedComplaint.resolved_by || 'Ward Municipal Officer'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

              ) : (

                <form onSubmit={handleAuthorityResolveSubmit} className="p-5 rounded-2xl bg-gray-900 light:bg-slate-100 border border-gray-800 light:border-slate-200 space-y-4">
                  <div className="flex items-center space-x-2 text-indigo-300 light:text-indigo-700 font-bold text-xs">
                    <Camera className="w-4 h-4 text-indigo-400 light:text-indigo-600" />
                    <span>Upload Resolution Proof & Mark Ticket Resolved</span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[11px] text-gray-400 light:text-slate-600 font-semibold mb-1">Officer Name / ID</label>
                      <input
                        type="text"
                        required
                        value={resolutionForm.resolved_by}
                        onChange={(e) => setResolutionForm({ ...resolutionForm, resolved_by: e.target.value })}
                        className="w-full px-3 py-2 rounded-xl bg-gray-800 light:bg-white border border-gray-700 light:border-slate-300 text-xs text-white light:text-slate-900 focus:outline-none shadow-sm"
                      />
                    </div>

                    <div>
                      <label className="block text-[11px] text-gray-400 light:text-slate-600 font-semibold mb-1">Upload Photo File or Pick Sample</label>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handlePhotoFileUpload}
                        className="w-full text-xs text-gray-400 light:text-slate-600 file:mr-2 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-600 file:text-white"
                      />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <p className="text-[10px] text-gray-400 light:text-slate-500">Quick Sample Proof Photos for Demo:</p>
                    <div className="flex flex-wrap gap-2">
                      {sampleProofPhotos.map((sample, idx) => (
                        <button
                          type="button"
                          key={idx}
                          onClick={() => setResolutionForm({ ...resolutionForm, resolution_photo: sample.url })}
                          className={`px-2.5 py-1 rounded-lg text-[10px] font-semibold border transition-colors ${
                            resolutionForm.resolution_photo === sample.url 
                              ? 'bg-indigo-600 text-white border-indigo-500' 
                              : 'bg-gray-800 light:bg-white text-gray-400 light:text-slate-700 border-gray-700 light:border-slate-300 hover:text-white light:hover:text-slate-900'
                          }`}
                        >
                          {sample.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-[11px] text-gray-400 light:text-slate-600 font-semibold mb-1">Resolution Work Note</label>
                    <textarea
                      rows={2}
                      placeholder="e.g. Replaced broken valve, cleared debris, verified safety..."
                      value={resolutionForm.resolution_note}
                      onChange={(e) => setResolutionForm({ ...resolutionForm, resolution_note: e.target.value })}
                      className="w-full px-3 py-2 rounded-xl bg-gray-800 light:bg-white border border-gray-700 light:border-slate-300 text-xs text-white light:text-slate-900 focus:outline-none shadow-sm"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={resolving}
                    className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/30 transition-all flex items-center justify-center space-x-2"
                  >
                    {resolving ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <Check className="w-4 h-4" />
                        <span>Confirm Authority Resolution & Mark Resolved ✓</span>
                      </>
                    )}
                  </button>

                </form>

              )}

            </div>

          </div>
        </div>
      )}

    </div>
  );
}
