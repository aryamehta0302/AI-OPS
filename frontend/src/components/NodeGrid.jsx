const NodeGrid = ({ nodes, onSelectNode }) => {
  const nodeList = Object.values(nodes);

  if (nodeList.length === 0) {
    return null;
  }

  const getStatusClass = (riskLevel) => {
    if (!riskLevel) return "unknown";
    return riskLevel.toLowerCase();
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case "DEGRADING": return "trend-down";
      case "IMPROVING": return "trend-up";
      case "STABLE": return "trend-stable";
      default: return "trend-analyzing";
    }
  };

  // FIXED: Check if node is disconnected
  const isDisconnected = (node) => {
    return node.connectionStatus === "DISCONNECTED";
  };

  return (
    <div className="node-grid">
      {nodeList.map((node) => {
        const health = node.health || {};
        const prediction = node.prediction || {};
        const metrics = node.metrics || {};
        const disconnected = isDisconnected(node);
        
        return (
          <div 
            key={node.node_id} 
            className={`node-card ${getStatusClass(health.risk_level)} ${disconnected ? 'disconnected' : ''}`}
            onClick={() => onSelectNode(node.node_id)}
          >
            {/* Header */}
            <div className="node-card-header">
              <div className="node-id">
                {/* Connection indicator dot */}
                <span className={`connection-dot ${disconnected ? 'disconnected' : 'connected'}`}></span>
                {node.node_id}
              </div>
              <div className={`node-status-badge ${disconnected ? 'disconnected' : getStatusClass(health.risk_level)}`}>
                {disconnected ? "OFFLINE" : (health.risk_level || "UNKNOWN")}
              </div>
            </div>

            {/* Health Score */}
            <div className="node-health-score">
              <span className="score-value">
                {health.health_score?.toFixed(0) || "--"}
              </span>
              <span className="score-label">HEALTH</span>
            </div>

            {/* Metrics Grid */}
            <div className="node-metrics-grid">
              <div className="metric-item">
                <span className="metric-label">CPU</span>
                <span className="metric-value">{metrics.cpu?.usage_percent?.toFixed(0) || 0}%</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">MEM</span>
                <span className="metric-value">{metrics.memory?.usage_percent?.toFixed(0) || 0}%</span>
              </div>
              <div className="metric-item">
                <span className="metric-label">DISK</span>
                <span className="metric-value">{metrics.disk?.usage_percent?.toFixed(0) || 0}%</span>
              </div>
            </div>

            {/* Prediction */}
            <div className="node-prediction">
              <span className={`trend-indicator ${getTrendIcon(prediction.trend)}`}></span>
              <span className="prediction-text">
                {prediction.trend || "ANALYZING"}
              </span>
            </div>

            {/* Root Cause */}
            {node.rootCause?.root_cause && node.rootCause.root_cause !== "INSUFFICIENT_DATA" && (
              <div className="node-root-cause">
                PRIMARY: {node.rootCause.root_cause}
              </div>
            )}

            {/* Click Indicator */}
            <div className="node-card-footer">
              VIEW DETAILS
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default NodeGrid;
