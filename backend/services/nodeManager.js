/**
 * nodeManager.js
 * 
 * Manages multi-node state for distributed AIOps agents.
 * HARDENED for realistic agent behavior:
 * - Tracks last heartbeat per node_id
 * - Validates agent inputs strictly
 * - Marks nodes DISCONNECTED after timeout
 * - Rejects malformed or stale data
 * - Broadcasts accurate connection state
 */

const { sendMetricsToAIEngine } = require("./aiEngineClient");
const { updateState } = require("./incidentManager");

// In-memory store: { node_id: { hostname, metrics, lastSeen, aiResult, status, agentState, heartbeat } }
const nodeStore = {};

// Heartbeat tracking: { node_id: { lastSeq, lastTimestamp, missedHeartbeats } }
const heartbeatTracker = {};

// Connection timeout (15 seconds = 3 missed heartbeats at 5s interval)
const NODE_TIMEOUT_MS = 15000;

// Heartbeat validation window (reject heartbeats older than this)
const HEARTBEAT_STALE_MS = 30000;

// Maximum allowed metric staleness
const METRIC_STALE_MS = 60000;

// Reference to Socket.IO instance
let ioInstance = null;

/**
 * Validate agent payload for required fields and data integrity
 * @param {Object} payload - { node_id, hostname, metrics, agent_state, heartbeat }
 * @returns {Object} { valid: boolean, error?: string }
 */
function validateAgentPayload(payload) {
  // Required fields
  if (!payload.node_id || typeof payload.node_id !== "string") {
    return { valid: false, error: "Missing or invalid node_id" };
  }
  
  if (!payload.metrics || typeof payload.metrics !== "object") {
    return { valid: false, error: "Missing or invalid metrics object" };
  }
  
  // Validate metrics structure
  const { metrics } = payload;
  if (!metrics.cpu || typeof metrics.cpu.usage_percent !== "number") {
    return { valid: false, error: "Invalid metrics.cpu structure" };
  }
  
  if (!metrics.memory || typeof metrics.memory.usage_percent !== "number") {
    return { valid: false, error: "Invalid metrics.memory structure" };
  }
  
  // Validate metric ranges (sanity check)
  if (metrics.cpu.usage_percent < 0 || metrics.cpu.usage_percent > 100) {
    return { valid: false, error: "CPU usage out of range (0-100)" };
  }
  
  if (metrics.memory.usage_percent < 0 || metrics.memory.usage_percent > 100) {
    return { valid: false, error: "Memory usage out of range (0-100)" };
  }
  
  // Check for stale metrics (if timestamp provided)
  if (metrics.timestamp) {
    const metricTime = new Date(metrics.timestamp).getTime();
    if (Date.now() - metricTime > METRIC_STALE_MS) {
      return { valid: false, error: "Metrics timestamp too old (stale data rejected)" };
    }
  }
  
  return { valid: true };
}

/**
 * Process and validate heartbeat from agent
 * @param {string} nodeId 
 * @param {Object} heartbeat - { sequence, timestamp, uptime_seconds }
 * @returns {Object} { valid: boolean, isNewConnection: boolean, missedBeats: number }
 */
function processHeartbeat(nodeId, heartbeat) {
  const now = Date.now();
  
  // Initialize tracker for new nodes
  if (!heartbeatTracker[nodeId]) {
    heartbeatTracker[nodeId] = {
      lastSeq: -1,
      lastTimestamp: now,
      missedHeartbeats: 0
    };
    return { valid: true, isNewConnection: true, missedBeats: 0 };
  }
  
  const tracker = heartbeatTracker[nodeId];
  
  // Validate heartbeat sequence (should be increasing)
  if (heartbeat && heartbeat.sequence !== undefined) {
    const expectedSeq = tracker.lastSeq + 1;
    const actualSeq = heartbeat.sequence;
    
    // Calculate missed heartbeats
    if (actualSeq > expectedSeq) {
      tracker.missedHeartbeats += (actualSeq - expectedSeq);
    }
    
    tracker.lastSeq = actualSeq;
  }
  
  // Check for stale heartbeat
  if (heartbeat && heartbeat.timestamp) {
    const heartbeatTime = new Date(heartbeat.timestamp).getTime();
    if (now - heartbeatTime > HEARTBEAT_STALE_MS) {
      return { valid: false, isNewConnection: false, missedBeats: tracker.missedHeartbeats };
    }
  }
  
  tracker.lastTimestamp = now;
  
  return { 
    valid: true, 
    isNewConnection: false, 
    missedBeats: tracker.missedHeartbeats 
  };
}

/**
 * Initialize connection status checker
 * Emits node_status_update when nodes go offline/online
 */
function initConnectionChecker(io) {
  ioInstance = io;
  
  // Check connection status every 5 seconds
  setInterval(() => {
    const now = Date.now();
    
    for (const [node_id, data] of Object.entries(nodeStore)) {
      const wasConnected = data.status === "CONNECTED";
      const timeSinceLastSeen = now - data.lastSeen;
      const isNowConnected = timeSinceLastSeen < NODE_TIMEOUT_MS;
      
      // Detect status change: CONNECTED -> DISCONNECTED
      if (wasConnected && !isNowConnected) {
        data.status = "DISCONNECTED";
        data.connection_state = "DISCONNECTED";
        
        console.log(`[NODE] ${node_id} DISCONNECTED (no heartbeat for ${(timeSinceLastSeen/1000).toFixed(1)}s)`);
        
        // Emit status update to frontend with full state
        io.emit("node_status_update", {
          node_id,
          status: "DISCONNECTED",
          connection_state: "DISCONNECTED",
          lastSeen: data.lastSeen,
          agent_status: "OFFLINE",
          timeSinceLastSeen: timeSinceLastSeen
        });
      }
    }
  }, 5000);
}

