const axios = require("axios");

const AI_ENGINE_URL = process.env.AI_ENGINE_URL || "http://127.0.0.1:8001";

/**
 * Fetch metrics from AI Engine (legacy single-node polling)
 * Used by socket.js for backward compatibility
 */
async function fetchMetrics() {
  try {
    const response = await axios.get(`${AI_ENGINE_URL}/metrics`, {
      timeout: 5000
    });
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch metrics from AI Engine: ${error.message}`);
    throw error;
  }
}

/**
 * Send agent metrics to AI Engine for processing (multi-node support)
 * @param {string} nodeId - Unique identifier for the node
 * @param {Object} metrics - Raw system metrics from agent
 * @returns {Object} AI-enriched metrics (anomaly, health, root_cause)
 */
async function sendMetricsToAIEngine(nodeId, metrics) {
  try {
    const response = await axios.post(
      `${AI_ENGINE_URL}/agent/metrics`,
      {
        node_id: nodeId,
        metrics: metrics
      },
      { timeout: 5000 }
    );
    return response.data;
  } catch (error) {
    console.error(`Failed to send metrics to AI Engine for ${nodeId}: ${error.message}`);
    throw error;
  }
}

module.exports = { fetchMetrics, sendMetricsToAIEngine };
