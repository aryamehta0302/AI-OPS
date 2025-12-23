import psutil
import time
import json
from datetime import datetime, timezone



def collect_system_metrics():
    """
    Collects real-time system health metrics.
    Returns a dictionary (JSON serializable).
    """

    cpu_percent = psutil.cpu_percent(interval=1)

    virtual_memory = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()

    metrics = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cpu": {
            "usage_percent": cpu_percent
        },
        "memory": {
            "total_mb": round(virtual_memory.total / (1024 * 1024), 2),
            "used_mb": round(virtual_memory.used / (1024 * 1024), 2),
            "usage_percent": virtual_memory.percent
        },
        "disk": {
            "total_gb": round(disk_usage.total / (1024 * 1024 * 1024), 2),
            "used_gb": round(disk_usage.used / (1024 * 1024 * 1024), 2),
            "usage_percent": disk_usage.percent
        },
        "network": {
            "bytes_sent": net_io.bytes_sent,
            "bytes_received": net_io.bytes_recv
        }
    }

    return metrics


if __name__ == "__main__":
    print("Starting system metrics collection...\n")

    while True:
        data = collect_system_metrics()
        print(json.dumps(data, indent=2))
        time.sleep(2)
