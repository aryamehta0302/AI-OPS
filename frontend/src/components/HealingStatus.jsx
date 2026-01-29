/**
 * AUTO-HEALING STATUS COMPONENT
 * ==============================
 * Displays current healing state including:
 * - Active healing indicator
 * - Verification status
 * - Recent healing actions
 * - Adaptive monitoring interval
 */

import "./HealingStatus.css";

function HealingStatus({ healingStatus, healingActions, nodeId }) {
  if (!healingStatus) {
    return (
      <div className="healing-panel">
        <div className="healing-panel-header">
          <span className="healing-icon">🔧</span>
          <span className="healing-title">AUTO-HEALING</span>
        </div>
        <div className="healing-panel-content">
          <div className="healing-idle">
            <span className="idle-icon">✓</span>
            <span>System healthy - No healing needed</span>
          </div>
        </div>
      </div>
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

  // Determine overall status
  let statusType = "idle";
  let statusLabel = "IDLE";
  let statusIcon = "✓";
  
  if (active_healing && verification_pending) {
    statusType = "healing";
    statusLabel = "HEALING IN PROGRESS";
    statusIcon = "⟳";
  } else if (verification_pending) {
    statusType = "verifying";
    statusLabel = "VERIFYING RECOVERY";
    statusIcon = "🔍";
  } else if (consecutive_failures > 0) {
    statusType = "failed";
    statusLabel = `HEALING FAILED (${consecutive_failures}x)`;
    statusIcon = "⚠";
  }

  // Format monitoring interval
  const intervalDisplay = monitoring_interval < 5 
    ? "AGGRESSIVE" 
    : monitoring_interval > 10 
      ? "RELAXED" 
      : "NORMAL";

  return (
    <div className="healing-panel">
      {/* Header */}
      <div className="healing-panel-header">
        <span className="healing-icon">🔧</span>
        <span className="healing-title">AUTO-HEALING</span>
        <span className="healing-node">{nodeId}</span>
      </div>

      {/* Main Status */}
      <div className="healing-panel-content">
        {/* Status Badge */}
        <div className={`healing-status-badge ${statusType}`}>
          <span className="status-icon">{statusIcon}</span>
          <span className="status-label">{statusLabel}</span>
        </div>

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
            <span className="simulated-note">⚠️ SIMULATED - Actual system unchanged</span>
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
            <span className="idle-icon">✓</span>
            <span>No active healing - System operating normally</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default HealingStatus;
