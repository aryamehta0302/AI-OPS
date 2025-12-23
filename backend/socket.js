const { fetchMetrics } = require("./services/aiEngineClient");

function setupSocket(io) {
  console.log("Socket.IO initialized");

  setInterval(async () => {
    try {
      const metrics = await fetchMetrics();
      io.emit("system_metrics", metrics);
    } catch (err) {
      console.error("Error fetching metrics:", err.message);
    }
  }, parseInt(process.env.POLL_INTERVAL_MS));
}

module.exports = setupSocket;
