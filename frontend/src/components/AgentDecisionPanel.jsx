/**
 * AGENT DECISION PANEL
 * =====================
 * Displays autonomous agent decisions with:
 * - Current decision and confidence
 * - AI-generated explanation (from Ollama)
 * - Contributing factors
 * - Reasoning chain
 * 
 * This is NOT a chatbot - it shows agent's autonomous decisions
 */

import { useState } from "react";
import "./AgentDecisionPanel.css";

function AgentDecisionPanel({ agentDecision, nodeId }) {
  const [expanded, setExpanded] = useState(false);

  if (!agentDecision) {
    return (
      <div className="agent-panel">
        <div className="agent-panel-header">
          <span className="agent-icon">🤖</span>
          <span className="agent-title">AGENT DECISION</span>
        </div>
        <div className="agent-panel-content">
          <div className="agent-loading">
            <span>Awaiting agent analysis...</span>
          </div>
        </div>
      </div>
    );
  }

  const {
    decision,
    confidence,
    explanation,
    explanation_source,
    health_trend,
    persistence,
    contributing_factors,
    reasoning_chain,
    trend_velocity
  } = agentDecision;

  // Decision styling based on type
  const decisionStyles = {
    NO_ACTION: { color: "#4ade80", icon: "✓", label: "NO ACTION NEEDED" },
    ESCALATE: { color: "#fbbf24", icon: "⚠", label: "ESCALATED" },
    DE_ESCALATE: { color: "#60a5fa", icon: "↓", label: "DE-ESCALATED" },
    PREDICT_FAILURE: { color: "#ef4444", icon: "🚨", label: "FAILURE PREDICTED" },
    AUTO_HEAL: { color: "#a855f7", icon: "🔧", label: "AUTO-HEALING" }
  };

  const style = decisionStyles[decision] || decisionStyles.NO_ACTION;

  // Trend arrow
  const trendIcon = {
    IMPROVING: "↑",
    STABLE: "→",
    DEGRADING: "↓",
    CRITICAL_DECLINE: "⬇"
  }[health_trend] || "→";

  const trendColor = {
    IMPROVING: "#4ade80",
    STABLE: "#60a5fa",
    DEGRADING: "#fbbf24",
    CRITICAL_DECLINE: "#ef4444"
  }[health_trend] || "#64748b";

  return (
    <div className="agent-panel">
      {/* Header */}
      <div className="agent-panel-header">
        <span className="agent-icon">🤖</span>
        <span className="agent-title">AGENT DECISION</span>
        <span className="agent-node">{nodeId}</span>
      </div>

      {/* Main Decision Display */}
      <div className="agent-panel-content">
        {/* Decision Badge */}
        <div className="agent-decision-badge" style={{ backgroundColor: style.color + "20", borderColor: style.color }}>
          <span className="decision-icon">{style.icon}</span>
          <span className="decision-label" style={{ color: style.color }}>
            {style.label}
          </span>
        </div>

        {/* Confidence Bar */}
        <div className="agent-confidence">
          <div className="confidence-label">
            <span>CONFIDENCE</span>
            <span className="confidence-value">{(confidence * 100).toFixed(0)}%</span>
          </div>
          <div className="confidence-bar-bg">
            <div 
              className="confidence-bar-fill" 
              style={{ 
                width: `${confidence * 100}%`,
                backgroundColor: confidence >= 0.8 ? "#4ade80" : confidence >= 0.6 ? "#fbbf24" : "#ef4444"
              }}
            />
          </div>
        </div>

        {/* Health Trend */}
        <div className="agent-trend">
          <span className="trend-label">HEALTH TREND</span>
          <div className="trend-value">
            <span className="trend-icon" style={{ color: trendColor }}>{trendIcon}</span>
            <span style={{ color: trendColor }}>{health_trend?.replace("_", " ")}</span>
            {trend_velocity && (
              <span className="trend-velocity">({trend_velocity > 0 ? "+" : ""}{trend_velocity.toFixed(2)}/cycle)</span>
            )}
          </div>
        </div>

        {/* Persistence */}
        {persistence > 0 && (
          <div className="agent-persistence">
            <span className="persistence-label">PERSISTENCE</span>
            <span className="persistence-value">{persistence} cycles</span>
          </div>
        )}

        {/* AI Explanation */}
        <div className="agent-explanation">
          <div className="explanation-header">
            <span className="explanation-label">AI EXPLANATION</span>
            <span className="explanation-source">
              {explanation_source === "ollama" ? "🧠 Ollama" : "📋 Fallback"}
            </span>
          </div>
          <p className="explanation-text">{explanation}</p>
        </div>

        {/* Expandable Details */}
        <button 
          className="agent-expand-btn"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? "Hide Details ▲" : "Show Details ▼"}
        </button>

        {expanded && (
          <div className="agent-details">
            {/* Contributing Factors */}
            {contributing_factors && contributing_factors.length > 0 && (
              <div className="agent-factors">
                <span className="factors-label">CONTRIBUTING FACTORS</span>
                <div className="factors-list">
                  {contributing_factors.map((factor, idx) => (
                    <span key={idx} className="factor-chip">{factor}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Reasoning Chain */}
            {reasoning_chain && reasoning_chain.length > 0 && (
              <div className="agent-reasoning">
                <span className="reasoning-label">REASONING CHAIN</span>
                <ol className="reasoning-list">
                  {reasoning_chain.map((step, idx) => (
                    <li key={idx} className="reasoning-step">{step}</li>
                  ))}
                </ol>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default AgentDecisionPanel;
