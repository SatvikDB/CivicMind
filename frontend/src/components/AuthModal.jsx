import React, { useState } from 'react';
import { loginUser } from '../api';
import { 
  ShieldCheck, 
  UserCheck, 
  X, 
  Lock, 
  Mail, 
  ArrowRight, 
  Building2, 
  Sparkles, 
  Check,
  Shield,
  User
} from 'lucide-react';

export default function AuthModal({ isOpen, onClose, onLoginSuccess }) {
  const [email, setEmail] = useState('citizen@civicmind.ai');
  const [password, setPassword] = useState('password123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleQuickRoleLogin = async (role) => {
    setLoading(true);
    setError('');
    const targetEmail = role === 'admin' ? 'admin@civicmind.ai' : 'citizen@civicmind.ai';
    try {
      const res = await loginUser(targetEmail, 'password123', role);
      onLoginSuccess(res.user);
      onClose();
    } catch (err) {
      setError(err.message || 'Login failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleCustomSubmit = async (e) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    setError('');
    try {
      const res = await loginUser(email, password);
      onLoginSuccess(res.user);
      onClose();
    } catch (err) {
      setError(err.message || 'Authentication failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-200 dark:border-gray-800 max-w-md w-full relative shadow-2xl space-y-6">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-6 right-6 p-2 rounded-xl bg-slate-100 dark:bg-gray-800 text-slate-500 dark:text-gray-400 hover:text-slate-900 dark:hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title & Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 dark:bg-indigo-500/20 border border-indigo-500/30 text-indigo-600 dark:text-indigo-300 text-xs font-semibold">
            <Building2 className="w-3.5 h-3.5" />
            <span>CivicMind AI Security Portal</span>
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white">Sign In to CivicMind AI</h2>
          <p className="text-xs text-slate-600 dark:text-gray-400">Select your authorization role or sign in with your credentials.</p>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-600 dark:text-red-300 text-xs text-center font-medium">
            {error}
          </div>
        )}

        {/* 1-CLICK QUICK DEMO LOGIN BUTTONS */}
        <div className="space-y-3 pt-1">
          <p className="text-[11px] font-bold text-slate-500 dark:text-gray-400 uppercase tracking-wider text-center">
            ⚡ 1-Click Quick Demo Authorization
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            
            {/* Citizen Role Button */}
            <button
              type="button"
              disabled={loading}
              onClick={() => handleQuickRoleLogin('citizen')}
              className="p-4 rounded-2xl bg-gradient-to-br from-indigo-50 dark:from-indigo-950/60 to-purple-50 dark:to-purple-950/40 border-2 border-indigo-200 dark:border-indigo-800/60 hover:border-indigo-500 text-left transition-all group shadow-sm hover:scale-[1.02]"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="p-2 rounded-xl bg-indigo-600 text-white shadow-md">
                  <User className="w-4 h-4" />
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-700 dark:text-indigo-300">
                  Citizen
                </span>
              </div>
              <p className="text-xs font-bold text-slate-900 dark:text-white">Citizen Mode</p>
              <p className="text-[10px] text-slate-500 dark:text-gray-400 mt-0.5">Report & Browse Nearby Complaints</p>
            </button>

            {/* Admin Role Button */}
            <button
              type="button"
              disabled={loading}
              onClick={() => handleQuickRoleLogin('admin')}
              className="p-4 rounded-2xl bg-gradient-to-br from-amber-50 dark:from-amber-950/60 to-red-50 dark:to-red-950/40 border-2 border-amber-200 dark:border-amber-800/60 hover:border-amber-500 text-left transition-all group shadow-sm hover:scale-[1.02]"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="p-2 rounded-xl bg-amber-600 text-white shadow-md">
                  <Shield className="w-4 h-4" />
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-700 dark:text-amber-300">
                  Admin
                </span>
              </div>
              <p className="text-xs font-bold text-slate-900 dark:text-white">Municipal Admin</p>
              <p className="text-[10px] text-slate-500 dark:text-gray-400 mt-0.5">Full Queue & Resolution Proof</p>
            </button>

          </div>
        </div>

        {/* Divider */}
        <div className="relative flex py-1 items-center">
          <div className="flex-grow border-t border-slate-200 dark:border-gray-800"></div>
          <span className="flex-shrink mx-3 text-[10px] text-slate-400 dark:text-gray-500 font-semibold uppercase">Or Sign In with Email</span>
          <div className="flex-grow border-t border-slate-200 dark:border-gray-800"></div>
        </div>

        {/* Custom Login Form */}
        <form onSubmit={handleCustomSubmit} className="space-y-4">
          <div>
            <label className="block text-[11px] font-semibold text-slate-700 dark:text-gray-300 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 dark:text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="citizen@civicmind.ai"
                className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-white dark:bg-gray-900 border border-slate-300 dark:border-gray-700 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500 shadow-sm"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-700 dark:text-gray-300 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 dark:text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-white dark:bg-gray-900 border border-slate-300 dark:border-gray-700 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500 shadow-sm"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2"
          >
            <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

      </div>
    </div>
  );
}
