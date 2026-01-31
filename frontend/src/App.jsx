import { useEffect, useState } from "react";
import socket from "./services/socket";
import "./App.css";

import NodeSelector from "./components/NodeSelector";
import NodeGrid from "./components/NodeGrid";
import HealthCard from "./components/HealthCard";
import RootCauseCard from "./components/RootCauseCard";
import PredictionCard from "./components/PredictionCard";
import IncidentTimeline from "./components/IncidentTimeline";
import MetricsChart from "./components/MetricsChart";
import ContributorsBar from "./components/ContributorsBar";
import AlertBanner from "./components/AlertBanner";
import AgentDecisionPanel from "./components/AgentDecisionPanel";
import HealingStatus from "./components/HealingStatus";
import ConnectionIndicator, { ConnectionDot } from "./components/ConnectionIndicator";

function App() {
  // Multi-node state: { node_id: { metrics, health, rootCause, prediction, agentDecision, healingStatus, history } }
  const [nodes, setNodes] = useState({});
  const [selectedNode, setSelectedNode] = useState("all");
  const [incidents, setIncidents] = useState([]);
  const [latestAlert, setLatestAlert] = useState(null);
  // FIXED: Initialize with actual socket connection state
  const [connected, setConnected] = useState(socket.connected);

  useEffect(() => {
    // FIXED: Check current connection state on mount (in case already connected)
    if (socket.connected) {
      setConnected(true);
    }

    socket.on("connect", () => {
      console.log("[Socket] Connected to backend");
      setConnected(true);
    });

    socket.on("disconnect", () => {
      console.log("[Socket] Disconnected from backend");
      setConnected(false);
    });

    socket.on("system_metrics", (data) => {
      const nodeId = data.node_id || "local";
      
      setNodes((prev) => {
        const existing = prev[nodeId] || { history: [] };
        const newHistory = [
          ...existing.history.slice(-30),
          {
            time: new Date().toLocaleTimeString(),
            cpu: data.cpu?.usage_percent || 0,
            memory: data.memory?.usage_percent || 0,
            disk: data.disk?.usage_percent || 0
          }
        ];

        return {
          ...prev,
          [nodeId]: {
            node_id: nodeId,
            hostname: data.hostname || nodeId,
            metrics: data,
            health: data.system_health,
            rootCause: data.root_cause,
            prediction: data.prediction,
            agentDecision: data.agent_decision,
            healingStatus: data.healing_status,
            healingActions: data.healing_actions,
            // NEW: Include agent state and status for multi-agent visibility
            agentState: data.agent_state,
            agentStatus: data.agent_status || "ACTIVE",
            connectionState: data.connection_state || "CONNECTED",
            history: newHistory,
            lastSeen: Date.now(),
            connectionStatus: "CONNECTED"
          }
        };
      });
    });

    // Handle per-node connection status updates from backend
    socket.on("node_status_update", (data) => {
      const { node_id, status, agent_status, connection_state } = data;
      
      setNodes((prev) => {
        if (!prev[node_id]) return prev;
        
        return {
          ...prev,
          [node_id]: {
            ...prev[node_id],
            connectionStatus: status,
            connectionState: connection_state || status,
            agentStatus: agent_status || (status === "DISCONNECTED" ? "OFFLINE" : "ACTIVE"),
            lastSeen: data.lastSeen || prev[node_id].lastSeen
          }
        };
      });
    });

    socket.on("incident_event", (incident) => {
      setIncidents((prev) => [incident, ...prev].slice(0, 20));
      setLatestAlert(incident);
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("system_metrics");
      socket.off("incident_event");
      socket.off("node_status_update");  // Cleanup new listener
    };
  }, []);

  // Get list of active node IDs
  const nodeIds = Object.keys(nodes);

  // Get data for selected node or aggregate
  const getSelectedData = () => {
    if (selectedNode === "all" || !nodes[selectedNode]) {
      // Return first available node for display, or null
      const firstNode = nodeIds.length > 0 ? nodes[nodeIds[0]] : null;
      return firstNode;
    }
    return nodes[selectedNode];
  };

  // Filter incidents by selected node
  const filteredIncidents = selectedNode === "all" 
    ? incidents 
    : incidents.filter(inc => inc.node_id === selectedNode);

  const selectedData = getSelectedData();

  return (
    <div className="dashboard">
      {/* Alert Banner */}
      <AlertBanner 
        alert={latestAlert} 
        onDismiss={() => setLatestAlert(null)} 
      />

      {/* Header */}
      <div className="header">
        <div className="header-title">
          <span className="header-icon"></span>
          AIOPS SYSTEM HEALTH PLATFORM
        </div>
        <div className="header-status">
          <ConnectionIndicator 
            isConnected={connected} 
            label="ENGINE STATUS"
          />
        </div>
      </div>

      {/* Node Selector */}
      <NodeSelector 
        nodes={nodeIds}
        selected={selectedNode}
        onSelect={setSelectedNode}
        nodeData={nodes}
      />

      {/* Node Grid - Shows all nodes when "all" selected */}
      {selectedNode === "all" && nodeIds.length > 0 && (
        <NodeGrid nodes={nodes} onSelectNode={setSelectedNode} />
      )}

      {/* Single Node Details */}
      {selectedNode !== "all" && selectedData && (
        <>
          {/* Summary Cards */}
          <div className="row">
            <HealthCard health={selectedData.health} nodeId={selectedNode} />
            <RootCauseCard rootCause={selectedData.rootCause} />
            <PredictionCard prediction={selectedData.prediction} />
          </div>

          {/* Contributors */}
          {selectedData.rootCause?.contributors && (
            <div className="section">
              <ContributorsBar contributors={selectedData.rootCause.contributors} />
            </div>
          )}

          {/* Charts */}
          <div className="row">
            <MetricsChart
              title="CPU UTILIZATION"
              data={selectedData.history}
              dataKey="cpu"
              color="#00d4ff"
            />
            <MetricsChart
              title="MEMORY UTILIZATION"
              data={selectedData.history}
              dataKey="memory"
              color="#a855f7"
            />
          </div>

          {/* Agentic AI Section */}
          <div className="agentic-section">
            <h3 className="section-title">AUTONOMOUS INTELLIGENCE</h3>
            <div className="agentic-row">
              <AgentDecisionPanel 
                agentDecision={selectedData.agentDecision}
                nodeId={selectedNode}
              />
              <HealingStatus 
                healingStatus={selectedData.healingStatus}
                healingActions={selectedData.healingActions}
                nodeId={selectedNode}
              />
            </div>
          </div>
        </>
      )}

      {/* Incidents */}
      <div className="section">
        <IncidentTimeline incidents={filteredIncidents} showNodeId={selectedNode === "all"} />
      </div>

      {/* Empty State */}
      {nodeIds.length === 0 && (
        <div className="empty-dashboard">
          <div className="empty-icon"></div>
          <h2>AWAITING NODE CONNECTIONS</h2>
          <p>Start monitoring agents to begin system analysis</p>
          <code>python agent.py --node-id PC-1</code>
        </div>
      )}
    </div>
  );
}

export default App;
