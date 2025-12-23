from fastapi import FastAPI
from metrics_collector import collect_system_metrics
from anomaly_detector import StreamingAnomalyDetector
from health_evaluator import calculate_health

app = FastAPI(
    title="AI Ops System Health Engine",
    description="Real-time system metrics, anomaly detection & health scoring",
    version="1.0.0"
)

detector = StreamingAnomalyDetector()


@app.get("/health")
def health_check():
    return {"status": "AI Engine running"}


@app.get("/metrics")
def get_system_metrics():
    metrics = collect_system_metrics()

    anomaly_score = detector.process(metrics)
    health = calculate_health(anomaly_score)

    metrics["anomaly_score"] = anomaly_score
    metrics["system_health"] = health

    return metrics
