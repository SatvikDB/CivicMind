import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import LandingPage from './components/LandingPage';
import LoginPage from './components/LoginPage';
import ComplaintForm from './components/ComplaintForm';
import CitizenBrowseFeed from './components/CitizenBrowseFeed';
import Dashboard from './components/Dashboard';
import MapView from './components/MapView';
import ComplaintManagement from './components/ComplaintManagement';
import AuthModal from './components/AuthModal';

export default function App() {
  const [activeTab, setActiveTab] = useState(() => {
    const saved = localStorage.getItem('civicmind-user');
    if (saved) {
      try {
        const user = JSON.parse(saved);
        return user?.role === 'admin' ? 'dashboard' : 'landing';
      } catch (e) { /* fallback */ }
    }
    return 'login';
  });
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('civicmind-theme') || 'dark';
  });

  const [currentUser, setCurrentUser] = useState(() => {
    const saved = localStorage.getItem('civicmind-user');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) { /* fallback */ }
    }
    return null; // No default user — send to login page
  });

  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'light') {
      root.classList.add('light');
      root.classList.remove('dark');
    } else {
      root.classList.add('dark');
      root.classList.remove('light');
    }
    localStorage.setItem('civicmind-theme', theme);
  }, [theme]);

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    localStorage.setItem('civicmind-user', JSON.stringify(user));
    if (user.role === 'admin') {
      setActiveTab('dashboard');
    } else {
      setActiveTab('browse');
    }
  };

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem('civicmind-user');
    setActiveTab('login');
  };

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark bg-[#0b0f19] text-white' : 'light bg-slate-100 text-slate-900'} flex flex-col font-sans selection:bg-indigo-500 selection:text-white transition-colors duration-300`}>
      
      {/* Sticky Navigation Header */}
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        theme={theme}
        setTheme={setTheme}
        currentUser={currentUser}
        onOpenAuth={() => setIsAuthModalOpen(true)}
        onLogout={handleLogout}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        {activeTab === 'landing' && <LandingPage setActiveTab={setActiveTab} />}
        {activeTab === 'login' && <LoginPage onLoginSuccess={handleLoginSuccess} setActiveTab={setActiveTab} />}
        {activeTab === 'submit' && <ComplaintForm setActiveTab={setActiveTab} />}
        {activeTab === 'browse' && <CitizenBrowseFeed setActiveTab={setActiveTab} currentUser={currentUser} onOpenAuth={() => setIsAuthModalOpen(true)} />}
        {activeTab === 'dashboard' && <Dashboard setActiveTab={setActiveTab} />}
        {activeTab === 'map' && <MapView />}
        {activeTab === 'management' && <ComplaintManagement setActiveTab={setActiveTab} />}
      </main>

      {/* Authentication & Role Switching Modal */}
      <AuthModal 
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onLoginSuccess={handleLoginSuccess}
      />

    </div>
  );
}
