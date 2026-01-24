const RootCauseCard = ({ rootCause }) => {
  if (!rootCause) {
    return (
      <div className="card">
        <h3>ROOT CAUSE ANALYSIS</h3>
        <div className="loading">
          <div className="loading-spinner"></div>
          Analyzing...
        </div>
      </div>
    );
  }

  if (rootCause.root_cause === "INSUFFICIENT_DATA") {
    return (
      <div className="card">
        <h3>ROOT CAUSE ANALYSIS</h3>
        <div className="empty-state">
          <div className="empty-state-icon scan-icon"></div>
          <p>Learning system baseline...</p>
        </div>
      </div>
    );
  }

  const confidencePercent = Math.round(rootCause.confidence * 100);

  const getConfidenceClass = (percent) => {
    if (percent > 70) return "high";
    if (percent > 40) return "medium";
    return "low";
  };

  return (
    <div className="card">
      <h3>ROOT CAUSE ANALYSIS</h3>
      <div className="root-cause-display">
        <div className="cause-indicator">
          <span className={`cause-icon ${rootCause.root_cause.toLowerCase()}`}></span>
        </div>
        <div className="cause-label">{rootCause.root_cause}</div>
      </div>
      <div className="cause-confidence">
        <span className="confidence-label">CONFIDENCE</span>
        <div className="confidence-meter">
          <div 
            className={`confidence-fill ${getConfidenceClass(confidencePercent)}`}
            style={{ width: `${confidencePercent}%` }}
          ></div>
        </div>
        <span className={`confidence-value ${getConfidenceClass(confidencePercent)}`}>
          {confidencePercent}%
        </span>
      </div>
    </div>
  );
};

export default RootCauseCard;
