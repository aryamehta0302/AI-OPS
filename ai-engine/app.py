from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from metrics_collector import collect_system_metrics
from anomaly_detector import StreamingAnomalyDetector
from health_evaluator import calculate_health
from root_cause_analyzer import RootCauseAnalyzer


app = FastAPI(
    title="AI Ops System Health Engine",
    description="Real-time AIOps engine with anomaly detection, health scoring, and root-cause analysis",
    version="2.0.0"
)

# Enable CORS for frontend/backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# MULTI-NODE STATE MANAGEMENT
# ==========================================

# Per-node streaming components: { node_id: { detector, analyzer } }
node_processors = {}


def get_or_create_processor(node_id: str):
    """
    Get or create anomaly detector and root cause analyzer for a node.
    Each node has independent streaming state.
    """
    if node_id not in node_processors:
        node_processors[node_id] = {
            "detector": StreamingAnomalyDetector(),
            "analyzer": RootCauseAnalyzer()
        }
    return node_processors[node_id]


# ==========================================
# LEGACY SINGLE-NODE (backward compatibility)
# ==========================================

# Initialize streaming components for local metrics
anomaly_detector = StreamingAnomalyDetector()
root_cause_analyzer = RootCauseAnalyzer()


@app.get("/health")
def health_check():
    """
    Service health check
    """
    return {"status": "AI Engine running", "version": "2.0.0", "multi_node": True}


@app.get("/metrics")
def get_system_metrics():
    """
    Returns real-time system metrics enriched with:
    - anomaly score
    - system health
    - root-cause attribution
    - prediction (FIXED: was missing, causing infinite loading)
    (Legacy endpoint for single-node polling)
    """

    # 1. Collect raw system metrics
    metrics = collect_system_metrics()

    # 2. Streaming anomaly detection
    anomaly_score = anomaly_detector.process(metrics)

    # 3. Health score & risk level
    system_health = calculate_health(anomaly_score)

    # 4. Root-cause analysis (explainability)
    root_cause_analyzer.update(metrics)
    root_cause = root_cause_analyzer.analyze(metrics)

    # 5. Generate prediction for local node with actual metrics context
    prediction = generate_prediction("local", anomaly_score, system_health, metrics, root_cause)

    # 6. Enrich response
    metrics["anomaly_score"] = anomaly_score
    metrics["system_health"] = system_health
    metrics["root_cause"] = root_cause
    metrics["prediction"] = prediction  # Now included!

    return metrics


# ==========================================
# MULTI-NODE AGENT ENDPOINT
# ==========================================

class AgentMetricsRequest(BaseModel):
    node_id: str
    metrics: Dict[str, Any]


@app.post("/agent/metrics")
def process_agent_metrics(request: AgentMetricsRequest):
    """
    Process metrics from a distributed agent.
    Each node_id has independent anomaly detection and root cause analysis.
    
    Returns enriched metrics with:
    - anomaly_score (per-node streaming)
    - system_health (per-node)
    - root_cause (per-node analysis)
    - prediction (future risk assessment)
    """
    node_id = request.node_id
    metrics = request.metrics
    
    # Get or create processor for this node
    processor = get_or_create_processor(node_id)
    detector = processor["detector"]
    analyzer = processor["analyzer"]
    
    # 1. Streaming anomaly detection (per-node)
    anomaly_score = detector.process(metrics)
    
    # 2. Health score & risk level
    system_health = calculate_health(anomaly_score)
    
    # 3. Root-cause analysis (per-node history)
    analyzer.update(metrics)
    root_cause = analyzer.analyze(metrics)
    
    # 4. Context-aware prediction based on actual metrics and root cause
    prediction = generate_prediction(node_id, anomaly_score, system_health, metrics, root_cause)
    
    # 5. Build enriched response
    return {
        "node_id": node_id,
        "timestamp": metrics.get("timestamp"),
        "cpu": metrics.get("cpu"),
        "memory": metrics.get("memory"),
        "disk": metrics.get("disk"),
        "network": metrics.get("network"),
        "anomaly_score": anomaly_score,
        "system_health": system_health,
        "root_cause": root_cause,
        "prediction": prediction
    }


# ==========================================
# PREDICTION ENGINE
# ==========================================

# Store recent anomaly scores for trend analysis
node_anomaly_history = {}
HISTORY_SIZE = 10


