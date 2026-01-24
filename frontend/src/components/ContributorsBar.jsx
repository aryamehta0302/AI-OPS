const colorMap = {
  CPU: "#00d4ff",
  MEMORY: "#a855f7",
  DISK: "#fbbf24",
  NETWORK: "#14b8a6"
};

const ContributorsBar = ({ contributors }) => {
  if (!contributors || Object.keys(contributors).length === 0) {
    return null;
  }

  // Sort by contribution (highest first)
  const sorted = Object.entries(contributors).sort((a, b) => b[1] - a[1]);

  return (
    <div className="card">
      <h3>METRIC CONTRIBUTION</h3>

      <div className="contributors-grid">
        {sorted.map(([key, value]) => (
          <div key={key} className="contributor-item">
            <div className="contributor-header">
              <span className={`contributor-icon ${key.toLowerCase()}`}></span>
              <span className="contributor-name">{key}</span>
              <span 
                className="contributor-percent"
                style={{ color: colorMap[key] || "#94a3b8" }}
              >
                {Math.round(value * 100)}%
              </span>
            </div>

            <div className="contributor-bar-bg">
              <div
                className="contributor-bar-fill"
                style={{
                  width: `${value * 100}%`,
                  background: colorMap[key] || "#94a3b8"
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ContributorsBar;
