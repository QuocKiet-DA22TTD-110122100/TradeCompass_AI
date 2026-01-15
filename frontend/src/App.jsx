import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Market from './pages/Market'
import Predictions from './pages/Predictions'
import About from './pages/About'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="container">
            <div className="nav-content">
              <div className="logo">
                <span className="logo-icon">📊</span>
                <span className="logo-text">TradeCompass AI</span>
              </div>
              <div className="nav-links">
                <Link to="/" className={activeTab === 'dashboard' ? 'active' : ''} onClick={() => setActiveTab('dashboard')}>
                  Dashboard
                </Link>
                <Link to="/market" className={activeTab === 'market' ? 'active' : ''} onClick={() => setActiveTab('market')}>
                  Market
                </Link>
                <Link to="/predictions" className={activeTab === 'predictions' ? 'active' : ''} onClick={() => setActiveTab('predictions')}>
                  AI Predictions
                </Link>
                <Link to="/about" className={activeTab === 'about' ? 'active' : ''} onClick={() => setActiveTab('about')}>
                  About
                </Link>
              </div>
            </div>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/market" element={<Market />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>

        <footer className="footer">
          <div className="container">
            <p>© 2024 TradeCompass AI - AI-powered trading ecosystem for everyone</p>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App
