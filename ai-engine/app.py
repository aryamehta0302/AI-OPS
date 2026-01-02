from fastapi import FastAPI

from metrics_collector import collect_system_metrics
from anomaly_detector import StreamingAnomalyDetector
from health_evaluator import calculate_health
from root_cause_analyzer import RootCauseAnalyzer


app = FastAPI(
    title="AI Ops System Health Engine",
    description="Real-time AIOps engine with anomaly detection, health scoring, and root-cause analysis",
    version="1.1.0"
)

# Initialize streaming components (stateful)
anomaly_detector = StreamingAnomalyDetector()
root_cause_analyzer = RootCauseAnalyzer()


@app.get("/health")
def health_check():
    """
    Service health check
    """
    return {"status": "AI Engine running"}


@app.get("/metrics")
def get_system_metrics():
    """
    Returns real-time system metrics enriched with:
    - anomaly score
    - system health
    - root-cause attribution
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

    # 5. Enrich response
    metrics["anomaly_score"] = anomaly_score
    metrics["system_health"] = system_health
    metrics["root_cause"] = root_cause

    return metrics
