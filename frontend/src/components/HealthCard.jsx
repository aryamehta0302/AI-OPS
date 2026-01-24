const HealthCard = ({ health, nodeId }) => {
  if (!health) {
    return (
      <div className="card">
        <h3>SYSTEM HEALTH</h3>
        <div className="loading">
          <div className="loading-spinner"></div>
          Connecting...
        </div>
      </div>
    );
  }

  const classMap = {
    NORMAL: "normal",
    WARNING: "warning",
    CRITICAL: "critical"
  };

  const riskClass = classMap[health.risk_level] || "normal";

  return (
    <div className="card">
      <h3>SYSTEM HEALTH {nodeId && nodeId !== "all" ? `// ${nodeId}` : ""}</h3>
      <div className={`health-display ${riskClass}`}>
        <div className="health-score">
          <span className="score-number">{health.health_score.toFixed(1)}</span>
          <span className="score-unit">%</span>
        </div>
        <div className="health-ring">
          <svg viewBox="0 0 100 100">
            <circle 
              className="ring-bg" 
              cx="50" cy="50" r="45" 
              fill="none" 
              strokeWidth="8"
            />
            <circle 
              className={`ring-fill ${riskClass}`}
              cx="50" cy="50" r="45" 
              fill="none" 
              strokeWidth="8"
              strokeDasharray={`${health.health_score * 2.83} 283`}
              transform="rotate(-90 50 50)"
            />
          </svg>
        </div>
      </div>
      <div className="health-status">
        <span className="status-label">STATUS</span>
        <span className={`risk-badge ${riskClass}`}>{health.risk_level}</span>
      </div>
    </div>
  );
};

export default HealthCard;
