/**
 * CONNECTION INDICATOR COMPONENT
 * ===============================
 * Shows connection status for:
 * - Backend socket connection
 * - Individual node connections
 */

import "./ConnectionIndicator.css";

function ConnectionIndicator({ isConnected, connected, nodeStatus, nodeId, label }) {
  // Support both 'connected' and 'isConnected' props for flexibility
  const isOnline = isConnected ?? connected ?? false;
  
  // For overall backend connection
  if (!nodeId) {
    return (
      <div className={`connection-indicator ${isOnline ? "connected" : "disconnected"}`}>
        <span className="connection-dot"></span>
        <span className="connection-text">
          {label ? `${label}: ` : ""}{isOnline ? "ONLINE" : "OFFLINE"}
        </span>
      </div>
    );
  }

  // For individual node status
  const status = nodeStatus || "UNKNOWN";
  const nodeConnected = status === "CONNECTED";

  return (
    <div className={`node-connection ${nodeConnected ? "connected" : "disconnected"}`}>
      <span className="connection-dot"></span>
      <span className="node-id">{nodeId}</span>
      <span className="node-status">{status}</span>
    </div>
  );
}

// Compact version for headers
export function ConnectionDot({ connected }) {
  return (
    <span 
      className={`connection-dot-only ${connected ? "connected" : "disconnected"}`}
      title={connected ? "Connected" : "Disconnected"}
    />
  );
}

// Node status badge for node selector
export function NodeStatusBadge({ status, lastSeen }) {
  const isConnected = status === "CONNECTED";
  const isStale = lastSeen && (Date.now() - lastSeen > 15000); // 15 seconds
  
  let displayStatus = status;
  let statusClass = isConnected ? "connected" : "disconnected";
  
  if (isStale && isConnected) {
    displayStatus = "STALE";
    statusClass = "stale";
  }

  return (
    <span className={`node-status-badge ${statusClass}`}>
      <span className="status-dot"></span>
      {displayStatus}
    </span>
  );
}

export default ConnectionIndicator;