def generate_prediction(node_id: str, current_score: float, health: dict, metrics: dict = None, root_cause: dict = None) -> dict:
    """
    Generate CONTEXT-AWARE predictive insights based on:
    - Anomaly trend history
    - Current health state  
    - Actual metrics values (CPU, memory, disk)
    - Root cause analysis
    ALWAYS returns a valid status to prevent infinite loading in frontend.
    """
    # Initialize history for new nodes
    if node_id not in node_anomaly_history:
        node_anomaly_history[node_id] = []
    
    history = node_anomaly_history[node_id]
    history.append(current_score)
    
    # Keep only recent history
    if len(history) > HISTORY_SIZE:
        history.pop(0)
    
    # Only need 2 data points for prediction
    if len(history) < 2:
        return {
            "status": "INSUFFICIENT_DATA",
            "trend": "ANALYZING",
            "risk_forecast": "INSUFFICIENT_DATA",
            "confidence": 0.0,
            "message": "Collecting baseline data..."
        }
    
    # Extract actual metric values for context-aware messages
    cpu_usage = metrics.get("cpu", {}).get("usage_percent", 0) if metrics else 0
    mem_usage = metrics.get("memory", {}).get("usage_percent", 0) if metrics else 0
    disk_usage = metrics.get("disk", {}).get("usage_percent", 0) if metrics else 0
    primary_cause = root_cause.get("root_cause", "UNKNOWN") if root_cause else "UNKNOWN"
    
    # Calculate trend from available history
    recent = history[-5:] if len(history) >= 5 else history
    avg_recent = sum(recent) / len(recent)
    avg_older = sum(history[:-len(recent)]) / max(1, len(history[:-len(recent)])) if len(history) > len(recent) else avg_recent
    
    trend_delta = avg_recent - avg_older
    
    # Factor in current health state for immediate responsiveness
    if current_score > 0.5:
        trend_delta += (current_score - 0.3) * 0.5
    
    # Generate CONTEXT-AWARE prediction messages based on actual metrics
    if trend_delta > 0.03 or health["risk_level"] == "CRITICAL":
        trend = "DEGRADING"
        if health["risk_level"] == "CRITICAL":
            risk_forecast = "HIGH"
            # Context-aware critical message
            if primary_cause == "CPU":
                message = f"⚠️ CPU critical at {cpu_usage:.1f}% - process overload likely"
            elif primary_cause == "MEMORY":
                message = f"⚠️ Memory critical at {mem_usage:.1f}% - risk of OOM"
            elif primary_cause == "DISK":
                message = f"⚠️ Disk critical at {disk_usage:.1f}% - storage exhaustion imminent"
            else:
                message = f"⚠️ System critical - {primary_cause} is primary factor"
            eta_minutes = max(2, int(15 / (trend_delta * 10 + 0.2)))
        elif health["risk_level"] == "WARNING":
            risk_forecast = "HIGH"
            # Context-aware warning message
            if primary_cause == "CPU":
                message = f"CPU elevated at {cpu_usage:.1f}% - may escalate to critical"
            elif primary_cause == "MEMORY":
                message = f"Memory pressure at {mem_usage:.1f}% - monitor for leaks"
            elif primary_cause == "DISK":
                message = f"Disk usage at {disk_usage:.1f}% - consider cleanup"
            else:
                message = f"Degradation detected - {primary_cause} trending up"
            eta_minutes = max(5, int(25 / (trend_delta * 10 + 0.1)))
        else:
            risk_forecast = "MEDIUM"
            message = f"Minor anomaly detected in {primary_cause.lower()}"
            eta_minutes = max(10, int(40 / (trend_delta * 10 + 0.1)))
        status = "FAILURE_LIKELY"
    elif trend_delta < -0.03:
        trend = "IMPROVING"
        risk_forecast = "LOW"
        # Context-aware recovery message
        if cpu_usage < 30 and mem_usage < 50:
            message = f"✓ Recovered - CPU {cpu_usage:.1f}%, Memory {mem_usage:.1f}%"
        else:
            message = f"✓ Improving - {primary_cause} returning to normal"
        status = "STABLE"
        eta_minutes = None
    else:
        trend = "STABLE"
        if health["risk_level"] == "WARNING":
            risk_forecast = "MEDIUM"
            message = f"Stable but elevated - {primary_cause} at moderate levels"
        else:
            risk_forecast = "LOW"
            # Show actual healthy stats
            message = f"✓ Healthy - CPU {cpu_usage:.1f}%, Mem {mem_usage:.1f}%, Disk {disk_usage:.1f}%"
        status = "STABLE"
        eta_minutes = None
    
    # Confidence based on data points and consistency
    data_confidence = min(1.0, len(history) / HISTORY_SIZE)  # More data = more confidence
    variance = sum((x - avg_recent) ** 2 for x in recent) / len(recent)
    consistency_confidence = max(0.3, 1.0 - variance)
    confidence = min(0.95, data_confidence * 0.4 + consistency_confidence * 0.6)  # Capped at 95%
    
    result = {
        "status": status,  # Explicit status: STABLE, FAILURE_LIKELY, INSUFFICIENT_DATA
        "trend": trend,
        "risk_forecast": risk_forecast,
        "confidence": round(confidence, 2),
        "message": message
    }
    
    # Include ETA only when failure is likely
    if eta_minutes is not None:
        result["eta_minutes"] = eta_minutes
    
    return result


@app.get("/nodes")
def get_active_nodes():
    """
    Returns list of nodes that have sent metrics to the AI Engine
    """
    return {
        "nodes": list(node_processors.keys()),
        "count": len(node_processors)
    }
