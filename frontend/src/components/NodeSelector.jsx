const NodeSelector = ({ nodes, selected, onSelect, nodeData }) => {
  // Get health status for node styling
  const getNodeStatus = (nodeId) => {
    const node = nodeData[nodeId];
    if (!node) return "unknown";
    return node.health?.risk_level?.toLowerCase() || "unknown";
  };

  // FIXED: Get connection status for node (CONNECTED/DISCONNECTED)
  const getConnectionStatus = (nodeId) => {
    const node = nodeData[nodeId];
    if (!node) return "disconnected";
    return node.connectionStatus === "CONNECTED" ? "connected" : "disconnected";
  };

  // Count connected nodes
  const connectedCount = nodes.filter(id => getConnectionStatus(id) === "connected").length;

  return (
    <div className="node-selector">
      <div className="selector-label">SELECT NODE</div>
      <div className="selector-options">
        <button
          className={`selector-btn ${selected === "all" ? "active" : ""}`}
          onClick={() => onSelect("all")}
        >
          <span className="btn-icon all-icon"></span>
          ALL NODES
          <span className="node-count">{connectedCount}/{nodes.length}</span>
        </button>
        
        {nodes.map((nodeId) => (
          <button
            key={nodeId}
            className={`selector-btn ${selected === nodeId ? "active" : ""} ${getConnectionStatus(nodeId)}`}
            onClick={() => onSelect(nodeId)}
          >
            {/* Connection indicator: green dot for connected, red for disconnected */}
            <span className={`connection-dot ${getConnectionStatus(nodeId)}`}></span>
            <span className={`btn-status ${getNodeStatus(nodeId)}`}></span>
            {nodeId}
            {getConnectionStatus(nodeId) === "disconnected" && (
              <span className="disconnected-badge">OFFLINE</span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
};

export default NodeSelector;
