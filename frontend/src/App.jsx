import { useEffect, useState } from "react";
import socket from "./services/socket";
import "./App.css";

import HealthCard from "./components/HealthCard";
import RootCauseCard from "./components/RootCauseCard";
import IncidentTimeline from "./components/IncidentTimeline";
import MetricsChart from "./components/MetricsChart";
import ContributorsBar from "./components/ContributorsBar";

function App() {
  const [metrics, setMetrics] = useState([]);
  const [health, setHealth] = useState(null);
  const [rootCause, setRootCause] = useState(null);
  const [incidents, setIncidents] = useState([]);

  useEffect(() => {
    socket.on("system_metrics", (data) => {
      setHealth(data.system_health);
      setRootCause(data.root_cause);

      setMetrics((prev) => [
        ...prev.slice(-30),
        {
          time: new Date().toLocaleTimeString(),
          cpu: data.cpu.usage_percent,
          memory: data.memory.usage_percent
        }
      ]);
    });

    socket.on("incident_event", (incident) => {
      setIncidents((prev) => [incident, ...prev].slice(0, 10));
    });

    return () => {
      socket.off("system_metrics");
      socket.off("incident_event");
    };
  }, []);

  return (
    <div className="dashboard">
      <div className="header">AI Ops System Health Dashboard</div>

      {/* SUMMARY */}
      <div className="row">
        <HealthCard health={health} />
        <RootCauseCard rootCause={rootCause} />
      </div>

      {/* CONTRIBUTORS */}
      {rootCause?.contributors && (
        <div className="section">
          <ContributorsBar contributors={rootCause.contributors} />
        </div>
      )}

      {/* INCIDENTS */}
      <div className="section">
        <IncidentTimeline incidents={incidents} />
      </div>

      {/* CHARTS */}
      <div className="section">
        <MetricsChart
          title="CPU Usage (%)"
          data={metrics}
          dataKey="cpu"
          color="#3498db"
        />
      </div>

      <div className="section">
        <MetricsChart
          title="Memory Usage (%)"
          data={metrics}
          dataKey="memory"
          color="#9b59b6"
        />
      </div>
    </div>
  );
}

export default App;
