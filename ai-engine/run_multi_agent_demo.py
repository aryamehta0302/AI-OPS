#!/usr/bin/env python3
"""
MULTI-AGENT DEMO LAUNCHER
==========================
Launches multiple PC agents simultaneously to demonstrate:
- Multi-agent agentic AI behavior
- Independent degradation per node
- Auto-healing and escalation across nodes
- Real-time UI updates showing different node states

USAGE:
    python run_multi_agent_demo.py [--agents N] [--backend-url URL]

EXAMPLES:
    python run_multi_agent_demo.py                    # Run 3 agents (default)
    python run_multi_agent_demo.py --agents 5         # Run 5 agents
    python run_multi_agent_demo.py --agents 2 --no-stress  # 2 agents, realistic only

This script is SIMULATION ONLY - no OS-level changes are made.
"""

import subprocess
import sys
import time
import argparse
import signal
import os
from typing import List


def get_python_executable():
    """Get the Python executable path"""
    return sys.executable


def launch_agent(node_id: str, backend_url: str, interval: int, demo_stress: bool, no_realistic: bool) -> subprocess.Popen:
    """
    Launch a single PC agent as a subprocess
    
    Args:
        node_id: Unique identifier for the agent
        backend_url: Backend server URL
        interval: Metric collection interval
        demo_stress: Enable legacy stress simulation
        no_realistic: Disable realistic probabilistic degradation
        
    Returns:
        Popen process handle
    """
    python_exe = get_python_executable()
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent.py")
    
    cmd = [
        python_exe,
        script_path,
        "--node-id", node_id,
        "--backend-url", backend_url,
        "--interval", str(interval)
    ]
    
    if demo_stress:
        cmd.append("--demo-stress")
    
    if no_realistic:
        cmd.append("--no-realistic")
    
    print(f"[LAUNCHER] Starting agent: {node_id}")
    print(f"[LAUNCHER] Command: {' '.join(cmd)}")
    
    # Launch with output visible
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    return process


def output_reader(process: subprocess.Popen, node_id: str):
    """Read and print output from a process with node_id prefix"""
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                # Don't double-prefix if already has node_id
                if node_id in line:
                    print(line.rstrip())
                else:
                    print(f"[{node_id}] {line.rstrip()}")
    except Exception as e:
        print(f"[{node_id}] Output reader error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Demo Launcher for AIOps Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
DEMONSTRATION SCENARIOS:
========================
1. BASIC MULTI-AGENT: Run 3 agents, watch one degrade while others stay healthy
   python run_multi_agent_demo.py --agents 3

2. STRESS TEST: Run 5 agents with legacy stress (guaranteed degradation)
   python run_multi_agent_demo.py --agents 5 --demo-stress

3. REALISTIC ONLY: Run 3 agents with only probabilistic degradation
   python run_multi_agent_demo.py --agents 3

4. NO DEGRADATION: Run 2 agents without any simulated degradation
   python run_multi_agent_demo.py --agents 2 --no-realistic

WHAT TO OBSERVE:
================
- Open the frontend at http://localhost:5173
- Watch the Node Grid to see different states per PC
- Observe Agent Decisions changing based on health
- See auto-healing triggers when nodes become critical
- Notice incidents recorded on state transitions
"""
    )
    
    parser.add_argument(
        "--agents",
        type=int,
        default=3,
        help="Number of PC agents to run (default: 3)"
    )
    
    parser.add_argument(
        "--backend-url",
        default="http://localhost:5000",
        help="Backend server URL (default: http://localhost:5000)"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Metric collection interval in seconds (default: 5)"
    )
    
    parser.add_argument(
        "--demo-stress",
        action="store_true",
        help="Enable legacy stress simulation (guaranteed degradation every ~15s)"
    )
    
    parser.add_argument(
        "--no-realistic",
        action="store_true",
        help="Disable probabilistic degradation (send only real metrics)"
    )
    
    parser.add_argument(
        "--prefix",
        default="PC",
        help="Node ID prefix (default: PC, resulting in PC-1, PC-2, etc.)"
    )
    
    args = parser.parse_args()
    
    # Store processes for cleanup
    processes: List[subprocess.Popen] = []
    
    # Signal handler for graceful shutdown
    def signal_handler(signum, frame):
        print("\n[LAUNCHER] Shutting down all agents...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait()
        print("[LAUNCHER] All agents stopped.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("MULTI-AGENT AIOPS DEMO LAUNCHER")
    print("=" * 60)
    print(f"Agents to launch: {args.agents}")
    print(f"Backend URL: {args.backend_url}")
    print(f"Interval: {args.interval}s")
    print(f"Legacy stress: {args.demo_stress}")
    print(f"Realistic degradation: {not args.no_realistic}")
    print("=" * 60)
    print()
    
    # Launch agents with staggered start
    for i in range(1, args.agents + 1):
        node_id = f"{args.prefix}-{i}"
        process = launch_agent(
            node_id=node_id,
            backend_url=args.backend_url,
            interval=args.interval,
            demo_stress=args.demo_stress,
            no_realistic=args.no_realistic
        )
        processes.append(process)
        
        # Stagger agent starts to avoid all starting at exactly the same time
        time.sleep(1)
    
    print()
    print("=" * 60)
    print(f"[LAUNCHER] {args.agents} agents running")
    print("[LAUNCHER] Press Ctrl+C to stop all agents")
    print("=" * 60)
    print()
    print("OBSERVE THE DEMO:")
    print("-----------------")
    print("1. Open http://localhost:5173 in your browser")
    print("2. Watch the Node Grid for different node states")
    print("3. Click individual nodes to see their agent decisions")
    print("4. Observe incidents in the timeline")
    print("5. Watch auto-healing triggers on critical nodes")
    print()
    
    # Monitor agents and forward their output
    import threading
    threads = []
    for i, process in enumerate(processes):
        node_id = f"{args.prefix}-{i+1}"
        t = threading.Thread(target=output_reader, args=(process, node_id), daemon=True)
        t.start()
        threads.append(t)
    
    # Wait for all processes (they run indefinitely until killed)
    try:
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)


if __name__ == "__main__":
    main()
