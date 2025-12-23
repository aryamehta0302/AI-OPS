def calculate_health(anomaly_score: float) -> dict:
    """
    Converts anomaly score into system health score and risk level
    """

    # Normalize anomaly score to health (simple & explainable)
    health_score = max(0, 100 - (anomaly_score * 100))

    if health_score >= 80:
        risk = "NORMAL"
    elif 50 <= health_score < 80:
        risk = "WARNING"
    else:
        risk = "CRITICAL"

    return {
        "health_score": round(health_score, 2),
        "risk_level": risk
    }
