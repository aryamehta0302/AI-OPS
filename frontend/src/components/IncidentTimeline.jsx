const IncidentTimeline = ({ incidents, showNodeId = false }) => {
  const isEscalation = (from, to) => {
    const levels = { NORMAL: 0, WARNING: 1, CRITICAL: 2 };
    return levels[to] > levels[from];
  };

  if (!incidents || incidents.length === 0) {
    return (
      <div className="card">
        <h3>INCIDENT TIMELINE {showNodeId && <span className="timeline-subtitle">(All Nodes)</span>}</h3>
        <div className="empty-state">
          <div className="empty-state-icon check-icon"></div>
          <p>No incidents recorded. All systems stable.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3>INCIDENT TIMELINE {showNodeId && <span className="timeline-subtitle">(All Nodes)</span>}</h3>
      <div className="incident-timeline">
        {incidents.map((incident, index) => {
          const escalation = isEscalation(incident.from, incident.to);
          
          return (
            <div key={index} className={`incident-item ${escalation ? "escalation" : "recovery"}`}>
              <div className="incident-line">
                <div className={`incident-dot ${escalation ? "escalation" : "recovery"}`}></div>
              </div>
              <div className="incident-content">
                <div className="incident-header">
                  {/* FIXED: Always show node_id badge for multi-node visibility */}
                  <span className={`incident-node ${incident.node_id === 'local' ? 'local' : 'remote'}`}>
                    {incident.node_id || 'unknown'}
                  </span>
                  <div className="incident-transition">
                    <span className={`risk-badge ${incident.from?.toLowerCase()}`}>{incident.from}</span>
                    <span className="transition-arrow"></span>
                    <span className={`risk-badge ${incident.to?.toLowerCase()}`}>{incident.to}</span>
                  </div>
                </div>
                <div className="incident-details">
                  <span className="detail-item">
                    <span className="detail-label">TIME</span>
                    {new Date(incident.timestamp).toLocaleString()}
                  </span>
                  <span className="detail-item">
                    <span className="detail-label">HEALTH</span>
                    {incident.health_score?.toFixed(1) || 0}%
                  </span>
                  <span className="detail-item">
                    <span className="detail-label">CAUSE</span>
                    {incident.root_cause || 'UNKNOWN'}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default IncidentTimeline;
