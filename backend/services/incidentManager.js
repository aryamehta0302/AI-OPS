/**
 * incidentManager.js
 * 
 * Tracks health state transitions per node for multi-node AIOps.
 * Maintains separate state and incident timeline per node_id.
 */

// Per-node state tracking: { node_id: { currentState, lastStateChange } }
const nodeStates = {};

// Default state for new nodes
const DEFAULT_STATE = "NORMAL";

// Global incident timeline (stores all node incidents)
const incidentTimeline = [];

// Maximum incidents to keep in timeline
const MAX_INCIDENTS = 50;

/**
 * Update health state for a specific node
 * @param {string} nodeId - Node identifier (use "local" for legacy single-node)
 * @param {Object} systemHealth - { health_score, risk_level }
 * @param {Object} rootCause - { root_cause, contributors }
 * @returns {Object|null} Incident object if state changed, null otherwise
 */
function updateState(nodeId, systemHealth, rootCause) {
  // For backward compatibility: if nodeId is an object (old signature), handle it
  if (typeof nodeId === "object") {
    // Old signature: updateState(systemHealth, rootCause)
    rootCause = systemHealth;
    systemHealth = nodeId;
    nodeId = "local";
  }

  // Initialize state for new nodes
  if (!nodeStates[nodeId]) {
    nodeStates[nodeId] = {
      currentState: DEFAULT_STATE,
      lastStateChange: Date.now()
    };
  }

  const nodeState = nodeStates[nodeId];
  const newState = systemHealth.risk_level;

  // Check for state transition
  if (newState !== nodeState.currentState) {
    const incident = {
      node_id: nodeId,
      from: nodeState.currentState,
      to: newState,
      timestamp: new Date().toISOString(),
      health_score: systemHealth.health_score,
      root_cause: rootCause?.root_cause || "UNKNOWN"
    };

    incidentTimeline.push(incident);

    // Keep timeline within max limit
    if (incidentTimeline.length > MAX_INCIDENTS) {
      incidentTimeline.shift();
    }

    // Update node state
    nodeState.lastStateChange = Date.now();
    nodeState.currentState = newState;

    return incident;
  }

  return null;
}

/**
 * Get incident timeline, optionally filtered by node_id
 * @param {string} [nodeId] - Optional node filter (null = all nodes)
 * @returns {Array} Array of incident objects
 */
function getTimeline(nodeId) {
  if (!nodeId || nodeId === "all") {
    return incidentTimeline;
  }
  return incidentTimeline.filter(incident => incident.node_id === nodeId);
}

/**
 * Get current state for a specific node
 * @param {string} nodeId 
 * @returns {string} Current risk level
 */
function getNodeState(nodeId) {
  return nodeStates[nodeId]?.currentState || DEFAULT_STATE;
}

module.exports = {
  updateState,
  getTimeline,
  getNodeState
};
