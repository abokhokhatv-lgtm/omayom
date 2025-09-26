import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Components
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './components/HomePage';
import AboutPage from './components/AboutPage';
import ServicesPage from './components/ServicesPage';
import BlogPage from './components/BlogPage';
import ContactPage from './components/ContactPage';
import CoursesPage from './components/CoursesPage';
import BookingPage from './components/BookingPage';
import LoginPage from './components/LoginPage';
import AdminDashboard from './components/AdminDashboard';
import TikTokLandingPage from './components/TikTokLandingPage';

function App() {
  const [language, setLanguage] = useState('ar');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('/api/auth/me', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const toggleLanguage = () => {
    setLanguage(language === 'ar' ? 'en' : 'ar');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className={`App ${language === 'ar' ? 'font-arabic' : 'font-english'}`} dir={language === 'ar' ? 'rtl' : 'ltr'}>
      <Router>
        <Routes>
          {/* Login Route */}
          <Route 
            path="/login" 
            element={
              user ? 
                <Navigate to={user.role === 'admin' ? '/admin' : '/'} replace /> :
                <LoginPage language={language} onLogin={handleLogin} />
            } 
          />
          
          {/* Admin Routes */}
          <Route 
            path="/admin/*" 
            element={
              user && user.role === 'admin' ? (
                <>
                  <Header 
                    language={language} 
                    toggleLanguage={toggleLanguage}
                    user={user}
                    onLogout={handleLogout}
                  />
                  <AdminDashboard language={language} />
                </>
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          
          {/* Public Routes */}
          <Route 
            path="/*" 
            element={
              <>
                <Header 
                  language={language} 
                  toggleLanguage={toggleLanguage}
                  user={user}
                  onLogout={handleLogout}
                />
                <main className="min-h-screen">
                  <Routes>
                    <Route path="/" element={<HomePage language={language} />} />
                    <Route path="/about" element={<AboutPage language={language} />} />
                    <Route path="/services" element={<ServicesPage language={language} />} />
                    <Route path="/blog" element={<BlogPage language={language} />} />
                    <Route path="/contact" element={<ContactPage language={language} />} />
                    <Route path="/courses" element={<CoursesPage language={language} />} />
                    <Route path="/booking" element={<BookingPage language={language} />} />
                    <Route path="/tiktok" element={<TikTokLandingPage language={language} />} />
                  </Routes>
                </main>
                <Footer language={language} />
              </>
            } 
          />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
