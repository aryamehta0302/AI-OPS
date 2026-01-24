const PredictionCard = ({ prediction }) => {
  // FIXED: Check explicit status field to prevent infinite loading
  // If prediction exists with any status, stop showing spinner
  
  if (!prediction) {
    // Only show loading when prediction object is completely missing
    return (
      <div className="card">
        <h3>PREDICTIVE ANALYSIS</h3>
        <div className="loading">
          <div className="loading-spinner"></div>
          Waiting for data...
        </div>
      </div>
    );
  }

  // Handle INSUFFICIENT_DATA status explicitly - show collecting message, not spinner
  if (prediction.status === "INSUFFICIENT_DATA" || prediction.trend === "ANALYZING") {
    return (
      <div className="card">
        <h3>PREDICTIVE ANALYSIS</h3>
        <div className="empty-state">
          <div className="empty-state-icon scan-icon"></div>
          <p>Collecting data... ({prediction.message || "Building baseline"})</p>
        </div>
      </div>
    );
  }

  const getTrendClass = (trend) => {
    switch (trend) {
      case "DEGRADING": return "critical";
      case "IMPROVING": return "normal";
      case "STABLE": return "warning";
      default: return "";
    }
  };

  const getRiskClass = (risk) => {
    switch (risk) {
      case "HIGH": return "critical";
      case "MEDIUM": return "warning";
      case "LOW": return "normal";
      default: return "";
    }
  };

  const confidencePercent = Math.round(prediction.confidence * 100);

  return (
    <div className="card">
      <h3>PREDICTIVE ANALYSIS</h3>
      
      <div className="prediction-content">
        <div className="prediction-trend">
          <span className="trend-label">TREND</span>
          <span className={`trend-value ${getTrendClass(prediction.trend)}`}>
            {prediction.trend}
          </span>
        </div>

        <div className="prediction-forecast">
          <span className="forecast-label">RISK FORECAST</span>
          <span className={`forecast-badge ${getRiskClass(prediction.risk_forecast)}`}>
            {prediction.risk_forecast}
          </span>
        </div>

        <div className="prediction-confidence">
          <div className="confidence-bar-bg">
            <div 
              className="confidence-bar-fill"
              style={{ width: `${confidencePercent}%` }}
            ></div>
          </div>
          <span className="confidence-value">{confidencePercent}% CONFIDENCE</span>
        </div>

        <div className="prediction-message">
          {prediction.message}
          {/* Show ETA when failure is likely */}
          {prediction.status === "FAILURE_LIKELY" && prediction.eta_minutes && (
            <div className="prediction-eta">
              ⚠️ Estimated time to issue: ~{prediction.eta_minutes} min
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PredictionCard;
