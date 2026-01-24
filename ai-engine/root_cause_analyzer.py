from collections import deque
import statistics


class RootCauseAnalyzer:
    """
    Accuracy-optimized Root Cause Analyzer for AIOps.

    Key properties:
    - Rolling baseline comparison
    - Network handled as RATE (not cumulative)
    - Metric-aware weighting (domain knowledge)
    - Temporal persistence (noise reduction)
    - Normalized confidence (0–1)
    - Multi-metric contribution breakdown
    """

    def __init__(self, window_size=20, persistence_window=5):
        self.window_size = window_size
        self.persistence_window = persistence_window

        # Rolling metric history
        self.history = {
            "cpu": deque(maxlen=window_size),
            "memory": deque(maxlen=window_size),
            "disk": deque(maxlen=window_size),
            "network_rate": deque(maxlen=window_size)
        }

        # For network rate calculation
        self.prev_network_bytes = None

        # Track recent dominant causes (for stability)
        self.recent_causes = deque(maxlen=persistence_window)

        # Human-readable labels
        self.label_map = {
            "cpu": "CPU",
            "memory": "MEMORY",
            "disk": "DISK",
            "network_rate": "NETWORK"
        }

        # 🔑 Metric-aware weights - CPU FOCUSED
        # CPU is the primary concern, network fluctuations are normal
        self.metric_weights = {
            "cpu": 2.5,          # CPU is PRIMARY focus - highest weight
            "memory": 1.5,       # Memory matters for stability
            "disk": 0.8,         # Disk is generally stable
            "network_rate": 0.1  # Network fluctuations are NORMAL, ignore mostly
        }

    def update(self, metrics: dict):
        """Update rolling history with latest metrics"""

        self.history["cpu"].append(metrics["cpu"]["usage_percent"])
        self.history["memory"].append(metrics["memory"]["usage_percent"])
        self.history["disk"].append(metrics["disk"]["usage_percent"])

        # Convert cumulative network bytes → rate
        current_bytes = metrics["network"]["bytes_received"]

        if self.prev_network_bytes is not None:
            rate = current_bytes - self.prev_network_bytes
            if rate >= 0:
                self.history["network_rate"].append(rate)

        self.prev_network_bytes = current_bytes

    def analyze(self, metrics: dict) -> dict:
        deviations = {}

        # Compute weighted deviation from rolling baseline
        for key, values in self.history.items():
            if len(values) < 5:
                continue

            baseline = statistics.mean(values)
            current = values[-1]

            if baseline > 0:
                raw_deviation = abs(current - baseline) / baseline
                weighted_deviation = raw_deviation * self.metric_weights[key]
                deviations[key] = weighted_deviation

        if not deviations:
            return {
                "root_cause": "INSUFFICIENT_DATA",
                "confidence": 0.0,
                "contributors": {}
            }

        # Raw dominant metric (largest weighted deviation)
        raw_root = max(deviations, key=deviations.get)
        self.recent_causes.append(raw_root)

        # Persistence-based dominant cause
        dominant = max(
            set(self.recent_causes),
            key=self.recent_causes.count
        )

        persistence_factor = self.recent_causes.count(dominant) / len(self.recent_causes)

        # Normalize confidence (0–1)
        raw_confidence = deviations[dominant]
        normalized_confidence = min(raw_confidence, 1.0)
        final_confidence = round(normalized_confidence * persistence_factor, 2)

        # Contribution breakdown (explainability)
        total_dev = sum(deviations.values())
        contributors = {
            self.label_map[k]: round(v / total_dev, 2)
            for k, v in deviations.items()
        }

        return {
            "root_cause": self.label_map[dominant],
            "confidence": final_confidence,
            "contributors": contributors
        }
