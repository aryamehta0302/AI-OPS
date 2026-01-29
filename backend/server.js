require("dotenv").config();
const express = require("express");
const http = require("http");
const cors = require("cors");
const { Server } = require("socket.io");

const setupSocket = require("./socket");
const { getTimeline } = require("./services/incidentManager");
const { processAgentMetrics, initConnectionChecker, getActiveNodes, getConnectionStats } = require("./services/nodeManager");

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: "*"
  }
});

// Initialize Socket.IO streaming (for legacy single-node polling)
setupSocket(io);

// Initialize node connection status checker (emits DISCONNECTED after 15s timeout)
initConnectionChecker(io);

// =======================
// REST API ENDPOINTS
// =======================

// Health check
app.get("/health", (req, res) => {
  res.json({ status: "Backend running" });
});

// Incident timeline (AIOps feature)
// Supports optional ?node_id= query parameter for filtering
app.get("/incidents", (req, res) => {
  const nodeId = req.query.node_id;
  const timeline = getTimeline(nodeId);
  res.json({
    count: timeline.length,
    incidents: timeline
  });
});

// =======================
// MULTI-NODE AGENT ENDPOINT
// =======================

// POST /agent/metrics - Receives metrics from distributed agents
// HARDENED: Strict validation, heartbeat tracking, connection state management
app.post("/agent/metrics", async (req, res) => {
  const { node_id, hostname, metrics, agent_state, heartbeat } = req.body;

  // Basic validation (detailed validation in nodeManager)
  if (!node_id || !metrics) {
    return res.status(400).json({ 
      error: "Missing required fields: node_id and metrics",
      received: { node_id: !!node_id, metrics: !!metrics }
    });
  }

  try {
    // Process metrics through AI Engine and emit to frontend
    const result = await processAgentMetrics(io, { 
      node_id, 
      hostname, 
      metrics,
      agent_state,
      heartbeat
    });
    
    res.json({ 
      status: "ok", 
      node_id, 
      processed: true,
      connection_state: "CONNECTED",
      agent_status: result.agent_status || "ACTIVE"
    });
  } catch (err) {
    console.error(`[AGENT] Error processing metrics for ${node_id}:`, err.message);
    res.status(err.message.includes("rejected") ? 400 : 500).json({ 
      error: err.message || "Failed to process metrics",
      node_id
    });
  }
});

// GET /nodes - Returns list of all nodes with connection state
app.get("/nodes", (req, res) => {
  const nodes = getActiveNodes();
  const stats = getConnectionStats();
  
  res.json({ 
    nodes,
    stats,
    timestamp: new Date().toISOString()
  });
});

// GET /nodes/:nodeId - Returns detailed info for a specific node
app.get("/nodes/:nodeId", (req, res) => {
  const { getNodeData } = require("./services/nodeManager");
  const nodeData = getNodeData(req.params.nodeId);
  
  if (!nodeData) {
    return res.status(404).json({ 
      error: "Node not found",
      node_id: req.params.nodeId
    });
  }
  
  res.json(nodeData);
});

// =======================
// SERVER START
// =======================

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`Backend listening on port ${PORT}`);
});
