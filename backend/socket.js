const { fetchMetrics } = require("./services/aiEngineClient");
const { updateState } = require("./services/incidentManager");

const interval = Number(process.env.POLL_INTERVAL_MS);

function setupSocket(io) {
  console.log("Socket.IO initialized");

  setInterval(async () => {
    try {
      const metrics = await fetchMetrics();

      // update incident state
      const incident = updateState(
        metrics.system_health,
        metrics.root_cause
      );

      // always emit metrics
      io.emit("system_metrics", metrics);

      // emit incident only on state change
      if (incident) {
        io.emit("incident_event", incident);
      }
    } catch (err) {
      console.error("Error fetching metrics:", err.message);
    }
  }, interval);
}

module.exports = setupSocket;
