from river import anomaly, preprocessing

class StreamingAnomalyDetector:
    """
    Online anomaly detector using River's Half-Space Trees
    OPTIMIZED: Focus on CPU issues, network fluctuations are normal
    """

    def __init__(self):
        self.model = preprocessing.StandardScaler() | anomaly.HalfSpaceTrees(
            n_trees=25,
            height=10,
            window_size=250,
            seed=42
        )

    def process(self, metrics: dict) -> float:
        """
        Takes one metrics record and returns anomaly score.
        CPU is weighted heavily, network is minimized (fluctuations are normal).
        """

        # FOCUSED: CPU gets high weight, network gets minimal weight
        features = {
            "cpu": metrics["cpu"]["usage_percent"] * 2.0,        # CPU is PRIMARY focus
            "memory": metrics["memory"]["usage_percent"] * 1.2,  # Memory matters
            "disk": metrics["disk"]["usage_percent"] * 0.8,      # Disk is stable
            # Network excluded - fluctuations are normal and don't indicate problems
        }

        score = self.model.score_one(features)
        self.model.learn_one(features)

        return round(score, 4)
