const AlertBanner = ({ alert }) => {
  if (!alert) return null;

  const colorMap = {
    NORMAL: "#2ecc71",
    WARNING: "#f39c12",
    CRITICAL: "#e74c3c"
  };

  return (
    <div
      className="card"
      style={{
        borderLeft: `6px solid ${colorMap[alert.to]}`
      }}
    >
      <b>{alert.from} → {alert.to}</b>
      <p>Root Cause: {alert.root_cause}</p>
    </div>
  );
};

export default AlertBanner;
