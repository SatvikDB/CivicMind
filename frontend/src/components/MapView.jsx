import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { fetchMapComplaints, updateComplaintStatus } from '../api';
import SLACountdown from './SLACountdown';
import { 
  Filter, 
  MapPin, 
  RefreshCw, 
  Sparkles, 
  AlertCircle, 
  CheckCircle, 
  Search,
  Check,
  Clock,
  Layers,
  ShieldAlert
} from 'lucide-react';

const createCustomIcon = (priority, status) => {
  let color = '#3b82f6';
  if (status === 'Resolved') {
    color = '#10b981';
  } else if (status === 'OVERDUE' || status === 'ESCALATED') {
    color = '#ef4444';
  } else if (priority === 'Critical') {
    color = '#ef4444';
  } else if (priority === 'High') {
    color = '#f97316';
  } else if (priority === 'Medium') {
    color = '#f59e0b';
  }

  const svgIcon = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${color}" width="32" height="32" stroke="#ffffff" stroke-width="1.5">
      <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
    </svg>
  `;

  return L.divIcon({
    html: svgIcon,
    className: (priority === 'Critical' || status === 'OVERDUE' || status === 'ESCALATED') && status !== 'Resolved' ? 'pulse-critical' : '',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32]
  });
};

export default function MapView() {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);

  const [filters, setFilters] = useState({
    search: '',
    category: 'All',
    priority: 'All',
    status: 'All'
  });

  const categories = ['All', 'Road', 'Water', 'Waste', 'Streetlight', 'Drainage', 'Safety', 'Other'];
  const priorityLevels = ['All', 'Critical', 'High', 'Medium', 'Low'];
  const statusLevels = ['All', 'Pending', 'In Progress', 'OVERDUE', 'Resolved'];

  const loadMapData = async () => {
    setLoading(true);
    try {
      const data = await fetchMapComplaints({
        category: filters.category,
        priority: filters.priority,
        status: filters.status
      });
      
      let filtered = data;
      if (filters.search.trim()) {
        const q = filters.search.toLowerCase();
        filtered = filtered.filter(c => 
          c.title.toLowerCase().includes(q) || 
          c.location.toLowerCase().includes(q) || 
          c.description.toLowerCase().includes(q)
        );
      }

      setComplaints(filtered);
    } catch (err) {
      console.error("Failed to load map data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMapData();
  }, [filters.category, filters.priority, filters.status]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadMapData();
  };

  const handleStatusChange = async (id, newStatus) => {
    setUpdatingId(id);
    try {
      await updateComplaintStatus(id, newStatus);
      await loadMapData();
    } catch (err) {
      alert(`Failed to update status: ${err.message}`);
    } finally {
      setUpdatingId(null);
    }
  };

  const centerPos = [12.3100, 76.6400];

  return (
    <div className="space-y-6 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-gray-800 light:border-slate-200">
        <div>
          <h1 className="text-3xl font-extrabold text-white light:text-slate-900 tracking-tight">Interactive Map Intelligence</h1>
          <p className="text-gray-400 light:text-slate-600 text-sm mt-1">Spatial GIS visualization with 48h SLA countdown markers and escalation tags.</p>
        </div>

        <div className="flex items-center space-x-2 text-xs font-semibold text-gray-400 light:text-slate-600 bg-gray-900 light:bg-white px-3.5 py-1.5 rounded-xl border border-gray-800 light:border-slate-200 shadow-sm">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 light:bg-emerald-500 animate-pulse"></span>
          <span>{complaints.length} Map Markers Active</span>
        </div>
      </div>

      {/* FILTER CONTROL BAR */}
      <div className="glass-panel p-4 rounded-2xl border border-gray-800 light:border-slate-200 flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-gray-400 light:text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search location or title..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-gray-900 light:bg-white border border-gray-700 light:border-slate-300 text-xs text-white light:text-slate-900 placeholder-gray-500 light:placeholder-slate-400 focus:outline-none focus:border-indigo-500 shadow-sm"
          />
        </form>

        {/* Dropdowns */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          
          <div className="flex items-center space-x-1.5">
            <span className="text-xs text-gray-400 light:text-slate-600 font-medium">Category:</span>
            <select
              value={filters.category}
              onChange={(e) => setFilters({ ...filters, category: e.target.value })}
              className="px-3 py-1.5 rounded-xl bg-gray-900 light:bg-white border border-gray-700 light:border-slate-300 text-xs text-white light:text-slate-900 focus:outline-none shadow-sm"
            >
              {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
            </select>
          </div>

          <div className="flex items-center space-x-1.5">
            <span className="text-xs text-gray-400 light:text-slate-600 font-medium">Priority:</span>
            <select
              value={filters.priority}
              onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
              className="px-3 py-1.5 rounded-xl bg-gray-900 light:bg-white border border-gray-700 light:border-slate-300 text-xs text-white light:text-slate-900 focus:outline-none shadow-sm"
            >
              {priorityLevels.map(prio => <option key={prio} value={prio}>{prio}</option>)}
            </select>
          </div>

          <div className="flex items-center space-x-1.5">
            <span className="text-xs text-gray-400 light:text-slate-600 font-medium">Status:</span>
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              className="px-3 py-1.5 rounded-xl bg-gray-900 light:bg-white border border-gray-700 light:border-slate-300 text-xs text-white light:text-slate-900 focus:outline-none shadow-sm"
            >
              {statusLevels.map(st => <option key={st} value={st}>{st}</option>)}
            </select>
          </div>

          <button
            onClick={loadMapData}
            className="p-2 rounded-xl bg-gray-800 light:bg-white text-gray-300 light:text-slate-700 hover:bg-gray-700 light:hover:bg-slate-100 transition-colors border border-gray-700 light:border-slate-200 shadow-sm"
            title="Refresh Map"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

      </div>

      {/* MAP CANVAS */}
      <div className="h-[550px] w-full rounded-2xl overflow-hidden border border-gray-800 light:border-slate-200 shadow-2xl relative">
        <MapContainer
          center={centerPos}
          zoom={13}
          scrollWheelZoom={true}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {complaints.map((item) => (
            <Marker
              key={item.id}
              position={[item.latitude, item.longitude]}
              icon={createCustomIcon(item.priority_level, item.status)}
            >
              <Popup>
                <div className="space-y-3 min-w-[250px] max-w-[290px]">
                  
                  <div className="flex items-center justify-between border-b border-gray-800 light:border-slate-200 pb-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 light:bg-indigo-50 text-indigo-300 light:text-indigo-700 border border-indigo-500/30 light:border-indigo-200">
                      {item.category}
                    </span>

                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      item.priority_level === 'Critical' ? 'bg-red-500/20 text-red-400 light:text-red-600 border border-red-500/40' :
                      item.priority_level === 'High' ? 'bg-amber-500/20 text-amber-400 light:text-amber-600 border border-amber-500/40' :
                      'bg-blue-500/20 text-blue-400 light:text-blue-600'
                    }`}>
                      Priority: {item.priority_score}
                    </span>
                  </div>

                  <div>
                    <h4 className="font-bold text-white light:text-slate-900 text-xs leading-snug">{item.title}</h4>
                    <p className="text-[11px] text-gray-400 light:text-slate-500 mt-0.5 flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-emerald-400 light:text-emerald-600 shrink-0" />
                      <span className="truncate">{item.location}</span>
                    </p>
                  </div>

                  <div className="pt-1">
                    <SLACountdown 
                      deadlineAt={item.deadline_at} 
                      status={item.status}
                      createdAt={item.created_at}
                      resolvedAt={item.resolved_at}
                      escalationLevel={item.escalation_level}
                    />
                  </div>

                  <div className="pt-2 border-t border-gray-800 light:border-slate-200">
                    <p className="text-[10px] text-gray-400 light:text-slate-500 font-medium mb-1.5">Change Status:</p>
                    <div className="grid grid-cols-3 gap-1">
                      {['Pending', 'In Progress', 'Resolved'].map((st) => (
                        <button
                          key={st}
                          disabled={updatingId === item.id || item.status === st}
                          onClick={() => handleStatusChange(item.id, st)}
                          className={`py-1 text-[10px] font-semibold rounded transition-colors ${
                            item.status === st
                              ? 'bg-indigo-600 text-white'
                              : 'bg-gray-800 light:bg-slate-100 text-gray-400 light:text-slate-700 hover:bg-gray-700 light:hover:bg-slate-200'
                          }`}
                        >
                          {st === 'In Progress' ? 'Progress' : st}
                        </button>
                      ))}
                    </div>
                  </div>

                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {/* LEGEND BAR */}
      <div className="glass-card p-4 rounded-xl border border-gray-800 light:border-slate-200 flex flex-wrap items-center justify-between text-xs text-gray-400 light:text-slate-600 gap-4 shadow-sm">
        <span className="font-semibold text-gray-300 light:text-slate-800">Marker Legend:</span>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-red-500"></span>
          <span>Critical / Overdue Incident</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-amber-500"></span>
          <span>Medium Priority</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-blue-500"></span>
          <span>Low Priority</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
          <span>Resolved Issue</span>
        </div>
      </div>

    </div>
  );
}
