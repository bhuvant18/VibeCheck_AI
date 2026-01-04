import { useState, useEffect } from 'react';
import './App.css';
import { verifyText } from './api';
import ClaimCard from './components/ClaimCard';
import TextInput from './components/TextInput';
import Header from './components/Header';
import Stats from './components/Stats';
import CorrectedTextModal from './components/CorrectedTextModal';

const SAMPLE_TEXT = `Recent studies by Johnson et al. (2024) in the Journal of Advanced AI suggest that neural networks consume 50% less energy when trained on quantum hardware. This breakthrough, known as the 'Quantum Leap Protocol', was validated by Google DeepMind in their 2023 annual report. Meanwhile, the moon is made of green cheese, a fact confirmed by NASA in 1969. The Transformer architecture was introduced by Vaswani et al. in their 2017 paper "Attention Is All You Need".`;

function App() {
  const [text, setText] = useState(SAMPLE_TEXT);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCorrectedModal, setShowCorrectedModal] = useState(false);
  const [correctedText, setCorrectedText] = useState('');
  const [apiKey, setApiKey] = useState('');

  useEffect(() => {
    // Load saved API key on mount
    const savedApiKey = localStorage.getItem('vibecheck-api-key') || '';
    setApiKey(savedApiKey);
  }, []);

  const handleApiKeyChange = (newApiKey) => {
    setApiKey(newApiKey);
  };

  const handleAudit = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    if (!apiKey.trim()) {
      setError('Please configure your API key first. Click the API button in the header.');
      return;
    }

    setLoading(true);
    setError(null);
    setReport(null);

    try {
      const result = await verifyText(text, apiKey);
      setReport(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to connect to VibeCheck API. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleAutoFix = () => {
    if (!report?.claims) return;

    let fixedText = text;
    report.claims.forEach(claim => {
      if (claim.status === 'HALLUCINATION' && claim.correction) {
        fixedText = fixedText.replace(claim.original_text, claim.correction);
      }
    });
    setCorrectedText(fixedText);
    setShowCorrectedModal(true);
  };

  const handleApplyCorrectedText = () => {
    setText(correctedText);
    setShowCorrectedModal(false);
    setReport(null);
  };

  const getStats = () => {
    if (!report?.claims) return { verified: 0, hallucinations: 0, suspicious: 0, total: 0 };
    
    const stats = {
      verified: 0,
      hallucinations: 0,
      suspicious: 0,
      total: report.claims.length
    };

    report.claims.forEach(claim => {
      if (claim.status === 'VERIFIED') stats.verified++;
      else if (claim.status === 'HALLUCINATION') stats.hallucinations++;
      else if (claim.status === 'SUSPICIOUS') stats.suspicious++;
    });

    return stats;
  };

  const stats = getStats();

  return (
    <div className="app">
      <div className="decorative-dots">
        <div className="dot"></div>
        <div className="dot"></div>
        <div className="dot"></div>
        <div className="dot"></div>
        <div className="dot"></div>
        <div className="dot"></div>
      </div>
      <Header onApiKeyChange={handleApiKeyChange} apiKey={apiKey} />
      
      <main className="container">
        <div className="input-section">
          <TextInput 
            value={text}
            onChange={setText}
            onAudit={handleAudit}
            loading={loading}
          />

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
        </div>

        {report && (
          <>
            <Stats stats={stats} />
            
            <div className="results-section">
              <div className="results-header">
                <h2>Analysis Results</h2>
                {stats.hallucinations > 0 && (
                  <button className="auto-fix-btn" onClick={handleAutoFix}>
                    Auto-Fix All
                  </button>
                )}
              </div>

              <div className="claims-list">
                {report.claims.map((claim, index) => (
                  <ClaimCard key={index} claim={claim} index={index} />
                ))}
              </div>
            </div>
          </>
        )}

        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Analyzing text for hallucinations...</p>
          </div>
        )}

        {showCorrectedModal && (
          <CorrectedTextModal
            originalText={text}
            correctedText={correctedText}
            onApply={handleApplyCorrectedText}
            onClose={() => setShowCorrectedModal(false)}
          />
        )}
      </main>

      <footer className="footer">
        <p>Powered by Gemini 2.0 Flash — Built with React & FastAPI</p>
      </footer>
    </div>
  );
}

export default App;