/**
 * Process metrics received from a distributed agent
 * HARDENED: Validates all inputs, tracks heartbeats, ensures consistency
 * @param {Server} io - Socket.IO server instance
 * @param {Object} payload - { node_id, hostname, metrics, agent_state, heartbeat }
 */
async function processAgentMetrics(io, payload) {
  const { node_id, hostname, metrics, agent_state, heartbeat } = payload;
  
  // VALIDATION: Strict input validation
  const validation = validateAgentPayload(payload);
  if (!validation.valid) {
    console.error(`[NODE] ${node_id || "UNKNOWN"} rejected: ${validation.error}`);
    throw new Error(validation.error);
  }
  
  // HEARTBEAT: Process and validate heartbeat
  const heartbeatResult = processHeartbeat(node_id, heartbeat);
  if (!heartbeatResult.valid) {
    console.warn(`[NODE] ${node_id} stale heartbeat rejected`);
    throw new Error("Stale heartbeat rejected");
  }
  
  // Track if this is a new node or reconnection
  const existingNode = nodeStore[node_id];
  const isNewOrReconnecting = !existingNode || existingNode.status === "DISCONNECTED";
  
  // Determine agent status from agent_state
  let agentStatus = "ACTIVE";
  if (agent_state) {
    if (agent_state.health_state === "DEGRADED" || agent_state.health_state === "DEGRADING") {
      agentStatus = "DEGRADED";
    } else if (agent_state.health_state === "RECOVERING") {
      agentStatus = "RECOVERING";
    }
  }
  
  // Update node store with comprehensive state
  nodeStore[node_id] = {
    hostname: hostname || node_id,
    metrics,
    lastSeen: Date.now(),
    status: "CONNECTED",
    connection_state: "CONNECTED",
    agent_status: agentStatus,
    agent_state: agent_state || null,
    heartbeat: {
      sequence: heartbeat?.sequence || 0,
      lastReceived: Date.now(),
      missedBeats: heartbeatResult.missedBeats
    }
  };
  
  // Emit connection status if node just connected/reconnected
  if (isNewOrReconnecting) {
    console.log(`[NODE] ${node_id} CONNECTED (hostname: ${hostname || node_id})`);
    io.emit("node_status_update", {
      node_id,
      status: "CONNECTED",
      connection_state: "CONNECTED",
      agent_status: agentStatus,
      lastSeen: Date.now(),
      isReconnection: !!existingNode
    });
  }

  // Forward to AI Engine for processing (with node_id AND agent_state)
  // This enables the decision agent to make accurate decisions based on real PC agent state
  const aiResult = await sendMetricsToAIEngine(node_id, metrics, agent_state, heartbeat);

  // Store AI result for this node
  nodeStore[node_id].aiResult = aiResult;

  // Build enriched metrics payload with full state information
  const enrichedMetrics = {
    node_id,
    hostname: hostname || node_id,
    // Connection state (REQUIRED)
    connection_state: "CONNECTED",
    agent_status: agentStatus,
    // Agent internal state
    agent_state: agent_state || null,
    // AI results
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
    // Enrich incident with connection state
    incident.connection_state = "CONNECTED";
    incident.agent_status = agentStatus;
    io.emit("incident_event", incident);
  }

  return enrichedMetrics;
}

/**
 * Get list of all known nodes with their current status
 * @returns {Array} Array of { node_id, hostname, lastSeen, status, connection_state, agent_status }
 */
function getActiveNodes() {
  const now = Date.now();
  const allNodes = [];

  for (const [node_id, data] of Object.entries(nodeStore)) {
    const timeSinceLastSeen = now - data.lastSeen;
    const isConnected = timeSinceLastSeen < NODE_TIMEOUT_MS;
    
    allNodes.push({
      node_id,
      hostname: data.hostname,
      lastSeen: data.lastSeen,
      timeSinceLastSeen,
      // Connection state
      status: isConnected ? "CONNECTED" : "DISCONNECTED",
      connection_state: isConnected ? "CONNECTED" : "DISCONNECTED",
      agent_status: isConnected ? (data.agent_status || "ACTIVE") : "OFFLINE",
      // Agent internal state
      agent_state: data.agent_state || null,
      // Health status from AI
      health_status: data.aiResult?.system_health?.risk_level || "UNKNOWN"
    });
  }

  return allNodes;
}

/**
 * Get stored data for a specific node
 * @param {string} nodeId 
 * @returns {Object|null}
 */
function getNodeData(nodeId) {
  const data = nodeStore[nodeId];
  if (!data) return null;
  
  const now = Date.now();
  const isConnected = (now - data.lastSeen) < NODE_TIMEOUT_MS;
  
  return {
    ...data,
    connection_state: isConnected ? "CONNECTED" : "DISCONNECTED",
    agent_status: isConnected ? (data.agent_status || "ACTIVE") : "OFFLINE"
  };
}

/**
 * Get connection statistics for all nodes
 * @returns {Object} { total, connected, disconnected, degraded }
 */
function getConnectionStats() {
  const now = Date.now();
  let connected = 0;
  let disconnected = 0;
  let degraded = 0;
  
  for (const data of Object.values(nodeStore)) {
    if ((now - data.lastSeen) < NODE_TIMEOUT_MS) {
      connected++;
      if (data.agent_status === "DEGRADED") {
        degraded++;
      }
    } else {
      disconnected++;
    }
  }
  
  return {
    total: Object.keys(nodeStore).length,
    connected,
    disconnected,
    degraded
  };
}

module.exports = {
  processAgentMetrics,
  getActiveNodes,
  getNodeData,
  getConnectionStats,
  initConnectionChecker
};
