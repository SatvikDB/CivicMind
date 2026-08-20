import React, { useState } from 'react';
import { loginUser } from '../api';
import {
  Building2,
  Sparkles,
  Shield,
  User,
  Mail,
  Lock,
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  AlertCircle,
  Eye,
  EyeOff,
} from 'lucide-react';

export default function LoginPage({ onLoginSuccess, setActiveTab }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingRole, setLoadingRole] = useState(null); // 'citizen' | 'admin'
  const [error, setError] = useState('');

  const handleQuickLogin = async (role) => {
    setError('');
    setLoadingRole(role);
    const targetEmail = role === 'admin' ? 'admin@civicmind.ai' : 'citizen@civicmind.ai';
    try {
      const res = await loginUser(targetEmail, 'password123', role);
      onLoginSuccess(res.user);
    } catch (err) {
      setError(err.message || 'Quick login failed. Please try again.');
    } finally {
      setLoadingRole(null);
    }
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (!email) return;
    setError('');
    setLoading(true);
    try {
      const res = await loginUser(email, password);
      onLoginSuccess(res.user);
    } catch (err) {
      setError(err.message || 'Authentication failed. Check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center py-12 px-4 relative overflow-hidden">

      {/* Background ambient glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-gradient-to-tr from-indigo-500/15 via-purple-500/15 to-pink-500/10 blur-[140px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-indigo-600/10 blur-[100px] rounded-full pointer-events-none" />
      <div className="absolute top-0 right-0 w-[250px] h-[250px] bg-purple-600/10 blur-[100px] rounded-full pointer-events-none" />

      <div className="w-full max-w-5xl relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">

        {/* ── LEFT: Brand Panel ── */}
        <div className="hidden lg:flex flex-col justify-center space-y-8 pr-8">

          {/* Logo */}
          <div
            className="flex items-center space-x-3 cursor-pointer group w-fit"
            onClick={() => setActiveTab('landing')}
          >
            <div className="p-3 rounded-2xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 text-white shadow-xl shadow-indigo-500/30 group-hover:scale-105 transition-transform">
              <Building2 className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-2xl tracking-tight text-slate-900 dark:text-white">CivicMind</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-500/10 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-300 border border-indigo-500/30 flex items-center gap-1">
                  <Sparkles className="w-3 h-3" /> AI
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-gray-400 font-medium">Civic Complaint Intelligence Platform</p>
            </div>
          </div>

          {/* Headline */}
          <div className="space-y-3">
            <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-tight">
              Smart Governance <br />
              <span className="text-gradient">Starts Here.</span>
            </h1>
            <p className="text-slate-600 dark:text-gray-400 text-base leading-relaxed max-w-sm">
              Sign in to report issues, track resolutions, and help build a better city — powered by AI.
            </p>
          </div>

          {/* Feature bullets */}
          <ul className="space-y-4">
            {[
              { icon: BrainCircuit, text: 'AI-powered complaint classification & prioritization', color: 'text-indigo-500' },
              { icon: CheckCircle2, text: '48-hour SLA enforcement with live countdown timers', color: 'text-purple-500' },
              { icon: Shield, text: 'Role-based access: Citizens & Municipal Admins', color: 'text-pink-500' },
            ].map(({ icon: Icon, text, color }) => (
              <li key={text} className="flex items-start space-x-3">
                <div className={`mt-0.5 shrink-0 ${color}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <span className="text-sm text-slate-700 dark:text-gray-300">{text}</span>
              </li>
            ))}
          </ul>

          {/* Stats strip */}
          <div className="grid grid-cols-3 gap-3">
            {[
              { value: '100%', label: 'Auto-classified', color: 'border-indigo-500' },
              { value: '48h', label: 'SLA Window', color: 'border-purple-500' },
              { value: '85%', label: 'Duplicate cut', color: 'border-pink-500' },
            ].map(({ value, label, color }) => (
              <div key={label} className={`glass-card p-3 rounded-xl text-center border-t-2 ${color}`}>
                <p className="text-lg font-extrabold text-slate-900 dark:text-white">{value}</p>
                <p className="text-[10px] text-slate-500 dark:text-gray-400 mt-0.5">{label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* ── RIGHT: Login Card ── */}
        <div className="glass-panel rounded-3xl border border-slate-200 dark:border-gray-800 shadow-2xl p-6 sm:p-8 space-y-6">

          {/* Mobile logo (only visible < lg) */}
          <div className="lg:hidden flex items-center space-x-2 mb-2">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 text-white shadow-lg">
              <Building2 className="w-5 h-5" />
            </div>
            <span className="font-bold text-lg text-slate-900 dark:text-white">CivicMind AI</span>
          </div>

          {/* Header */}
          <div className="space-y-1">
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-indigo-500/10 dark:bg-indigo-500/20 border border-indigo-500/30 text-indigo-600 dark:text-indigo-300 text-[11px] font-semibold">
              <Building2 className="w-3 h-3" />
              <span>CivicMind AI Security Portal</span>
            </div>
            <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white pt-1">Sign In</h2>
            <p className="text-xs text-slate-500 dark:text-gray-400">Choose your role below or enter your credentials.</p>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="flex items-center space-x-2 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-600 dark:text-red-300 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* 1-Click Role Login */}
          <div className="space-y-3">
            <p className="text-[11px] font-bold text-slate-500 dark:text-gray-400 uppercase tracking-wider text-center">
              ⚡ 1-Click Demo Login
            </p>

            <div className="grid grid-cols-2 gap-3">

              {/* Citizen */}
              <button
                type="button"
                disabled={loadingRole !== null || loading}
                onClick={() => handleQuickLogin('citizen')}
                className="relative p-4 rounded-2xl bg-gradient-to-br from-indigo-50 dark:from-indigo-950/60 to-purple-50 dark:to-purple-950/40 border-2 border-indigo-200 dark:border-indigo-800/60 hover:border-indigo-500 dark:hover:border-indigo-500 text-left transition-all shadow-sm hover:scale-[1.02] hover:shadow-indigo-500/20 hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <div className="flex items-center justify-between mb-2.5">
                  <div className="p-2 rounded-xl bg-indigo-600 text-white shadow-md shadow-indigo-500/30">
                    <User className="w-4 h-4" />
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-700 dark:text-indigo-300">
                    Citizen
                  </span>
                </div>
                <p className="text-xs font-bold text-slate-900 dark:text-white">
                  {loadingRole === 'citizen' ? 'Signing in…' : 'Citizen Mode'}
                </p>
                <p className="text-[10px] text-slate-500 dark:text-gray-400 mt-0.5">Report & browse complaints</p>
              </button>

              {/* Admin */}
              <button
                type="button"
                disabled={loadingRole !== null || loading}
                onClick={() => handleQuickLogin('admin')}
                className="relative p-4 rounded-2xl bg-gradient-to-br from-amber-50 dark:from-amber-950/60 to-red-50 dark:to-red-950/40 border-2 border-amber-200 dark:border-amber-800/60 hover:border-amber-500 dark:hover:border-amber-500 text-left transition-all shadow-sm hover:scale-[1.02] hover:shadow-amber-500/20 hover:shadow-lg disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <div className="flex items-center justify-between mb-2.5">
                  <div className="p-2 rounded-xl bg-amber-600 text-white shadow-md shadow-amber-500/30">
                    <Shield className="w-4 h-4" />
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-700 dark:text-amber-300">
                    Admin
                  </span>
                </div>
                <p className="text-xs font-bold text-slate-900 dark:text-white">
                  {loadingRole === 'admin' ? 'Signing in…' : 'Municipal Admin'}
                </p>
                <p className="text-[10px] text-slate-500 dark:text-gray-400 mt-0.5">Full queue & resolution portal</p>
              </button>

            </div>
          </div>

          {/* Divider */}
          <div className="relative flex items-center py-1">
            <div className="flex-grow border-t border-slate-200 dark:border-gray-800" />
            <span className="mx-3 text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-gray-500 flex-shrink">
              Or sign in with email
            </span>
            <div className="flex-grow border-t border-slate-200 dark:border-gray-800" />
          </div>

          {/* Email / Password Form */}
          <form onSubmit={handleFormSubmit} className="space-y-4">

            <div>
              <label className="block text-[11px] font-semibold text-slate-700 dark:text-gray-300 mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 dark:text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-white dark:bg-gray-900/80 border border-slate-300 dark:border-gray-700 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all shadow-sm"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-slate-700 dark:text-gray-300 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 dark:text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-10 py-2.5 rounded-xl bg-white dark:bg-gray-900/80 border border-slate-300 dark:border-gray-700 text-xs text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-gray-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all shadow-sm"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-gray-500 hover:text-slate-600 dark:hover:text-gray-300 transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || loadingRole !== null}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white font-bold text-sm shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:scale-[1.01] transition-all flex items-center justify-center space-x-2 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              <span>{loading ? 'Authenticating…' : 'Sign In'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Demo hint */}
          <p className="text-center text-[11px] text-slate-400 dark:text-gray-500">
            Demo credentials: <span className="font-mono text-indigo-500">citizen@civicmind.ai</span> or{' '}
            <span className="font-mono text-amber-500">admin@civicmind.ai</span> · password{' '}
            <span className="font-mono">password123</span>
          </p>

        </div>
      </div>
    </div>
  );
}
