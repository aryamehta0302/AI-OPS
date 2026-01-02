require("dotenv").config();
const express = require("express");
const http = require("http");
const cors = require("cors");
const { Server } = require("socket.io");

const setupSocket = require("./socket");
const { getTimeline } = require("./services/incidentManager");

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: "*"
  }
});

// Initialize Socket.IO streaming
setupSocket(io);

// =======================
// REST API ENDPOINTS
// =======================

// Health check
app.get("/health", (req, res) => {
  res.json({ status: "Backend running" });
});

// Incident timeline (AIOps feature)
app.get("/incidents", (req, res) => {
  res.json({
    count: getTimeline().length,
    incidents: getTimeline()
  });
});

// =======================
// SERVER START
// =======================

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`Backend listening on port ${PORT}`);
});
