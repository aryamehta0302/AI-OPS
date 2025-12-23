import { useEffect, useState } from "react";
import socket from "./services/socket";
import HealthCard from "./components/HealthCard";
import MetricsChart from "./components/MetricsChart";

function App() {
  const [metrics, setMetrics] = useState([]);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    socket.on("system_metrics", (data) => {
      setHealth(data.system_health);

      setMetrics((prev) => [
        ...prev.slice(-20),
        {
          time: new Date().toLocaleTimeString(),
          cpu: data.cpu.usage_percent,
          memory: data.memory.usage_percent
        }
      ]);
    });

    return () => socket.off("system_metrics");
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>AIOps System Health Dashboard</h1>

      <HealthCard health={health} />

      <MetricsChart
        title="CPU Usage (%)"
        data={metrics}
        dataKey="cpu"
        color="blue"
      />

      <MetricsChart
        title="Memory Usage (%)"
        data={metrics}
        dataKey="memory"
        color="purple"
      />
    </div>
  );
}

export default App;
