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
import { motion, AnimatePresence } from "framer-motion";
import { 
  CheckCircle2, 
  AlertTriangle, 
  ArrowDownCircle, 
  XOctagon, 
  Wrench,
  TrendingUp,
  TrendingDown,
  Minus,
  ChevronsDown,
  Brain,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Bot,
  Activity
} from "lucide-react";
import "./AgentDecisionPanel.css";

function AgentDecisionPanel({ agentDecision, nodeId }) {
  const [expanded, setExpanded] = useState(false);

  if (!agentDecision) {
    return (
      <motion.div 
        className="agent-panel"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="agent-panel-header">
          <Bot size={18} className="agent-header-icon" />
          <span className="agent-title">AUTONOMOUS AGENT</span>
        </div>
        <div className="agent-panel-content">
          <div className="agent-loading">
            <Activity size={20} className="loading-spinner" />
            <span>Awaiting agent analysis...</span>
          </div>
        </div>
      </motion.div>
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
    NO_ACTION: { color: "#4ade80", Icon: CheckCircle2, label: "NO ACTION NEEDED" },
    ESCALATE: { color: "#fbbf24", Icon: AlertTriangle, label: "ESCALATED" },
    DE_ESCALATE: { color: "#60a5fa", Icon: ArrowDownCircle, label: "DE-ESCALATED" },
    PREDICT_FAILURE: { color: "#ef4444", Icon: XOctagon, label: "FAILURE PREDICTED" },
    AUTO_HEAL: { color: "#a855f7", Icon: Wrench, label: "AUTO-HEALING" }
  };

  const style = decisionStyles[decision] || decisionStyles.NO_ACTION;
  const DecisionIcon = style.Icon;

  // Trend icons
  const trendIcons = {
    IMPROVING: TrendingUp,
    STABLE: Minus,
    DEGRADING: TrendingDown,
    CRITICAL_DECLINE: ChevronsDown
  };
  const TrendIcon = trendIcons[health_trend] || Minus;

  const trendColor = {
    IMPROVING: "#4ade80",
    STABLE: "#60a5fa",
    DEGRADING: "#fbbf24",
    CRITICAL_DECLINE: "#ef4444"
  }[health_trend] || "#64748b";

  return (
    <motion.div 
      className="agent-panel"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="agent-panel-header">
        <Bot size={18} className="agent-header-icon" />
        <span className="agent-title">AUTONOMOUS AGENT</span>
        <span className="agent-node">{nodeId}</span>
      </div>

      {/* Main Decision Display */}
      <div className="agent-panel-content">
        {/* Decision Badge */}
        <motion.div 
          className="agent-decision-badge" 
          style={{ backgroundColor: style.color + "20", borderColor: style.color }}
          key={decision}
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
        >
          <DecisionIcon size={22} color={style.color} />
          <span className="decision-label" style={{ color: style.color }}>
            {style.label}
          </span>
        </motion.div>

        {/* Confidence Bar */}
        <div className="agent-confidence">
          <div className="confidence-label">
            <span>CONFIDENCE</span>
            <span className="confidence-value">{(confidence * 100).toFixed(0)}%</span>
          </div>
          <div className="confidence-bar-bg">
            <motion.div 
              className="confidence-bar-fill" 
              initial={{ width: 0 }}
              animate={{ width: `${confidence * 100}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
              style={{ 
                backgroundColor: confidence >= 0.8 ? "#4ade80" : confidence >= 0.6 ? "#fbbf24" : "#ef4444"
              }}
            />
          </div>
        </div>

        {/* Health Trend */}
        <div className="agent-trend">
          <span className="trend-label">HEALTH TREND</span>
          <div className="trend-value">
            <TrendIcon size={18} color={trendColor} />
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
            <span className="explanation-label">AI ANALYSIS</span>
            <span className="explanation-source">
              {explanation_source === "ollama" ? (
                <><Brain size={12} /> LLM</>
              ) : (
                <><BookOpen size={12} /> RULES</>
              )}
            </span>
          </div>
          <p className="explanation-text">{explanation}</p>
        </div>

        {/* Expandable Details */}
        <button 
          className="agent-expand-btn"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? (
            <><ChevronUp size={16} /> HIDE DETAILS</>
          ) : (
            <><ChevronDown size={16} /> SHOW DETAILS</>
          )}
        </button>

        <AnimatePresence>
          {expanded && (
            <motion.div 
              className="agent-details"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              {/* Contributing Factors */}
              {contributing_factors && contributing_factors.length > 0 && (
                <div className="agent-factors">
                  <span className="factors-label">CONTRIBUTING FACTORS</span>
                  <div className="factors-list">
                    {contributing_factors.map((factor, idx) => (
                      <motion.span 
                        key={idx} 
                        className="factor-chip"
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: idx * 0.05 }}
                      >
                        {factor}
                      </motion.span>
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
                      <motion.li 
                        key={idx} 
                        className="reasoning-step"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                      >
                        {step}
                      </motion.li>
                    ))}
                  </ol>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

export default AgentDecisionPanel;
