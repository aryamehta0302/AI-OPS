/**
 * socket.js
 * 
 * Legacy single-node polling for backward compatibility.
 * When no distributed agents are connected, this polls the AI Engine
 * directly using local system metrics.
 * 
 * For multi-node setups, agents POST to /agent/metrics instead.
 */

const { fetchMetrics } = require("./services/aiEngineClient");
const { updateState } = require("./services/incidentManager");

const interval = Number(process.env.POLL_INTERVAL_MS) || 2000;

function setupSocket(io) {
  console.log(`Socket.IO initialized (legacy polling every ${interval}ms)`);

  setInterval(async () => {
    try {
      const metrics = await fetchMetrics();

      // Add node_id for consistency with multi-node events
      // "local" indicates this is from the legacy single-node polling
      const enrichedMetrics = {
        node_id: "local",
        hostname: "local",
        ...metrics
      };

      // Update incident state (uses "local" as node_id internally)
      const incident = updateState(
        "local",
        metrics.system_health,
        metrics.root_cause
      );

      // Always emit metrics with node_id
      io.emit("system_metrics", enrichedMetrics);

      // Emit incident only on state change
      if (incident) {
        io.emit("incident_event", incident);
      }
    } catch (err) {
      // Silently fail if AI Engine is not running
      // (may be using agent-based model instead)
      if (process.env.DEBUG) {
        console.error("Legacy polling error:", err.message);
      }
    }
  }, interval);
}

module.exports = setupSocket;
