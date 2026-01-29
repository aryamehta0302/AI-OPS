from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

from metrics_collector import collect_system_metrics
from anomaly_detector import StreamingAnomalyDetector
from health_evaluator import calculate_health
from root_cause_analyzer import RootCauseAnalyzer
from decision_agent import DecisionAgent
from auto_healer import AutoHealer
from explanation_engine import ExplanationEngine


app = FastAPI(
    title="AI Ops System Health Engine",
    description="Agentic AIOps engine with autonomous decision-making, auto-healing, and explainable AI",
    version="3.0.0"
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

# Global DecisionAgent instance (maintains memory across all nodes)
decision_agent = DecisionAgent(
    memory_window_size=20,
    degradation_threshold=70.0,
    critical_threshold=50.0,
    anomaly_threshold=0.6,
    persistence_threshold=3
)

# Global AutoHealer instance (handles healing actions)
auto_healer = AutoHealer(
    base_sampling_interval=5.0,
    min_sampling_interval=1.0,
    max_sampling_interval=15.0,
    verification_window_seconds=30.0,
    max_healing_attempts=3
)

# Global ExplanationEngine (Ollama integration)
# Uses local Ollama LLM for human-readable explanations
explanation_engine = ExplanationEngine(
    ollama_url="http://localhost:11434",
    model="phi3:mini",
    timeout_seconds=15.0,  # Allow time for model to respond
    enabled=True  # ENABLED - Use Ollama for agentic AI explanations
)


@app.on_event("startup")
async def startup_event():
    """Check Ollama availability and warm up model on startup"""
    available = await explanation_engine.check_availability()
    if available:
        # Warm up the model by sending a simple request
        # This loads the model into VRAM so subsequent requests are fast
        print("[STARTUP] Warming up Ollama model (this may take a moment)...")
        try:
            warmup_result = explanation_engine.explain_decision(
                decision="NO_ACTION",
                root_cause="startup_warmup",
                health_trend="STABLE",
                persistence=0,
                action_taken=None,
                confidence=1.0,
                contributing_factors=["warmup"]
            )
            print(f"[STARTUP] Ollama ready! (generated_by: {warmup_result['generated_by']})")
        except Exception as e:
            print(f"[STARTUP] Ollama warmup failed: {e} (will use fallback)")
    else:
        print("[STARTUP] Ollama not available, using fallback explanations")


def get_or_create_processor(node_id: str):
    """
    Get or create anomaly detector and root cause analyzer for a node.
    Each node has independent streaming state.
    DecisionAgent and AutoHealer are shared globally but maintain per-node memory.
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

    # 5. AGENTIC AI DECISION (for local node)
    agent_reasoning = decision_agent.perceive(
        node_id="local",
        health_score=system_health["health_score"],
        anomaly_score=anomaly_score,
        root_cause=root_cause.get("root_cause"),
        incident_state=None,
        agent_state=None,
        metrics=metrics  # Pass raw metrics for CPU tracking
    )
    
    # Build agent decision dict
    agent_decision = {
        "decision": agent_reasoning.decision,
        "confidence": agent_reasoning.confidence,
        "contributing_factors": agent_reasoning.contributing_factors,
        "persistence": agent_reasoning.persistence,
        "health_trend": agent_reasoning.health_trend,
        "trend_velocity": agent_reasoning.trend_velocity,
        "reasoning_chain": agent_reasoning.reasoning_chain,
        "timestamp": agent_reasoning.timestamp
    }
    
    # Generate explanation - use FALLBACK for local polling (fast)
    # Ollama is used for /agent/metrics endpoint instead
    explanation_result = explanation_engine.explain_decision(
        decision=agent_reasoning.decision,
        root_cause=root_cause.get("root_cause"),
        health_trend=agent_reasoning.health_trend,
        persistence=agent_reasoning.persistence,
        action_taken=None,
        confidence=agent_reasoning.confidence,
        contributing_factors=agent_reasoning.contributing_factors,
        use_fallback=True  # Force fast fallback for local polling
    )
    agent_decision["explanation"] = explanation_result["explanation"]
    agent_decision["explanation_source"] = explanation_result["generated_by"]

    # 6. Generate prediction for local node with actual metrics context
    prediction = generate_prediction("local", anomaly_score, system_health, metrics, root_cause)

    # 7. Enrich response
    metrics["anomaly_score"] = anomaly_score
    metrics["system_health"] = system_health
    metrics["root_cause"] = root_cause
    metrics["prediction"] = prediction
    metrics["agent_decision"] = agent_decision  # Now includes agent decision!
    metrics["node_id"] = "local"

    return metrics


# ==========================================
# MULTI-NODE AGENT ENDPOINT
# ==========================================

class HeartbeatInfo(BaseModel):
    sequence: int = 0
    timestamp: Optional[str] = None
    uptime_seconds: float = 0


class AgentStateInfo(BaseModel):
    """Agent internal health state (from PC agent)"""
    health_state: str = "HEALTHY"  # HEALTHY, DEGRADING, DEGRADED, RECOVERING
    degradation_type: str = "NONE"  # NONE, CPU_PRESSURE, MEMORY_PRESSURE, NETWORK_SATURATION, COMBINED
    degradation_level: float = 0.0  # 0.0 to 1.0
    cycles_in_state: int = 0
    heartbeat_seq: int = 0
    connected: bool = True


class AgentMetricsRequest(BaseModel):
    node_id: str
    metrics: Dict[str, Any]
    hostname: Optional[str] = None
    agent_state: Optional[AgentStateInfo] = None
    heartbeat: Optional[HeartbeatInfo] = None
    simulated_event: bool = False
    target_severity: str = "NORMAL"


@app.post("/agent/metrics")
def process_agent_metrics(request: AgentMetricsRequest):
    """
    Process metrics from a distributed agent.
    Each node_id has independent anomaly detection and root cause analysis.
    
    ENHANCED AGENTIC AI PIPELINE:
    1. Anomaly detection (streaming)
    2. Health scoring
    3. Root cause analysis
    4. DECISION AGENT (autonomous reasoning with connection state awareness)
    5. AUTO-HEALING (safe, non-destructive)
    6. GENAI EXPLANATION (LLM explains, never decides)
    7. Prediction generation
    
    Returns enriched metrics with:
    - anomaly_score (per-node streaming)
    - system_health (per-node)
    - root_cause (per-node analysis)
    - agent_decision (autonomous decision with reasoning)
    - connection_state (CONNECTED/DISCONNECTED)
    - agent_status (ACTIVE/DEGRADED/RECOVERING/OFFLINE)
    - prediction (future risk assessment)
    """
    try:
        node_id = request.node_id
        metrics = request.metrics
        agent_state = request.agent_state
        
        # Determine agent status from agent_state (if provided)
        agent_status = "ACTIVE"
        if agent_state:
            if agent_state.health_state in ["DEGRADED", "DEGRADING"]:
                agent_status = "DEGRADED"
            elif agent_state.health_state == "RECOVERING":
                agent_status = "RECOVERING"
        
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
        
        # 4. AGENTIC AI DECISION ENGINE
        # Agent perceives environment and makes autonomous decisions
        # Now includes agent_state for REAL degradation awareness
        agent_reasoning = decision_agent.perceive(
            node_id=node_id,
            health_score=system_health["health_score"],
            anomaly_score=anomaly_score,
            root_cause=root_cause.get("root_cause"),
            incident_state=None,
            agent_state=agent_state.dict() if agent_state else None,
            metrics=metrics  # Pass raw metrics for CPU tracking
        )
        
        # Convert agent reasoning to dictionary for JSON response
        agent_decision = {
            "decision": agent_reasoning.decision,
            "confidence": agent_reasoning.confidence,
            "contributing_factors": agent_reasoning.contributing_factors,
            "persistence": agent_reasoning.persistence,
            "health_trend": agent_reasoning.health_trend,
            "trend_velocity": agent_reasoning.trend_velocity,
            "reasoning_chain": agent_reasoning.reasoning_chain,
            "timestamp": agent_reasoning.timestamp
        }
        
        # 5. AUTO-HEALING (Task B)
        # Process agent decision and execute safe healing actions
        healing_actions = auto_healer.process_decision(
            node_id=node_id,
            agent_decision=agent_reasoning.decision,
            health_score=system_health["health_score"],
            anomaly_score=anomaly_score,
            confidence=agent_reasoning.confidence
        )
        
        # Get healing status for this node
        healing_status = auto_healer.get_healing_status(node_id)
        
        # Convert healing actions to dicts
        healing_actions_dicts = [
            {
                "action": a.action,
                "action_type": a.action_type,
                "result": a.result,
                "confidence": a.confidence,
                "verification_status": a.verification_status,
                "timestamp": a.timestamp
            }
            for a in healing_actions
        ]
        
        # 6. GENAI EXPLANATION (Task C)
        # Generate human-readable explanation of agent decision
        # LLM only explains - NEVER decides
        explanation_result = explanation_engine.explain_decision(
            decision=agent_reasoning.decision,
            root_cause=root_cause.get("root_cause"),
            health_trend=agent_reasoning.health_trend,
            persistence=agent_reasoning.persistence,
            action_taken=healing_actions[0].action if healing_actions else None,
            confidence=agent_reasoning.confidence,
            contributing_factors=agent_reasoning.contributing_factors
        )
        
        # Add explanation to agent decision
        agent_decision["explanation"] = explanation_result["explanation"]
        agent_decision["explanation_source"] = explanation_result["generated_by"]
        
        # 7. Context-aware prediction based on actual metrics and root cause
        prediction = generate_prediction(node_id, anomaly_score, system_health, metrics, root_cause)
        
        # 8. Build enriched response with full agentic intelligence
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
            "agent_decision": agent_decision,  # Autonomous decision + explanation
            "healing_status": healing_status,  # Auto-healing state
            "healing_actions": healing_actions_dicts,  # Actions taken
            "prediction": prediction,
            # Connection and agent status for multi-agent realism
            "connection_state": "CONNECTED",  # Always CONNECTED when receiving metrics
            "agent_status": agent_status,  # ACTIVE, DEGRADED, RECOVERING
            "agent_state": agent_state.dict() if agent_state else None  # Full agent internal state
        }
    except Exception as e:
        # Log error but return a valid response so the system keeps working
        import traceback
        print(f"[ERROR] process_agent_metrics failed for {request.node_id}: {e}")
        traceback.print_exc()
        
        # Return minimal valid response with error info
        return {
            "node_id": request.node_id,
            "timestamp": request.metrics.get("timestamp") if request.metrics else None,
            "cpu": request.metrics.get("cpu") if request.metrics else None,
            "memory": request.metrics.get("memory") if request.metrics else None,
            "disk": request.metrics.get("disk") if request.metrics else None,
            "network": request.metrics.get("network") if request.metrics else None,
            "anomaly_score": 0.0,
            "system_health": {"health_score": 100.0, "risk_level": "NORMAL"},
            "root_cause": {"root_cause": "ERROR", "contributors": {}},
            "agent_decision": {
                "decision": "NO_ACTION",
                "confidence": 0.0,
                "contributing_factors": ["processing_error"],
                "persistence": 0,
                "health_trend": "STABLE",
                "trend_velocity": 0.0,
                "reasoning_chain": [f"Error during processing: {str(e)}"],
                "timestamp": 0,
                "explanation": f"Processing error: {str(e)}",
                "explanation_source": "error"
            },
            "healing_status": None,
            "healing_actions": [],
            "prediction": {"status": "ERROR", "trend": "UNKNOWN", "risk_forecast": "UNKNOWN", "confidence": 0.0, "message": str(e)},
            "connection_state": "CONNECTED",
            "agent_status": "ACTIVE",
            "agent_state": None
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


@app.get("/agent/decisions")
def get_agent_decisions(limit: int = 10):
    """
    Get recent agent decisions across all nodes
    Shows the agent's autonomous decision history
    """
    return {
        "decisions": decision_agent.get_decision_history(limit=limit),
        "total_nodes": len(decision_agent.node_memories)
    }


@app.get("/agent/memory/{node_id}")
def get_agent_memory(node_id: str):
    """
    Get current agent memory state for a specific node
    Useful for debugging and understanding agent's internal state
    """
    memory = decision_agent.get_node_memory_summary(node_id)
    if memory is None:
        return {"error": f"No memory found for node {node_id}"}
    return memory


# ==========================================
# AUTO-HEALING ENDPOINTS (Task B)
# ==========================================

@app.get("/healing/status/{node_id}")
def get_healing_status(node_id: str):
    """
    Get current healing status for a specific node
    """
    return auto_healer.get_healing_status(node_id)


@app.get("/healing/history")
def get_healing_history(limit: int = 20):
    """
    Get recent healing actions across all nodes
    """
    return {
        "actions": auto_healer.get_healing_history(limit=limit),
        "total_nodes": len(auto_healer.healing_memories)
    }


@app.get("/healing/monitoring/{node_id}")
def get_monitoring_interval(node_id: str):
    """
    Get current adaptive monitoring interval for a node
    """
    interval = auto_healer.get_monitoring_interval(node_id)
    return {
        "node_id": node_id,
        "recommended_interval_seconds": interval
    }


# ==========================================
# EXPLANATION ENGINE ENDPOINTS (Task C)
# ==========================================

@app.get("/explanation/status")
def get_explanation_status():
    """
    Get status of the explanation engine (Ollama)
    """
    return explanation_engine.get_status()


@app.post("/explanation/generate")
def generate_explanation(
    decision: str,
    health_trend: str,
    persistence: int,
    root_cause: Optional[str] = None,
    action_taken: Optional[str] = None,
    confidence: float = 0.8
):
    """
    Generate an explanation for a decision (for testing)
    """
    return explanation_engine.explain_decision(
        decision=decision,
        root_cause=root_cause,
        health_trend=health_trend,
        persistence=persistence,
        action_taken=action_taken,
        confidence=confidence,
        contributing_factors=[]
    )
