let currentState = "NORMAL";
let lastStateChange = Date.now();

const incidentTimeline = [];

function updateState(systemHealth, rootCause) {
  const newState = systemHealth.risk_level;

  if (newState !== currentState) {
    const incident = {
      from: currentState,
      to: newState,
      timestamp: new Date().toISOString(),
      health_score: systemHealth.health_score,
      root_cause: rootCause?.root_cause || "UNKNOWN"
    };

    incidentTimeline.push(incident);

    // keep last 20 incidents only
    if (incidentTimeline.length > 20) {
      incidentTimeline.shift();
    }

    lastStateChange = Date.now();
    currentState = newState;

    return incident;
  }

  return null;
}

function getTimeline() {
  return incidentTimeline;
}

module.exports = {
  updateState,
  getTimeline
};
