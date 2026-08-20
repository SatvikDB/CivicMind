import React from 'react';
import { 
  Sparkles, 
  ShieldAlert, 
  Layers, 
  Cpu, 
  MapPin, 
  TrendingUp, 
  CheckCircle2, 
  ArrowRight, 
  BrainCircuit, 
  AlertTriangle, 
  Clock, 
  Users,
  FileCheck,
  Building2
} from 'lucide-react';

export default function LandingPage({ setActiveTab }) {
  return (
    <div className="space-y-20 pb-16">
      
      {/* HERO SECTION */}
      <section className="relative overflow-hidden pt-12 pb-16 md:pt-20 md:pb-24">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-indigo-500/20 via-purple-500/20 to-pink-500/10 blur-[120px] rounded-full pointer-events-none"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          
          <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-indigo-500/10 dark:bg-indigo-500/20 border border-indigo-500/30 text-indigo-600 dark:text-indigo-300 text-xs sm:text-sm font-semibold mb-6">
            <Sparkles className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            <span>Next-Generation Civic Intelligence SaaS Platform</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-6 leading-tight">
            Transform Civic Complaints into <br />
            <span className="text-gradient">Real-Time Municipal Intelligence</span>
          </h1>

          <p className="max-w-3xl mx-auto text-lg sm:text-xl text-slate-600 dark:text-gray-300 font-normal leading-relaxed mb-10">
            CivicMind AI automatically classifies citizen reports, detects duplicate complaints using vector embeddings, tracks 48-hour resolution SLA timers, and guides municipal teams with AI action recommendations.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={() => setActiveTab('submit')}
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white font-semibold text-base shadow-xl shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:scale-[1.02] transition-all flex items-center justify-center space-x-2 group"
            >
              <span>Submit a Complaint</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>

            <button
              onClick={() => setActiveTab('dashboard')}
              className="w-full sm:w-auto px-8 py-4 rounded-xl glass-card text-slate-800 dark:text-gray-200 font-semibold text-base border border-slate-300 dark:border-gray-700 hover:bg-slate-200 dark:hover:bg-gray-800 transition-all flex items-center justify-center space-x-2 shadow-sm"
            >
              <TrendingUp className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <span>Executive Dashboard</span>
            </button>
          </div>

          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            <div className="glass-card p-4 rounded-xl text-center border-t-2 border-indigo-500">
              <p className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">100%</p>
              <p className="text-xs text-slate-500 dark:text-gray-400 mt-1">Automated NLP Classification</p>
            </div>
            <div className="glass-card p-4 rounded-xl text-center border-t-2 border-purple-500">
              <p className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">85%</p>
              <p className="text-xs text-slate-500 dark:text-gray-400 mt-1">Duplicate Work Order Reduction</p>
            </div>
            <div className="glass-card p-4 rounded-xl text-center border-t-2 border-pink-500">
              <p className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">48 Hours</p>
              <p className="text-xs text-slate-500 dark:text-gray-400 mt-1">Max Resolution SLA Window</p>
            </div>
            <div className="glass-card p-4 rounded-xl text-center border-t-2 border-emerald-500">
              <p className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">98.4%</p>
              <p className="text-xs text-slate-500 dark:text-gray-400 mt-1">Action Recommendation Accuracy</p>
            </div>
          </div>

        </div>
      </section>

      {/* PROBLEM VS SOLUTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-3">Why Traditional Municipal Portals Fail</h2>
          <p className="text-slate-600 dark:text-gray-400 max-w-2xl mx-auto text-sm sm:text-base">
            Modern cities generate thousands of overlapping citizen complaints daily. Traditional systems suffer from manual bottlenecks and zero automated prioritization.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="glass-card p-8 rounded-2xl border-l-4 border-red-500 relative overflow-hidden">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 rounded-xl bg-red-500/10 dark:bg-red-500/20 text-red-600 dark:text-red-400 border border-red-500/20">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white">Traditional Municipal System</h3>
                <p className="text-xs text-red-600 dark:text-red-400 font-semibold">Manual, Slow & Fragmented</p>
              </div>
            </div>

            <ul className="space-y-4 text-sm text-slate-700 dark:text-gray-300">
              <li className="flex items-start space-x-3">
                <span className="text-red-500 font-bold mt-0.5">✕</span>
                <span>Citizens flood support queues with 20+ duplicate reports for a single pothole.</span>
              </li>
              <li className="flex items-start space-x-3">
                <span className="text-red-500 font-bold mt-0.5">✕</span>
                <span>Critical hazards (live wires, open manholes) get lost in massive pending backlogs.</span>
              </li>
              <li className="flex items-start space-x-3">
                <span className="text-red-500 font-bold mt-0.5">✕</span>
                <span>No automated severity scoring or standardized department dispatching.</span>
              </li>
              <li className="flex items-start space-x-3">
                <span className="text-red-500 font-bold mt-0.5">✕</span>
                <span>City administrators lack spatial GIS visual dashboards for ward analytics.</span>
              </li>
            </ul>
          </div>

          <div className="glass-card p-8 rounded-2xl border-l-4 border-indigo-500 relative overflow-hidden bg-indigo-50/50 dark:bg-indigo-950/20">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 rounded-xl bg-indigo-500/10 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 border border-indigo-500/30">
                <BrainCircuit className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white">CivicMind AI Platform</h3>
                <p className="text-xs text-indigo-600 dark:text-indigo-400 font-semibold">Automated Intelligence & 48h SLA Action</p>
              </div>
            </div>

            <ul className="space-y-4 text-sm text-slate-700 dark:text-gray-300">
              <li className="flex items-start space-x-3">
                <CheckCircle2 className="w-5 h-5 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
                <span><strong className="text-slate-900 dark:text-white">Cosine Similarity Engine:</strong> Instantly detects duplicate complaints (e.g. 88% match) and aggregates community urgency.</span>
              </li>
              <li className="flex items-start space-x-3">
                <CheckCircle2 className="w-5 h-5 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
                <span><strong className="text-slate-900 dark:text-white">48-Hour SLA Timers:</strong> Assigns live resolution countdowns and automatically escalates breached tickets.</span>
              </li>
              <li className="flex items-start space-x-3">
                <CheckCircle2 className="w-5 h-5 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
                <span><strong className="text-slate-900 dark:text-white">AI Action & Proof Workflow:</strong> Synthesizes dispatcher recommendations and captures resolution photo proofs.</span>
              </li>
              <li className="flex items-start space-x-3">
                <CheckCircle2 className="w-5 h-5 text-indigo-600 dark:text-indigo-400 shrink-0 mt-0.5" />
                <span><strong className="text-slate-900 dark:text-white">Interactive Leaflet GIS Map:</strong> Color-coded priority pins allow administrators to trigger instant status updates.</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 border-t border-slate-200 dark:border-gray-800 text-center sm:text-left flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 dark:text-gray-500 gap-4">
        <div className="flex items-center space-x-2">
          <Building2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          <span className="font-semibold text-slate-800 dark:text-gray-300">CivicMind AI Platform</span>
          <span>• Hackathon SaaS Edition</span>
        </div>
        <p>© 2026 CivicMind AI • Powered by FastAPI, Scikit-learn & React Leaflet</p>
      </footer>

    </div>
  );
}
