const HealthCard = ({ health }) => {
  if (!health) return null;

  const color =
    health.risk_level === "NORMAL"
      ? "green"
      : health.risk_level === "WARNING"
      ? "orange"
      : "red";

  return (
    <div style={{ border: `2px solid ${color}`, padding: "1rem", marginBottom: "1rem" }}>
      <h2>System Health</h2>
      <h3 style={{ color }}>{health.health_score}</h3>
      <p>Risk Level: <b>{health.risk_level}</b></p>
    </div>
  );
};

export default HealthCard;
