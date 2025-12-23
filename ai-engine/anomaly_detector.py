from river import anomaly, preprocessing

class StreamingAnomalyDetector:
    """
    Online anomaly detector using River's Half-Space Trees
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
        Takes one metrics record and returns anomaly score
        """

        features = {
            "cpu": metrics["cpu"]["usage_percent"],
            "memory": metrics["memory"]["usage_percent"],
            "disk": metrics["disk"]["usage_percent"],
            "net_sent": metrics["network"]["bytes_sent"],
            "net_recv": metrics["network"]["bytes_received"],
        }

        score = self.model.score_one(features)
        self.model.learn_one(features)

        return round(score, 4)
