import time
import socket
import argparse
import requests
import psutil
import platform
import random
import threading
from datetime import datetime, timezone
from enum import Enum


def get_disk_path():
    """Get appropriate disk path for the OS"""
    if platform.system() == "Windows":
        return "C:\\"
    return "/"


# ==========================================
# AGENT STATE ENUMS
# ==========================================

class AgentHealthState(Enum):
    """Internal health state of the PC agent"""
    HEALTHY = "HEALTHY"
    DEGRADING = "DEGRADING"
    DEGRADED = "DEGRADED"
    RECOVERING = "RECOVERING"


class DegradationType(Enum):
    """Types of simulated degradation"""
    NONE = "NONE"
    CPU_PRESSURE = "CPU_PRESSURE"
    MEMORY_PRESSURE = "MEMORY_PRESSURE"
    NETWORK_SATURATION = "NETWORK_SATURATION"
    COMBINED = "COMBINED"


# ==========================================
# REALISTIC PC AGENT STATE CLASS
# ==========================================

class PCAgentState:
    """
    Maintains realistic internal state for a PC agent.
    This makes each agent behave like a real autonomous system node.
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        
        # Internal health tracking
        self.health_state = AgentHealthState.HEALTHY
        self.degradation_type = DegradationType.NONE
        self.degradation_level = 0.0  # 0.0 to 1.0 (severity)
        
        # Timing and persistence
        self.cycles_in_current_state = 0
        self.last_state_change = time.time()
        self.heartbeat_sequence = 0
        
        # Connection state
        self.connected = False
        self.last_successful_send = None
        self.consecutive_failures = 0
        self.reconnect_attempts = 0
        
        # Degradation simulation parameters (probabilistic)
        self.degradation_probability = 0.05  # 5% chance per cycle to start degrading
        self.recovery_probability = 0.15  # 15% chance per cycle to start recovering
        self.max_degradation_cycles = 12  # Max cycles before forced recovery
        self.min_degradation_cycles = 4   # Min cycles of degradation
        
        # Lock for thread safety
        self._lock = threading.Lock()
    
    def update_cycle(self) -> dict:
        """
        Update agent state for this cycle.
        Returns state info to be included in metrics payload.
        
        IMPORTANT: This is SIMULATION only - no OS-level changes.
        """
        with self._lock:
            self.cycles_in_current_state += 1
            self.heartbeat_sequence += 1
            
            # State machine transitions (probabilistic + time-based)
            if self.health_state == AgentHealthState.HEALTHY:
                # Small chance to start degrading
                if random.random() < self.degradation_probability:
                    self._start_degradation()
                    
            elif self.health_state == AgentHealthState.DEGRADING:
                # Gradually increase degradation
                self.degradation_level = min(1.0, self.degradation_level + random.uniform(0.1, 0.25))
                
                if self.degradation_level >= 0.6:
                    self.health_state = AgentHealthState.DEGRADED
                    self.cycles_in_current_state = 0
                    print(f"[{self.node_id}] State: DEGRADING -> DEGRADED (level: {self.degradation_level:.2f})")
                    
            elif self.health_state == AgentHealthState.DEGRADED:
                # Stay degraded for a while, then probabilistically recover
                if self.cycles_in_current_state >= self.min_degradation_cycles:
                    if (self.cycles_in_current_state >= self.max_degradation_cycles or 
                        random.random() < self.recovery_probability):
                        self._start_recovery()
                        
            elif self.health_state == AgentHealthState.RECOVERING:
                # Gradually decrease degradation
                self.degradation_level = max(0.0, self.degradation_level - random.uniform(0.15, 0.3))
                
                if self.degradation_level <= 0.1:
                    self.health_state = AgentHealthState.HEALTHY
                    self.degradation_type = DegradationType.NONE
                    self.degradation_level = 0.0
                    self.cycles_in_current_state = 0
                    print(f"[{self.node_id}] State: RECOVERING -> HEALTHY")
            
            return self._get_state_info()
    
    def _start_degradation(self):
        """Begin a degradation event"""
        # Randomly choose degradation type with weighted probabilities
        weights = [0.45, 0.35, 0.15, 0.05]  # CPU most common
        degradation_types = [
            DegradationType.CPU_PRESSURE,
            DegradationType.MEMORY_PRESSURE,
            DegradationType.NETWORK_SATURATION,
            DegradationType.COMBINED
        ]
        self.degradation_type = random.choices(degradation_types, weights=weights)[0]
        self.degradation_level = random.uniform(0.1, 0.3)  # Start mild
        self.health_state = AgentHealthState.DEGRADING
        self.cycles_in_current_state = 0
        self.last_state_change = time.time()
        
        print(f"[{self.node_id}] State: HEALTHY -> DEGRADING ({self.degradation_type.value})")
    
    def _start_recovery(self):
        """Begin recovery from degradation"""
        self.health_state = AgentHealthState.RECOVERING
        self.cycles_in_current_state = 0
        self.last_state_change = time.time()
        print(f"[{self.node_id}] State: DEGRADED -> RECOVERING")
    
    def _get_state_info(self) -> dict:
        """Get current state information for payload"""
        return {
            "health_state": self.health_state.value,
            "degradation_type": self.degradation_type.value,
            "degradation_level": round(self.degradation_level, 3),
            "cycles_in_state": self.cycles_in_current_state,
            "heartbeat_seq": self.heartbeat_sequence,
            "connected": self.connected
        }
    
    def apply_degradation_to_metrics(self, metrics: dict) -> dict:
        """
        Apply simulated degradation to metrics.
        This is SIMULATION ONLY - does NOT affect real system.
        """
        if self.degradation_level == 0 or self.degradation_type == DegradationType.NONE:
            return metrics
        
        # Scale factor based on degradation level
        scale = self.degradation_level
        
        if self.degradation_type == DegradationType.CPU_PRESSURE:
            # Simulate CPU pressure (gradual increase)
            base_cpu = metrics["cpu"]["usage_percent"]
            added = scale * random.uniform(30, 60)
            metrics["cpu"]["usage_percent"] = min(99, base_cpu + added)
            
        elif self.degradation_type == DegradationType.MEMORY_PRESSURE:
            # Simulate memory pressure
            base_mem = metrics["memory"]["usage_percent"]
            added = scale * random.uniform(25, 50)
            metrics["memory"]["usage_percent"] = min(98, base_mem + added)
            # Memory pressure also affects CPU slightly
            metrics["cpu"]["usage_percent"] = min(95, metrics["cpu"]["usage_percent"] + scale * 10)
            
        elif self.degradation_type == DegradationType.NETWORK_SATURATION:
            # Simulate network saturation (high IO)
            metrics["network"]["bytes_sent"] = int(metrics["network"]["bytes_sent"] * (1 + scale * 5))
            metrics["network"]["bytes_received"] = int(metrics["network"]["bytes_received"] * (1 + scale * 5))
            # Network saturation causes some CPU overhead
            metrics["cpu"]["usage_percent"] = min(90, metrics["cpu"]["usage_percent"] + scale * 15)
            
        elif self.degradation_type == DegradationType.COMBINED:
            # Combined pressure - most severe
            base_cpu = metrics["cpu"]["usage_percent"]
            base_mem = metrics["memory"]["usage_percent"]
            metrics["cpu"]["usage_percent"] = min(99, base_cpu + scale * random.uniform(35, 55))
            metrics["memory"]["usage_percent"] = min(98, base_mem + scale * random.uniform(20, 40))
        
        return metrics
    
    def record_send_success(self):
        """Record successful metric send"""
        with self._lock:
            self.connected = True
            self.last_successful_send = time.time()
            self.consecutive_failures = 0
            self.reconnect_attempts = 0
    
    def record_send_failure(self):
        """Record failed metric send"""
        with self._lock:
            self.consecutive_failures += 1
            if self.consecutive_failures >= 3:
                self.connected = False


# Global agent state (created per agent instance)
agent_state = None


# ==========================================
# LEGACY STRESS SIMULATION (kept for backward compatibility)
# ==========================================

# Stress event state
stress_event = {
    "active": False,
    "type": None,
    "severity": "NORMAL",
    "remaining_cycles": 0
}

cycle_counter = 0
STRESS_EVERY_N_CYCLES = 3
SEVERITY_ROTATION = ["WARNING", "CRITICAL", "CRITICAL", "WARNING"]
severity_index = 0


def maybe_trigger_stress():
    """Legacy stress trigger - kept for --demo-stress flag compatibility"""
    global stress_event, cycle_counter, severity_index
    
    cycle_counter += 1
    
    if stress_event["active"]:
        stress_event["remaining_cycles"] -= 1
        if stress_event["remaining_cycles"] <= 0:
            print(f"[STRESS] Event ended: {stress_event['type']} ({stress_event['severity']})")
            stress_event["active"] = False
            stress_event["type"] = None
            stress_event["severity"] = "NORMAL"
        return stress_event
    
    if cycle_counter >= STRESS_EVERY_N_CYCLES:
        cycle_counter = 0
        severity_index = (severity_index + 1) % len(SEVERITY_ROTATION)
        target_severity = SEVERITY_ROTATION[severity_index]
        stress_types = ["CPU_SPIKE", "CPU_SPIKE", "MEMORY_PRESSURE"]
        stress_event["active"] = True
        stress_event["type"] = random.choice(stress_types)
        stress_event["severity"] = target_severity
        stress_event["remaining_cycles"] = 2
        print(f"[STRESS] Triggered: {stress_event['type']} -> {target_severity} for 2 cycles")
    
    return stress_event


def apply_stress_modifier(metrics, event):
    """Legacy stress modifier - kept for backward compatibility"""
    if not event["active"]:
        return metrics, False, "NORMAL"
    
    stress_type = event["type"]
    target_severity = event["severity"]
    real_cpu = metrics["cpu"]["usage_percent"]
    real_memory = metrics["memory"]["usage_percent"]
    
    if target_severity == "CRITICAL":
        if stress_type == "CPU_SPIKE":
            metrics["cpu"]["usage_percent"] = min(99, real_cpu + random.uniform(50, 70))
        elif stress_type == "MEMORY_PRESSURE":
            metrics["memory"]["usage_percent"] = min(98, real_memory + random.uniform(35, 50))
            metrics["cpu"]["usage_percent"] = min(90, real_cpu + random.uniform(15, 25))
    elif target_severity == "WARNING":
        if stress_type == "CPU_SPIKE":
            metrics["cpu"]["usage_percent"] = min(85, real_cpu + random.uniform(25, 40))
        elif stress_type == "MEMORY_PRESSURE":
            metrics["memory"]["usage_percent"] = min(85, real_memory + random.uniform(20, 35))
    
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


def run_agent(node_id, backend_url, interval, enable_stress=False, enable_realistic=True):
    """
    Run the PC agent with realistic behavior simulation.
    
    Args:
        node_id: Unique identifier for this agent
        backend_url: Backend server URL
        interval: Metric collection interval in seconds
        enable_stress: Enable legacy stress simulation (--demo-stress)
        enable_realistic: Enable realistic probabilistic degradation (default: True)
    """
    global agent_state
    
    hostname = socket.gethostname()
    agent_state = PCAgentState(node_id)
    
    print(f"=" * 60)
    print(f"[AGENT STARTED] Node: {node_id}")
    print(f"[AGENT] Hostname: {hostname}")
    print(f"[AGENT] Backend: {backend_url}")
    print(f"[AGENT] Interval: {interval}s")
    print(f"[AGENT] Realistic Mode: {enable_realistic}")
    print(f"[AGENT] Legacy Stress: {enable_stress}")
    print(f"=" * 60)
    
    if enable_realistic:
        print(f"[AGENT] Probabilistic degradation enabled:")
        print(f"        - {agent_state.degradation_probability*100:.0f}% chance to degrade per cycle")
        print(f"        - {agent_state.recovery_probability*100:.0f}% chance to recover per cycle")
        print(f"        - Types: CPU_PRESSURE, MEMORY_PRESSURE, NETWORK_SATURATION, COMBINED")
    
    if enable_stress:
        print(f"[AGENT] Legacy demo mode: Health drop every ~15 seconds")

    reconnect_delay = 1  # Start with 1 second reconnect delay
    max_reconnect_delay = 30  # Max 30 seconds between reconnect attempts
    
    while True:
        try:
            # Collect REAL metrics
            metrics = collect_metrics()
            
            # Update agent state (probabilistic state machine)
            if enable_realistic:
                state_info = agent_state.update_cycle()
                metrics = agent_state.apply_degradation_to_metrics(metrics)
            else:
                state_info = {
                    "health_state": "HEALTHY",
                    "degradation_type": "NONE",
                    "degradation_level": 0.0,
                    "cycles_in_state": 0,
                    "heartbeat_seq": 0,
                    "connected": True
                }
            
            # Legacy stress simulation (if enabled)
            simulated_event = False
            target_severity = "NORMAL"
            if enable_stress:
                event = maybe_trigger_stress()
                metrics, simulated_event, target_severity = apply_stress_modifier(metrics, event)
            
            # Build comprehensive payload with heartbeat + metrics
            payload = {
                "node_id": node_id,
                "hostname": hostname,
                "metrics": metrics,
                # Agent state information
                "agent_state": state_info,
                "heartbeat": {
                    "sequence": state_info["heartbeat_seq"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "uptime_seconds": time.time() - agent_state.last_state_change if agent_state else 0
                },
                # Legacy fields for backward compatibility
                "simulated_event": simulated_event or (state_info["degradation_level"] > 0),
                "target_severity": target_severity if enable_stress else (
                    "CRITICAL" if state_info["degradation_level"] > 0.7 else
                    "WARNING" if state_info["degradation_level"] > 0.3 else "NORMAL"
                )
            }

            response = requests.post(
                f"{backend_url}/agent/metrics",
                json=payload,
                timeout=5
            )

            if response.status_code == 200:
                agent_state.record_send_success()
                reconnect_delay = 1  # Reset reconnect delay on success
                
                # Log state changes
                if state_info["degradation_level"] > 0:
                    print(f"[{node_id}] Sent metrics - State: {state_info['health_state']}, "
                          f"Type: {state_info['degradation_type']}, "
                          f"Level: {state_info['degradation_level']:.2f}")
            else:
                agent_state.record_send_failure()
                print(f"[{node_id}] WARN: Backend responded with {response.status_code}")

        except requests.exceptions.ConnectionError:
            agent_state.record_send_failure()
            print(f"[{node_id}] ERROR: Cannot connect to backend (attempt {agent_state.consecutive_failures})")
            print(f"[{node_id}] Retrying in {reconnect_delay}s...")
            time.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)  # Exponential backoff
            continue
            
        except requests.exceptions.Timeout:
            agent_state.record_send_failure()
            print(f"[{node_id}] ERROR: Request timeout")
            
        except Exception as e:
            agent_state.record_send_failure()
            print(f"[{node_id}] ERROR: Failed to send metrics: {e}")

        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIOps PC Monitoring Agent - Realistic Autonomous Node")

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
        help="Enable legacy periodic stress simulation (every ~15 seconds)"
    )
    
    parser.add_argument(
        "--no-realistic",
        action="store_true",
        help="Disable realistic probabilistic degradation (use only for testing)"
    )
    
    parser.add_argument(
        "--degradation-chance",
        type=float,
        default=0.05,
        help="Probability of degradation per cycle (0.0-1.0, default: 0.05)"
    )
    
    parser.add_argument(
        "--recovery-chance",
        type=float,
        default=0.15,
        help="Probability of recovery per cycle (0.0-1.0, default: 0.15)"
    )

    args = parser.parse_args()
    
    # Configure degradation probabilities if custom values provided
    enable_realistic = not args.no_realistic
    
    run_agent(
        node_id=args.node_id,
        backend_url=args.backend_url,
        interval=args.interval,
        enable_stress=args.demo_stress,
        enable_realistic=enable_realistic
    )
