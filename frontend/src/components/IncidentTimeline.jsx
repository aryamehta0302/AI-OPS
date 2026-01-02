const IncidentTimeline = ({ incidents }) => {
  if (!incidents || incidents.length === 0) {
    return (
      <div style={{ border: "1px dashed gray", padding: "1rem", marginBottom: "1rem" }}>
        <h3>Incident Timeline</h3>
        <p>No incidents recorded yet.</p>
      </div>
    );
  }

  return (
    <div style={{ border: "2px solid #333", padding: "1rem", marginBottom: "1rem" }}>
      <h3>Incident Timeline</h3>

      <ul style={{ listStyle: "none", padding: 0 }}>
        {incidents.map((incident, index) => (
          <li
            key={index}
            style={{
              marginBottom: "0.75rem",
              paddingBottom: "0.75rem",
              borderBottom: "1px solid #ccc"
            }}
          >
            <p>
              <b>{incident.from}</b> → <b>{incident.to}</b>
            </p>
            <p>
              🕒 {new Date(incident.timestamp).toLocaleString()}
            </p>
            <p>
              ❤️ Health: {incident.health_score}
            </p>
            <p>
              🔍 Root Cause: {incident.root_cause}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default IncidentTimeline;
