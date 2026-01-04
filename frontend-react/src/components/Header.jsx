import { useState, useEffect } from 'react';
import './Header.css';

function Header({ onApiKeyChange, apiKey }) {
  const [theme, setTheme] = useState('light');
  const [showApiModal, setShowApiModal] = useState(false);
  const [inputApiKey, setInputApiKey] = useState('');

  useEffect(() => {
    const savedTheme = localStorage.getItem('vibecheck-theme') || 'light';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Load saved API key
    const savedApiKey = localStorage.getItem('vibecheck-api-key') || '';
    setInputApiKey(savedApiKey);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('vibecheck-theme', newTheme);
  };

  const handleSaveApiKey = () => {
    localStorage.setItem('vibecheck-api-key', inputApiKey);
    onApiKeyChange(inputApiKey);
    setShowApiModal(false);
  };

  const handleClearApiKey = () => {
    setInputApiKey('');
    localStorage.removeItem('vibecheck-api-key');
    onApiKeyChange('');
  };

  return (
    <header className="header">
      <nav className="nav">
        <div className="logo">VIBECHECK.</div>
        <div className="nav-links">
          <button className="nav-link api-btn" onClick={() => setShowApiModal(true)}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="key-icon">
              <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>
            </svg>
            API {apiKey ? '✓' : ''}
          </button>
          <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === 'light' ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="5"/>
                <line x1="12" y1="1" x2="12" y2="3"/>
                <line x1="12" y1="21" x2="12" y2="23"/>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                <line x1="1" y1="12" x2="3" y2="12"/>
                <line x1="21" y1="12" x2="23" y2="12"/>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
              </svg>
            )}
          </button>
        </div>
      </nav>
      <div className="header-content">
        <h1 className="title">AI HALLUCINATION & CORRECTION</h1>
        <p className="tagline">
          Detect and fix AI-generated misinformation
        </p>
      </div>

      {/* API Key Modal */}
      {showApiModal && (
        <div className="api-modal-overlay" onClick={() => setShowApiModal(false)}>
          <div className="api-modal" onClick={e => e.stopPropagation()}>
            <div className="api-modal-header">
              <h3>API Configuration</h3>
              <button className="api-modal-close" onClick={() => setShowApiModal(false)}>×</button>
            </div>
            <div className="api-modal-body">
              <label className="api-label">Google Gemini API Key</label>
              <input
                type="password"
                className="api-input"
                placeholder="Enter your API key..."
                value={inputApiKey}
                onChange={(e) => setInputApiKey(e.target.value)}
              />
              <p className="api-hint">
                Get your API key from <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer">Google AI Studio</a>
              </p>
            </div>
            <div className="api-modal-footer">
              <button className="api-clear-btn" onClick={handleClearApiKey}>Clear</button>
              <button className="api-save-btn" onClick={handleSaveApiKey}>Save Key</button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}

export default Header;
