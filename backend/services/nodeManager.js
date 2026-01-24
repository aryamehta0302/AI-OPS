/**
 * nodeManager.js
 * 
 * Manages multi-node state for distributed AIOps agents.
 * - Stores latest metrics per node_id
 * - Forwards metrics to AI Engine with node_id
 * - Emits Socket.IO events with node_id included
 * - Tracks connection status per node (CONNECTED/DISCONNECTED)
 */

const { sendMetricsToAIEngine } = require("./aiEngineClient");
const { updateState } = require("./incidentManager");

// In-memory store: { node_id: { hostname, metrics, lastSeen, aiResult, status } }
const nodeStore = {};

// FIXED: Reduced timeout for responsive disconnect detection (15 seconds)
const NODE_TIMEOUT_MS = 15000;

// Reference to Socket.IO instance for status updates
let ioInstance = null;

/**
 * Initialize connection status checker
 * Emits node_status_update when nodes go offline
 */
function initConnectionChecker(io) {
  ioInstance = io;
  
  // Check connection status every 5 seconds
  setInterval(() => {
    const now = Date.now();
    
    for (const [node_id, data] of Object.entries(nodeStore)) {
      const wasConnected = data.status === "CONNECTED";
      const isNowConnected = (now - data.lastSeen) < NODE_TIMEOUT_MS;
      
      // Detect status change: CONNECTED -> DISCONNECTED
      if (wasConnected && !isNowConnected) {
        data.status = "DISCONNECTED";
        console.log(`[NODE] ${node_id} disconnected (no metrics for ${NODE_TIMEOUT_MS/1000}s)`);
        
        // Emit status update to frontend
        io.emit("node_status_update", {
          node_id,
          status: "DISCONNECTED",
          lastSeen: data.lastSeen
        });
      }
    }
  }, 5000);
}

/**
 * Process metrics received from a distributed agent
 * @param {Server} io - Socket.IO server instance
 * @param {Object} payload - { node_id, hostname, metrics }
 */
async function processAgentMetrics(io, { node_id, hostname, metrics }) {
  // Track if this is a new node or reconnection
  const isNewOrReconnecting = !nodeStore[node_id] || nodeStore[node_id].status === "DISCONNECTED";
  
  // Update node store with latest data
  nodeStore[node_id] = {
    hostname: hostname || node_id,
    metrics,
    lastSeen: Date.now(),
    status: "CONNECTED"  // Mark as connected when receiving metrics
  };
  
  // Emit connection status if node just connected/reconnected
  if (isNewOrReconnecting) {
    console.log(`[NODE] ${node_id} connected`);
    io.emit("node_status_update", {
      node_id,
      status: "CONNECTED",
      lastSeen: Date.now()
    });
  }

  // Forward to AI Engine for processing (with node_id)
  const aiResult = await sendMetricsToAIEngine(node_id, metrics);

  // Store AI result for this node
  nodeStore[node_id].aiResult = aiResult;

  // Build enriched metrics payload with node_id
  const enrichedMetrics = {
    node_id,
    hostname: hostname || node_id,
    ...aiResult
  };

  // Emit system_metrics event (includes node_id for frontend filtering)
  io.emit("system_metrics", enrichedMetrics);

  // Check for health state transitions (per-node incident tracking)
  const incident = updateState(
    node_id,
    aiResult.system_health,
    aiResult.root_cause
  );

  // Emit incident event only on state change
  if (incident) {
    io.emit("incident_event", incident);
  }

  return enrichedMetrics;
}

/**
 * Get list of active nodes (seen within timeout period)
 * @returns {Array} Array of { node_id, hostname, lastSeen }
 */
function getActiveNodes() {
  const now = Date.now();
  const activeNodes = [];

  for (const [node_id, data] of Object.entries(nodeStore)) {
    // Include node if seen within timeout
    if (now - data.lastSeen < NODE_TIMEOUT_MS) {
      activeNodes.push({
        node_id,
        hostname: data.hostname,
        lastSeen: data.lastSeen,
        // Include latest health status if available
        health_status: data.aiResult?.system_health?.risk_level || "UNKNOWN"
      });
    }
  }

  return activeNodes;
}

/**
 * Get stored data for a specific node
 * @param {string} nodeId 
 * @returns {Object|null}
 */
function getNodeData(nodeId) {
  return nodeStore[nodeId] || null;
}

module.exports = {
  processAgentMetrics,
  getActiveNodes,
  getNodeData,
  initConnectionChecker  // Export for server.js to initialize
};
