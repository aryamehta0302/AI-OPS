const HealthCard = ({ health }) => {
  if (!health) return null;

  const classMap = {
    NORMAL: "normal",
    WARNING: "warning",
    CRITICAL: "critical"
  };

  return (
    <div className="card">
      <h3>System Health</h3>
      <div className={`value ${classMap[health.risk_level]}`}>
        {health.health_score}
      </div>
      <p>Risk Level: <b>{health.risk_level}</b></p>
    </div>
  );
};

export default HealthCard;
