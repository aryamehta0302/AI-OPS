const axios = require("axios");

const AI_ENGINE_URL = process.env.AI_ENGINE_URL;

async function fetchMetrics() {
  const response = await axios.get(`${AI_ENGINE_URL}/metrics`);
  return response.data;
}

module.exports = { fetchMetrics };
