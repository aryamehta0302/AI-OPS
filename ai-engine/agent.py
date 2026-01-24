import time
import socket
import argparse
import requests
import psutil
import platform
import random
from datetime import datetime, timezone


def get_disk_path():
    """Get appropriate disk path for the OS"""
    if platform.system() == "Windows":
        return "C:\\"
    return "/"


# ==========================================
# DEMO STRESS SIMULATION
# OPTIMIZED: Guaranteed health drop every ~15 seconds for incidents
# Cycles between NORMAL -> WARNING -> CRITICAL -> NORMAL
# ==========================================

# Stress event state
stress_event = {
    "active": False,
    "type": None,
    "severity": "NORMAL",  # Track severity for incident transitions
    "remaining_cycles": 0
}

# Cycle counter for guaranteed stress every 15 seconds (3 cycles at 5s interval)
cycle_counter = 0
STRESS_EVERY_N_CYCLES = 3  # 3 cycles * 5 seconds = 15 seconds

# Severity rotation for clear incident recording
SEVERITY_ROTATION = ["WARNING", "CRITICAL", "CRITICAL", "WARNING"]
severity_index = 0


def maybe_trigger_stress():
    """
    OPTIMIZED: Trigger health drop every ~15 seconds.
    Rotates between severities to create clear incident transitions.
    """
    global stress_event, cycle_counter, severity_index
    
    cycle_counter += 1
    
    # If stress is already active, decrement counter
    if stress_event["active"]:
        stress_event["remaining_cycles"] -= 1
        if stress_event["remaining_cycles"] <= 0:
            print(f"[STRESS] Event ended: {stress_event['type']} ({stress_event['severity']})")
            stress_event["active"] = False
            stress_event["type"] = None
            stress_event["severity"] = "NORMAL"
        return stress_event
    
    # Trigger stress every 3 cycles (~15 seconds)
    if cycle_counter >= STRESS_EVERY_N_CYCLES:
        cycle_counter = 0
        
        # Rotate through severities for varied incidents
        severity_index = (severity_index + 1) % len(SEVERITY_ROTATION)
        target_severity = SEVERITY_ROTATION[severity_index]
        
        # FOCUSED: CPU-centric stress types (network fluctuations are normal)
        stress_types = ["CPU_SPIKE", "CPU_SPIKE", "MEMORY_PRESSURE"]  # 66% CPU focus
        stress_event["active"] = True
        stress_event["type"] = random.choice(stress_types)
        stress_event["severity"] = target_severity
        stress_event["remaining_cycles"] = 2  # 10 seconds duration
        
        print(f"[STRESS] Triggered: {stress_event['type']} -> {target_severity} for 2 cycles")
    
    return stress_event


def apply_stress_modifier(metrics, event):
    """
    Apply stress modifiers ON TOP OF real metrics.
    FOCUSED: CPU is the primary concern - most stress affects CPU.
    Network fluctuations are normal and ignored.
    """
    if not event["active"]:
        return metrics, False, "NORMAL"
    
    stress_type = event["type"]
    target_severity = event["severity"]
    
    # Get REAL values as base
    real_cpu = metrics["cpu"]["usage_percent"]
    real_memory = metrics["memory"]["usage_percent"]
    
    # ADD stress on top of real metrics - CPU FOCUSED
    if target_severity == "CRITICAL":
        if stress_type == "CPU_SPIKE":
            # Primary focus: CPU spike (simulates runaway process)
            metrics["cpu"]["usage_percent"] = min(99, real_cpu + random.uniform(50, 70))
            print(f"[METRICS] CPU CRITICAL: {real_cpu:.1f}% -> {metrics['cpu']['usage_percent']:.1f}%")
        elif stress_type == "MEMORY_PRESSURE":
            # Memory pressure also affects CPU slightly
            metrics["memory"]["usage_percent"] = min(98, real_memory + random.uniform(35, 50))
            metrics["cpu"]["usage_percent"] = min(90, real_cpu + random.uniform(15, 25))
            print(f"[METRICS] Memory CRITICAL: {real_memory:.1f}% -> {metrics['memory']['usage_percent']:.1f}%")
            
    elif target_severity == "WARNING":
        if stress_type == "CPU_SPIKE":
            # Moderate CPU increase
            metrics["cpu"]["usage_percent"] = min(85, real_cpu + random.uniform(25, 40))
            print(f"[METRICS] CPU WARNING: {real_cpu:.1f}% -> {metrics['cpu']['usage_percent']:.1f}%")
        elif stress_type == "MEMORY_PRESSURE":
            metrics["memory"]["usage_percent"] = min(85, real_memory + random.uniform(20, 35))
            print(f"[METRICS] Memory WARNING: {real_memory:.1f}% -> {metrics['memory']['usage_percent']:.1f}%")
    
    return metrics, True, target_severity


def collect_metrics():
    """Collect REAL system metrics using psutil"""
    disk_path = get_disk_path()
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cpu": {
            "usage_percent": psutil.cpu_percent(interval=1)
        },
        "memory": {
            "total_mb": round(psutil.virtual_memory().total / (1024 ** 2), 2),
            "used_mb": round(psutil.virtual_memory().used / (1024 ** 2), 2),
            "usage_percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total_gb": round(psutil.disk_usage(disk_path).total / (1024 ** 3), 2),
            "used_gb": round(psutil.disk_usage(disk_path).used / (1024 ** 3), 2),
            "usage_percent": psutil.disk_usage(disk_path).percent
        },
        "network": {
            "bytes_sent": psutil.net_io_counters().bytes_sent,
            "bytes_received": psutil.net_io_counters().bytes_recv
        }
    }


def run_agent(node_id, backend_url, interval, enable_stress=False):
    hostname = socket.gethostname()
    print(f"[AGENT STARTED] Node: {node_id} | Hostname: {hostname}")
    if enable_stress:
        print(f"[AGENT] Demo mode: Health drop every ~15 seconds (WARNING/CRITICAL rotation)")
        print(f"[AGENT] Incidents will be recorded on each state transition")

    while True:
        try:
            # Collect REAL metrics
            metrics = collect_metrics()
            
            # Check for stress events (demo mode only)
            simulated_event = False
            target_severity = "NORMAL"
            if enable_stress:
                event = maybe_trigger_stress()
                metrics, simulated_event, target_severity = apply_stress_modifier(metrics, event)
            
            payload = {
                "node_id": node_id,
                "hostname": hostname,
                "metrics": metrics,
                "simulated_event": simulated_event,  # Flag for transparency
                "target_severity": target_severity   # Hint for debugging
            }

            response = requests.post(
                f"{backend_url}/agent/metrics",
                json=payload,
                timeout=3
            )

            if response.status_code != 200:
                print(f"[WARN] Backend responded with {response.status_code}")

        except Exception as e:
            print(f"[ERROR] Failed to send metrics: {e}")

        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIOps PC Monitoring Agent")

    parser.add_argument(
        "--node-id",
        required=True,
        help="Unique identifier for this PC (e.g., PC-1, PC-2)"
    )

    parser.add_argument(
        "--backend-url",
        default="http://localhost:5000",
        help="Backend server URL"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Metric collection interval (seconds)"
    )

    parser.add_argument(
        "--demo-stress",
        action="store_true",
        help="Enable occasional stress simulation for demo (2%% chance per cycle)"
    )

    args = parser.parse_args()

    run_agent(
        node_id=args.node_id,
        backend_url=args.backend_url,
        interval=args.interval,
        enable_stress=args.demo_stress
    )
