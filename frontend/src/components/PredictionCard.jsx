import { 
  BarChart3, 
  CheckCircle2, 
  Loader2,
  Clock,
  TrendingDown,
  TrendingUp,
  Minus
} from "lucide-react";

const PredictionCard = ({ prediction }) => {
  // FIXED: Explicit status handling to prevent infinite loading
  // Status can be: STABLE, FAILURE_LIKELY, INSUFFICIENT_DATA
  
  if (!prediction) {
    // Only show loading when prediction object is completely missing
    return (
      <div className="card">
        <h3>PREDICTIVE ANALYSIS</h3>
        <div className="loading">
          <Loader2 size={20} className="loading-spinner spin" />
          Awaiting agent analysis...
        </div>
      </div>
    );
  }

  // Handle INSUFFICIENT_DATA status - show collecting message, not spinner
  if (prediction.status === "INSUFFICIENT_DATA" || prediction.trend === "ANALYZING") {
    return (
      <div className="card">
        <h3>PREDICTIVE ANALYSIS</h3>
        <div className="prediction-collecting">
          <BarChart3 size={24} className="collecting-icon" />
          <div className="collecting-text">
            <span className="collecting-status">COLLECTING DATA</span>
            <span className="collecting-message">{prediction.message || "Building baseline..."}</span>
          </div>
        </div>
      </div>
    );
  }

  // Handle STABLE status
  if (prediction.status === "STABLE") {
    return (
      <div className="card">
        <h3>PREDICTIVE ANALYSIS</h3>
        <div className="prediction-stable">
          <CheckCircle2 size={24} className="stable-icon" color="#4ade80" />
          <div className="stable-content">
            <span className="stable-status">SYSTEM STABLE</span>
            <span className="stable-message">{prediction.message}</span>
            <div className="stable-confidence">
              <span>Confidence: {Math.round(prediction.confidence * 100)}%</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Handle FAILURE_LIKELY status
  const getTrendClass = (trend) => {
    switch (trend) {
      case "DEGRADING": return "critical";
      case "IMPROVING": return "normal";
      case "STABLE": return "warning";
      case "CRITICAL_DECLINE": return "critical";
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
            {prediction.trend?.replace("_", " ")}
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
        </div>

        {/* Show ETA when failure is likely */}
        {prediction.status === "FAILURE_LIKELY" && prediction.eta_minutes && (
          <div className="prediction-eta">
            <Clock size={16} className="eta-icon" />
            <span className="eta-text">
              Estimated time to issue: <strong>~{prediction.eta_minutes} min</strong>
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictionCard;
