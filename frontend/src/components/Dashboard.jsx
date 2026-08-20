import React, { useState, useEffect } from 'react';
import { 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  AreaChart, 
  Area 
} from 'recharts';
import { fetchDashboardAnalytics } from '../api';
import SLACountdown from './SLACountdown';
import { 
  ClipboardList, 
  AlertOctagon, 
  Copy, 
  CheckCircle, 
  Sparkles, 
  RefreshCw, 
  TrendingUp, 
  Flame, 
  Clock,
  AlertTriangle,
  ShieldAlert,
  MapPin,
  ArrowRight
} from 'lucide-react';

const CATEGORY_COLORS = {
  Road: '#6366f1',
  Water: '#06b6d4',
  Waste: '#f59e0b',
  Streetlight: '#eab308',
  Drainage: '#a855f7',
  Safety: '#ef4444',
  Other: '#6b7280'
};

const PRIORITY_COLORS = {
  Critical: '#ef4444',
  High: '#f97316',
  Medium: '#eab308',
  Low: '#3b82f6'
};

export default function Dashboard({ setActiveTab }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const analytics = await fetchDashboardAnalytics();
      setData(analytics);
      setError('');
    } catch (err) {
      console.error(err);
      setError('Failed to load dashboard metrics. Verify backend server status.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
        <RefreshCw className="w-8 h-8 text-indigo-500 animate-spin" />
        <p className="text-gray-400 light:text-slate-600 text-sm font-medium">Calculating SLA Timers & Municipal Analytics...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="glass-panel p-8 rounded-2xl text-center space-y-4 max-w-xl mx-auto border border-red-500/30">
        <AlertOctagon className="w-12 h-12 text-red-500 mx-auto" />
        <h2 className="text-xl font-bold text-white light:text-slate-900">Dashboard Offline</h2>
        <p className="text-sm text-gray-400 light:text-slate-600">{error || 'No analytics data available.'}</p>
        <button
          onClick={loadDashboard}
          className="px-5 py-2.5 rounded-xl bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500 transition-colors"
        >
          Retry Load
        </button>
      </div>
    );
  }

  const { stats, category_distribution, priority_distribution, complaint_trends, smart_insights, needs_immediate_attention } = data;

  return (
    <div className="space-y-8 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-800 light:border-slate-200">
        <div>
          <h1 className="text-3xl font-extrabold text-white light:text-slate-900 tracking-tight">Executive Analytics & SLA Control</h1>
          <p className="text-gray-400 light:text-slate-600 text-sm mt-1">48-hour SLA tracking, automatic escalation monitoring, and resolution metrics.</p>
        </div>

        <button
          onClick={loadDashboard}
          className="px-4 py-2 rounded-xl glass-card text-xs font-semibold text-gray-300 light:text-slate-700 hover:bg-gray-800 light:hover:bg-slate-200 transition-colors flex items-center space-x-2 self-start sm:self-auto shadow-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Intelligence</span>
        </button>
      </div>

      {/* KPI METRICS GRID (6 Cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        
        {/* Total Complaints */}
        <div className="glass-card p-5 rounded-2xl border-l-4 border-indigo-500">
          <p className="text-xs font-semibold text-gray-400 light:text-slate-500 uppercase tracking-wider">Total Incidents</p>
          <p className="text-2xl font-extrabold text-white light:text-slate-900 mt-1">{stats.total_complaints}</p>
          <p className="text-[10px] text-gray-400 light:text-slate-500 mt-2">All ward submissions</p>
        </div>

        {/* Active SLA Timers */}
        <div className="glass-card p-5 rounded-2xl border-l-4 border-cyan-500">
          <p className="text-xs font-semibold text-cyan-400 light:text-cyan-600 uppercase tracking-wider">Active SLA Timers</p>
          <p className="text-2xl font-extrabold text-cyan-300 light:text-cyan-700 mt-1">{stats.active_sla_timers}</p>
          <p className="text-[10px] text-cyan-200 light:text-cyan-600 mt-2">Within 48h deadline</p>
        </div>

        {/* Overdue SLA Complaints */}
        <div className="glass-card p-5 rounded-2xl border-l-4 border-red-500 bg-red-950/20 light:bg-red-50/50">
          <p className="text-xs font-semibold text-red-400 light:text-red-600 uppercase tracking-wider">SLA Overdue</p>
          <p className="text-2xl font-extrabold text-red-400 light:text-red-600 mt-1">{stats.overdue_count}</p>
          <p className="text-[10px] text-red-300 light:text-red-600 mt-2 font-bold flex items-center gap-1">
            <AlertTriangle className="w-3 h-3 text-red-500" /> Breached 48h SLA
          </p>
        </div>

        {/* Escalated Complaints */}
        <div className="glass-card p-5 rounded-2xl border-l-4 border-amber-500 bg-amber-950/20 light:bg-amber-50/50">
          <p className="text-xs font-semibold text-amber-400 light:text-amber-600 uppercase tracking-wider">Escalated Tickets</p>
          <p className="text-2xl font-extrabold text-amber-400 light:text-amber-600 mt-1">{stats.escalated_count}</p>
          <p className="text-[10px] text-amber-300 light:text-amber-600 mt-2 flex items-center gap-1">
            <ShieldAlert className="w-3 h-3 text-amber-500" /> L2/L3 Officer Review
          </p>
        </div>

        {/* Resolution Rate */}
        <div className="glass-card p-5 rounded-2xl border-l-4 border-emerald-500">
          <p className="text-xs font-semibold text-emerald-400 light:text-emerald-600 uppercase tracking-wider">Resolution Rate</p>
          <p className="text-2xl font-extrabold text-emerald-400 light:text-emerald-600 mt-1">{stats.resolution_rate}%</p>
          <p className="text-[10px] text-emerald-300 light:text-emerald-600 mt-2">{stats.resolved_count} issues resolved</p>
        </div>

        {/* Avg Resolution Time */}
        <div className="glass-card p-5 rounded-2xl border-l-4 border-purple-500">
          <p className="text-xs font-semibold text-purple-400 light:text-purple-600 uppercase tracking-wider">Avg Repair Time</p>
          <p className="text-2xl font-extrabold text-purple-300 light:text-purple-700 mt-1">{stats.avg_resolution_hours}<span className="text-xs text-gray-400 light:text-slate-500 font-normal"> hrs</span></p>
          <p className="text-[10px] text-purple-200 light:text-purple-600 mt-2">Speed to resolution</p>
        </div>

      </div>

      {/* PROMINENT "NEEDS IMMEDIATE ATTENTION" CALLOUT SECTION */}
      {needs_immediate_attention && needs_immediate_attention.length > 0 && (
        <div className="glass-panel p-6 rounded-2xl border-2 border-red-500/40 bg-gradient-to-r from-red-950/30 light:from-red-50 via-gray-900 light:via-slate-50 to-gray-900 light:to-slate-50 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="p-2 rounded-lg bg-red-500/20 text-red-500 pulse-critical">
                <AlertOctagon className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-lg font-extrabold text-white light:text-slate-900 flex items-center gap-2">
                  Needs Immediate Attention
                  <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-red-500/20 text-red-300 light:text-red-600 border border-red-500/40">
                    {needs_immediate_attention.length} Critical / Overdue
                  </span>
                </h2>
                <p className="text-xs text-gray-400 light:text-slate-600">High severity & SLA breached incidents requiring emergency municipal action</p>
              </div>
            </div>

            <button
              onClick={() => setActiveTab('management')}
              className="text-xs font-bold text-red-400 light:text-red-600 hover:text-red-300 flex items-center gap-1"
            >
              <span>View All in Admin</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {needs_immediate_attention.map((item) => (
              <div key={item.id} className="glass-card p-4 rounded-xl border border-red-800/60 light:border-red-300 bg-gray-900/90 light:bg-white space-y-3 shadow-sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-red-500/20 text-red-400 light:text-red-600 border border-red-500/40">
                    Priority Score: {item.priority_score}
                  </span>
                  <span className="text-[10px] font-bold text-gray-400 light:text-slate-500">{item.category}</span>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-white light:text-slate-900 line-clamp-1">{item.title}</h4>
                  <p className="text-xs text-gray-400 light:text-slate-500 mt-0.5 flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-emerald-400 light:text-emerald-600" /> {item.location}
                  </p>
                </div>

                <div className="pt-2 border-t border-gray-800 light:border-slate-200 flex items-center justify-between">
                  <SLACountdown 
                    deadlineAt={item.deadline_at} 
                    status={item.status}
                    createdAt={item.created_at}
                    escalationLevel={item.escalation_level}
                  />
                  
                  <button
                    onClick={() => setActiveTab('management')}
                    className="px-2.5 py-1 rounded-lg bg-indigo-600 text-white text-[10px] font-bold hover:bg-indigo-500"
                  >
                    Action →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SMART INSIGHTS BANNER */}
      {smart_insights && smart_insights.length > 0 && (
        <div className="glass-panel p-6 rounded-2xl border border-indigo-500/30 bg-gradient-to-r from-indigo-950/40 light:from-indigo-50/60 via-purple-950/20 light:via-purple-50/40 to-gray-900 light:to-slate-50 space-y-3">
          <div className="flex items-center space-x-2 text-indigo-300 light:text-indigo-700 font-bold text-xs uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-indigo-400 light:text-indigo-600" />
            <span>AI Smart Insights & SLA Feed</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {smart_insights.map((insight, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-gray-900/80 light:bg-white border border-gray-800 light:border-slate-200 text-xs sm:text-sm text-gray-200 light:text-slate-800 flex items-start space-x-2 shadow-sm">
                <span className="text-indigo-400 light:text-indigo-600 mt-0.5">•</span>
                <span className="leading-snug">{insight}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* CHARTS GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Category Distribution Pie Chart */}
        <div className="glass-panel p-6 rounded-2xl border border-gray-800 light:border-slate-200 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white light:text-slate-900 mb-1">Category Distribution</h3>
            <p className="text-xs text-gray-400 light:text-slate-500 mb-4">Breakdown by issue domain</p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={category_distribution}
                  dataKey="count"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={4}
                >
                  {category_distribution.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={CATEGORY_COLORS[entry.category] || '#6366f1'} 
                    />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', borderRadius: '0.5rem', color: '#f8fafc' }}
                />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Priority Bar Chart */}
        <div className="glass-panel p-6 rounded-2xl border border-gray-800 light:border-slate-200 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white light:text-slate-900 mb-1">Priority Classification</h3>
            <p className="text-xs text-gray-400 light:text-slate-500 mb-4">Severity distribution</p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={priority_distribution}>
                <XAxis dataKey="priority_level" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', borderRadius: '0.5rem', color: '#f8fafc' }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {priority_distribution.map((entry, index) => (
                    <Cell 
                      key={`bar-${index}`} 
                      fill={PRIORITY_COLORS[entry.priority_level] || '#6366f1'} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 7-Day Trend Area Chart */}
        <div className="glass-panel p-6 rounded-2xl border border-gray-800 light:border-slate-200 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-white light:text-slate-900 mb-1">7-Day Incident Volume</h3>
            <p className="text-xs text-gray-400 light:text-slate-500 mb-4">Total vs high priority items</p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={complaint_trends}>
                <defs>
                  <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorHigh" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#475569', borderRadius: '0.5rem', color: '#f8fafc' }}
                />
                <Area type="monotone" dataKey="count" stroke="#6366f1" fillOpacity={1} fill="url(#colorTotal)" name="Total Reports" />
                <Area type="monotone" dataKey="high_priority" stroke="#ef4444" fillOpacity={1} fill="url(#colorHigh)" name="Critical Items" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

    </div>
  );
}
