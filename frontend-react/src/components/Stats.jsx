import './Stats.css';

function Stats({ stats }) {
  const accuracy = stats.total > 0 
    ? Math.round((stats.verified / stats.total) * 100)
    : 0;

  return (
    <div className="stats-container">
      <div className="stat-card verified">
        <div className="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <div className="stat-content">
          <div className="stat-value">{stats.verified}</div>
          <div className="stat-label">Verified</div>
        </div>
      </div>

      <div className="stat-card hallucination">
        <div className="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
        </div>
        <div className="stat-content">
          <div className="stat-value">{stats.hallucinations}</div>
          <div className="stat-label">Hallucinations</div>
        </div>
      </div>

      <div className="stat-card suspicious">
        <div className="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
        </div>
        <div className="stat-content">
          <div className="stat-value">{stats.suspicious}</div>
          <div className="stat-label">Suspicious</div>
        </div>
      </div>

      <div className="stat-card accuracy">
        <div className="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="20" x2="18" y2="10"/>
            <line x1="12" y1="20" x2="12" y2="4"/>
            <line x1="6" y1="20" x2="6" y2="14"/>
          </svg>
        </div>
        <div className="stat-content">
          <div className="stat-value">{accuracy}%</div>
          <div className="stat-label">Accuracy</div>
        </div>
      </div>
    </div>
  );
}

export default Stats;
