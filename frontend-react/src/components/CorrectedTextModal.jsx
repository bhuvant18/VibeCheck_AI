import { useState } from 'react';
import './CorrectedTextModal.css';

function CorrectedTextModal({ originalText, correctedText, onApply, onClose }) {
  const [view, setView] = useState('corrected'); // 'original', 'corrected', 'comparison'

  const getDifferences = () => {
    // Simple diff highlighting
    const differences = [];
    let tempOriginal = originalText;
    
    // Find differences by comparing
    const originalWords = originalText.split(' ');
    const correctedWords = correctedText.split(' ');
    
    return { originalWords, correctedWords };
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(correctedText);
    alert('Corrected text copied to clipboard!');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>✨ Corrected Text</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-tabs">
          <button 
            className={`tab ${view === 'original' ? 'active' : ''}`}
            onClick={() => setView('original')}
          >
            📄 Original
          </button>
          <button 
            className={`tab ${view === 'corrected' ? 'active' : ''}`}
            onClick={() => setView('corrected')}
          >
            ✅ Corrected
          </button>
          <button 
            className={`tab ${view === 'comparison' ? 'active' : ''}`}
            onClick={() => setView('comparison')}
          >
            🔍 Side-by-Side
          </button>
        </div>

        <div className="modal-body">
          {view === 'original' && (
            <div className="text-view">
              <div className="view-label">Original Text</div>
              <div className="text-content original">
                {originalText}
              </div>
            </div>
          )}

          {view === 'corrected' && (
            <div className="text-view">
              <div className="view-label">Corrected Text (Hallucinations Removed)</div>
              <div className="text-content corrected">
                {correctedText}
              </div>
            </div>
          )}

          {view === 'comparison' && (
            <div className="comparison-view">
              <div className="comparison-column">
                <div className="view-label">Original Text</div>
                <div className="text-content original">
                  {originalText}
                </div>
              </div>
              <div className="comparison-divider">
                <div className="arrow">→</div>
              </div>
              <div className="comparison-column">
                <div className="view-label">Corrected Text</div>
                <div className="text-content corrected">
                  {correctedText}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={handleCopy}>
            📋 Copy Corrected Text
          </button>
          <button className="btn-primary" onClick={onApply}>
            ✓ Apply Corrections
          </button>
        </div>
      </div>
    </div>
  );
}

export default CorrectedTextModal;
