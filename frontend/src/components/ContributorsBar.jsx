const colorMap = {
  CPU: "#3498db",
  MEMORY: "#9b59b6",
  DISK: "#f1c40f",
  NETWORK: "#1abc9c"
};

const ContributorsBar = ({ contributors }) => {
  if (!contributors || Object.keys(contributors).length === 0) {
    return null;
  }

  return (
    <div className="card">
      <h3>Metric Contribution</h3>

      {Object.entries(contributors).map(([key, value]) => (
        <div key={key} style={{ marginBottom: "10px" }}>
          <div style={{ fontSize: "14px", marginBottom: "4px" }}>
            {key} — {Math.round(value * 100)}%
          </div>

          <div
            style={{
              height: "10px",
              background: "#e0e0e0",
              borderRadius: "6px",
              overflow: "hidden"
            }}
          >
            <div
              style={{
                width: `${value * 100}%`,
                height: "100%",
                background: colorMap[key] || "#95a5a6"
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};

export default ContributorsBar;
