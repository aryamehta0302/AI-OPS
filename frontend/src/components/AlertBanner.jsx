import { useEffect, useState } from "react";

const AlertBanner = ({ alert, onDismiss }) => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (alert) {
      setVisible(true);
      // Auto-dismiss after 5 seconds
      const timer = setTimeout(() => {
        setVisible(false);
        if (onDismiss) onDismiss();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [alert, onDismiss]);

  if (!alert || !visible) return null;

  const isEscalation = () => {
    const levels = { NORMAL: 0, WARNING: 1, CRITICAL: 2 };
    return levels[alert.to] > levels[alert.from];
  };

  const bannerClass = alert.to.toLowerCase();
  const nodeLabel = alert.node_id ? `[${alert.node_id}] ` : "";

  return (
    <div className={`alert-banner ${bannerClass}`}>
      <div className={`alert-icon ${isEscalation() ? "warning" : "success"}`}></div>
      <div className="alert-content">
        <div className="alert-title">
          {isEscalation() ? "SYSTEM ALERT" : "SYSTEM RECOVERY"}
        </div>
        <div className="alert-message">
          {nodeLabel}Status changed from {alert.from} to {alert.to} | Root Cause: {alert.root_cause}
        </div>
      </div>
      <button
        className="alert-dismiss"
        onClick={() => {
          setVisible(false);
          if (onDismiss) onDismiss();
        }}
      >
        DISMISS
      </button>
    </div>
  );
};

export default AlertBanner;
