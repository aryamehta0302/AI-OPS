const axios = require("axios");

const AI_ENGINE_URL = process.env.AI_ENGINE_URL || "http://127.0.0.1:8001";

/**
 * Fetch metrics from AI Engine (legacy single-node polling)
 * Used by socket.js for backward compatibility
 */
async function fetchMetrics() {
  try {
    const response = await axios.get(`${AI_ENGINE_URL}/metrics`, {
      timeout: 20000  // 20s timeout - Ollama LLM can be slow
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
 * @param {Object} agentState - PC agent internal health state (optional)
 * @param {Object} heartbeat - Heartbeat info from agent (optional)
 * @returns {Object} AI-enriched metrics (anomaly, health, root_cause, agent_decision)
 */
async function sendMetricsToAIEngine(nodeId, metrics, agentState = null, heartbeat = null) {
  try {
    const payload = {
      node_id: nodeId,
      metrics: metrics
    };
    
    // Include agent_state if provided (for accurate decision-making)
    if (agentState) {
      payload.agent_state = agentState;
    }
    
    // Include heartbeat if provided
    if (heartbeat) {
      payload.heartbeat = heartbeat;
    }
    
    const response = await axios.post(
      `${AI_ENGINE_URL}/agent/metrics`,
      payload,
      { timeout: 10000 }  // Increased timeout for AI processing
    );
    return response.data;
  } catch (error) {
    console.error(`Failed to send metrics to AI Engine for ${nodeId}: ${error.message}`);
    throw error;
  }
}

module.exports = { fetchMetrics, sendMetricsToAIEngine };
