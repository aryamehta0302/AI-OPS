# AI Engine

FastAPI-based autonomous AI engine for real-time system monitoring and decision-making.

## What's in This Folder

| File | Purpose |
|------|---------|
| `app.py` | Main FastAPI server - exposes `/metrics`, `/agent/metrics`, `/agent/decisions` endpoints |
| `decision_agent.py` | **DecisionAgent** - Autonomous reasoning engine that perceives, remembers, reasons, decides |
| `anomaly_detector.py` | Streaming ML anomaly detection using River's Half-Space Trees |
| `root_cause_analyzer.py` | AI-powered root cause attribution with confidence scores |
| `health_evaluator.py` | Health scoring and risk level calculation |
| `auto_healer.py` | Safe, non-destructive auto-healing actions |
| `explanation_engine.py` | GenAI explanation layer (LLM explains decisions, never decides) |
| `metrics_collector.py` | System metrics collection using psutil |
| `agent.py` | PC Agent - Runs on monitored nodes, sends metrics to backend |
| `run_multi_agent_demo.py` | Demo script to simulate multiple PC agents |
| `test_decision_agent.py` | Test suite for the DecisionAgent |
| `requirements.txt` | Python dependencies |

## Quick Start

```bash
# Create virtual environment
python -m venv myenv
myenv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the AI Engine
uvicorn app:app --reload --port 8001
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/metrics` | GET | Get local system metrics with AI analysis |
| `/agent/metrics` | POST | Process metrics from remote agents |
| `/agent/decisions` | GET | Get recent agent decision history |
| `/agent/memory/{node_id}` | GET | Get agent memory state for a node |

## DecisionAgent Architecture

```
PERCEIVE → REMEMBER → REASON → DECIDE → EXPLAIN
    ↓          ↓          ↓        ↓         ↓
 Metrics   Memory    Trends   Action   Reasoning
           (20-pt    Analysis  (AUTO_   Chain
           window)            HEAL,
                              ESCALATE,
                              etc.)
```

**Decisions:** `NO_ACTION`, `ESCALATE`, `DE_ESCALATE`, `PREDICT_FAILURE`, `AUTO_HEAL`

## Running a PC Agent

```bash
# Run agent for a specific node
python agent.py --node-id PC-1 --backend-url http://localhost:5000

# Run multi-agent demo (simulates 3 nodes)
python run_multi_agent_demo.py
```
