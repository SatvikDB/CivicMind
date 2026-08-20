import React from 'react';
import { 
  Building2, 
  PlusCircle, 
  LayoutDashboard, 
  MapPin, 
  ClipboardList, 
  Sparkles,
  Home,
  Sun,
  Moon,
  User,
  Shield,
  LogIn,
  LogOut,
  Users,
  Compass
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, theme, setTheme, currentUser, onOpenAuth, onLogout }) {
  const isCitizen = currentUser?.role === 'citizen';
  const isAdmin = currentUser?.role === 'admin';
  const isLoggedIn = !!currentUser;

  const citizenNavItems = [
    { id: 'landing', label: 'Home', icon: Home },
    { id: 'submit', label: 'Report Issue', icon: PlusCircle, highlight: true },
    { id: 'browse', label: 'Browse Feed', icon: Compass },
    { id: 'map', label: 'Live Map', icon: MapPin },
  ];

  const adminNavItems = [
    { id: 'landing', label: 'Home', icon: Home },
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'map', label: 'Live Map', icon: MapPin },
    { id: 'management', label: 'Admin Portal', icon: ClipboardList },
  ];

  const guestNavItems = [
    { id: 'landing', label: 'Home', icon: Home },
  ];

  const navItems = isAdmin ? adminNavItems : isCitizen ? citizenNavItems : guestNavItems;

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
  };

  return (
    <header className="sticky top-0 z-40 glass-panel border-b border-slate-200 dark:border-gray-800 backdrop-blur-md transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Logo */}
          <div 
            className="flex items-center space-x-3 cursor-pointer group"
            onClick={() => setActiveTab('landing')}
          >
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 text-white shadow-lg shadow-indigo-500/25 group-hover:scale-105 transition-transform duration-200">
              <Building2 className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-xl tracking-tight text-slate-900 dark:text-white">CivicMind</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-500/10 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-300 border border-indigo-500/30 flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-indigo-600 dark:text-indigo-400" /> AI
                </span>
              </div>
              <p className="text-[10px] text-slate-500 dark:text-gray-400 font-medium tracking-wide">Civic Complaint Intelligence Platform</p>
            </div>
          </div>

          {/* Navigation Links (Role Scoped) */}
          <nav className="hidden md:flex items-center space-x-1 bg-slate-200/80 dark:bg-gray-900/80 p-1.5 rounded-xl border border-slate-300/80 dark:border-gray-800/80">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              
              if (item.highlight) {
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`flex items-center space-x-1.5 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                      isActive 
                        ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/30' 
                        : 'bg-indigo-600/10 dark:bg-indigo-600/20 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-600/20 dark:hover:bg-indigo-600/30 border border-indigo-500/30'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </button>
                );
              }

              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive 
                      ? 'bg-white dark:bg-gray-800 text-indigo-600 dark:text-indigo-400 border border-slate-300 dark:border-gray-700 shadow-sm font-bold' 
                      : 'text-slate-700 dark:text-gray-400 hover:text-slate-900 dark:hover:text-gray-200 hover:bg-slate-300/60 dark:hover:bg-gray-800/50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-500 dark:text-gray-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* User Profile, Role Badge & Theme Controls */}
          <div className="flex items-center space-x-3">
            
            {/* Login Button or Active Role Badge */}
            {!isLoggedIn ? (
              <button
                onClick={() => setActiveTab('login')}
                className="flex items-center space-x-2 px-3 py-1.5 rounded-xl border text-xs font-bold transition-all shadow-sm bg-indigo-600 text-white border-indigo-600 hover:bg-indigo-500"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Sign In</span>
              </button>
            ) : (
              <button
                onClick={onOpenAuth}
                className={`flex items-center space-x-2 px-3 py-1.5 rounded-xl border text-xs font-bold transition-all shadow-sm ${
                  isAdmin 
                    ? 'bg-amber-500/10 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 border-amber-500/30 dark:border-amber-800/50 hover:bg-amber-500/20' 
                    : 'bg-indigo-500/10 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 border-indigo-500/30 dark:border-indigo-800/50 hover:bg-indigo-500/20'
                }`}
                title="Click to switch role or sign in"
              >
                {isAdmin ? (
                  <Shield className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                ) : (
                  <User className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                )}
                <span className="hidden sm:inline font-semibold">{currentUser?.name || (isAdmin ? 'Admin' : 'Citizen')}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded-md bg-white/60 dark:bg-gray-800/80 font-mono uppercase">
                  {currentUser?.role || 'Citizen'}
                </span>
              </button>
            )}

            {/* Logout Button (only when logged in) */}
            {isLoggedIn && (
              <button
                onClick={onLogout}
                className="p-2.5 rounded-xl glass-card text-slate-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors flex items-center justify-center border border-slate-300 dark:border-gray-800"
                title="Log Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            )}

            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              className="p-2.5 rounded-xl glass-card text-slate-700 dark:text-gray-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200 dark:hover:bg-gray-800 transition-colors flex items-center justify-center border border-slate-300 dark:border-gray-800"
              title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
            >
              {theme === 'dark' ? (
                <Sun className="w-4 h-4 text-amber-400" />
              ) : (
                <Moon className="w-4 h-4 text-indigo-600" />
              )}
            </button>

            {/* Mobile Nav Triggers */}
            <div className="md:hidden flex space-x-1">
              {isLoggedIn ? (
                <button
                  onClick={() => setActiveTab(isAdmin ? 'dashboard' : 'browse')}
                  className="p-2 rounded-lg bg-indigo-600 text-white text-xs font-medium"
                >
                  {isAdmin ? 'Dashboard' : 'Browse'}
                </button>
              ) : (
                <button
                  onClick={() => setActiveTab('login')}
                  className="p-2 rounded-lg bg-indigo-600 text-white text-xs font-medium"
                >
                  Sign In
                </button>
              )}
            </div>

          </div>

        </div>
      </div>
    </header>
  );
}
