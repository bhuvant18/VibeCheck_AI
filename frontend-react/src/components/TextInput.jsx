import { useRef, useEffect } from 'react';
import './TextInput.css';

function TextInput({ value, onChange, onAudit, loading }) {
  const textareaRef = useRef(null);

  // Auto-expand textarea as content grows
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const newHeight = Math.min(Math.max(textarea.scrollHeight, 80), 300);
      textarea.style.height = newHeight + 'px';
    }
  }, [value]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && value.trim() && !loading) {
      e.preventDefault();
      onAudit();
    }
  };

  return (
    <div className="text-input-container">
      <textarea
        ref={textareaRef}
        className="text-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Enter text to check for hallucinations..."
        rows={3}
        disabled={loading}
      />
      <div className="input-actions">
        <button
          className="clear-btn"
          onClick={() => onChange('')}
          disabled={loading || !value}
          title="Clear"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
        <button
          className="audit-btn"
          onClick={onAudit}
          disabled={loading || !value.trim()}
          title="Analyze"
        >
          {loading ? (
            <div className="loading-spinner"></div>
          ) : (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M22 2L11 13"/>
              <path d="M22 2L15 22L11 13L2 9L22 2Z"/>
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}

export default TextInput;
