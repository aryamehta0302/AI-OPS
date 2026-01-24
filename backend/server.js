require("dotenv").config();
const express = require("express");
const http = require("http");
const cors = require("cors");
const { Server } = require("socket.io");

const setupSocket = require("./socket");
const { getTimeline } = require("./services/incidentManager");
const { processAgentMetrics, initConnectionChecker } = require("./services/nodeManager");

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
app.post("/agent/metrics", async (req, res) => {
  const { node_id, hostname, metrics } = req.body;

  // Validate required fields
  if (!node_id || !metrics) {
    return res.status(400).json({ 
      error: "Missing required fields: node_id and metrics" 
    });
  }

  try {
    // Process metrics through AI Engine and emit to frontend
    const result = await processAgentMetrics(io, { node_id, hostname, metrics });
    res.json({ status: "ok", node_id, processed: true });
  } catch (err) {
    console.error(`[AGENT] Error processing metrics for ${node_id}:`, err.message);
    res.status(500).json({ error: "Failed to process metrics" });
  }
});

// GET /nodes - Returns list of active nodes
app.get("/nodes", (req, res) => {
  const { getActiveNodes } = require("./services/nodeManager");
  res.json({ nodes: getActiveNodes() });
});

// =======================
// SERVER START
// =======================

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`Backend listening on port ${PORT}`);
});
