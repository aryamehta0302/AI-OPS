/**
 * AUTO-HEALING STATUS COMPONENT
 * ==============================
 * Displays current healing state including:
 * - Active healing indicator
 * - Verification status
 * - Recent healing actions
 * - Adaptive monitoring interval
 */

import { 
  Wrench, 
  CheckCircle2, 
  Loader2, 
  Search, 
  AlertTriangle,
  Shield,
  Activity
} from "lucide-react";
import { motion } from "framer-motion";
import "./HealingStatus.css";

function HealingStatus({ healingStatus, healingActions, nodeId }) {
  if (!healingStatus) {
    return (
      <motion.div 
        className="healing-panel"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="healing-panel-header">
          <Wrench size={18} className="healing-header-icon" />
          <span className="healing-title">AUTO-REMEDIATION</span>
        </div>
        <div className="healing-panel-content">
          <div className="healing-idle">
            <CheckCircle2 size={20} color="#4ade80" />
            <span>System healthy - No action needed</span>
          </div>
        </div>
      </motion.div>
    );
  }

  const {
    active_healing,
    verification_pending,
    consecutive_failures,
    monitoring_interval,
    health_modifier,
    anomaly_modifier
  } = healingStatus;

  // Determine overall status with icons
  let statusType = "idle";
  let statusLabel = "IDLE";
  let StatusIcon = CheckCircle2;
  
  if (active_healing && verification_pending) {
    statusType = "healing";
    statusLabel = "REMEDIATION IN PROGRESS";
    StatusIcon = Loader2;
  } else if (verification_pending) {
    statusType = "verifying";
    statusLabel = "VERIFYING RECOVERY";
    StatusIcon = Search;
  } else if (consecutive_failures > 0) {
    statusType = "failed";
    statusLabel = `REMEDIATION FAILED (${consecutive_failures}x)`;
    StatusIcon = AlertTriangle;
  }

  // Format monitoring interval
  const intervalDisplay = monitoring_interval < 5 
    ? "AGGRESSIVE" 
    : monitoring_interval > 10 
      ? "RELAXED" 
      : "NORMAL";

  return (
    <motion.div 
      className="healing-panel"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="healing-panel-header">
        <Wrench size={18} className="healing-header-icon" />
        <span className="healing-title">AUTO-REMEDIATION</span>
        <span className="healing-node">{nodeId}</span>
      </div>

      {/* Main Status */}
      <div className="healing-panel-content">
        {/* Status Badge */}
        <motion.div 
          className={`healing-status-badge ${statusType}`}
          key={statusType}
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
        >
          <StatusIcon size={20} className={statusType === "healing" ? "spin" : ""} />
          <span className="status-label">{statusLabel}</span>
        </motion.div>

        {/* Monitoring Interval */}
        <div className="healing-monitoring">
          <span className="monitoring-label">MONITORING MODE</span>
          <div className="monitoring-value">
            <span className={`monitoring-mode ${intervalDisplay.toLowerCase()}`}>
              {intervalDisplay}
            </span>
            <span className="monitoring-interval">({monitoring_interval?.toFixed(1)}s)</span>
          </div>
        </div>

        {/* Active Modifiers (if simulated healing active) */}
        {(health_modifier !== 0 || anomaly_modifier !== 0) && (
          <div className="healing-modifiers">
            <span className="modifiers-label">SIMULATED ADJUSTMENTS</span>
            <div className="modifiers-list">
              {health_modifier !== 0 && (
                <span className="modifier-chip health">
                  Health: {health_modifier > 0 ? "+" : ""}{health_modifier?.toFixed(1)}
                </span>
              )}
              {anomaly_modifier !== 0 && (
                <span className="modifier-chip anomaly">
                  Anomaly: {anomaly_modifier > 0 ? "+" : ""}{anomaly_modifier?.toFixed(2)}
                </span>
              )}
            </div>
            <span className="simulated-note">[SIM] Simulation mode - Actual system unchanged</span>
          </div>
        )}

        {/* Recent Actions */}
        {healingActions && healingActions.length > 0 && (
          <div className="healing-actions">
            <span className="actions-label">RECENT ACTIONS</span>
            <div className="actions-list">
              {healingActions.slice(0, 3).map((action, idx) => (
                <div key={idx} className={`action-item ${action.action_type?.toLowerCase()}`}>
                  <div className="action-header">
                    <span className="action-name">{action.action?.replace(/_/g, " ")}</span>
                    <span className={`action-type ${action.action_type?.toLowerCase()}`}>
                      {action.action_type}
                    </span>
                  </div>
                  <span className="action-result">{action.result}</span>
                  <div className="action-footer">
                    <span className={`verification-status ${action.verification_status?.toLowerCase()}`}>
                      {action.verification_status}
                    </span>
                    <span className="action-confidence">
                      {(action.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Idle State */}
        {!active_healing && !verification_pending && consecutive_failures === 0 && (
          <div className="healing-idle">
            <CheckCircle2 size={20} color="#4ade80" />
            <span>No active remediation - System operating normally</span>
          </div>
        )}
      </div>
    </motion.div>
  );
}

export default HealingStatus;
