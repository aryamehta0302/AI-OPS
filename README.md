# Multi-Agent Agentic AIOps Platform

Real-time **agentic AI operations monitoring** with autonomous decision-making, anomaly detection, and self-healing.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────────┐
│   Frontend      │────▶│    Backend      │────▶│   AI Engine          │
│   (React)       │◀────│   (Node.js)     │◀────│   (FastAPI)          │
│                 │     │                 │     │                      │
│  - Dashboard    │     │  - Socket.IO    │     │  - DecisionAgent ⭐  │
│  - Agent UI     │     │  - Incidents    │     │  - Anomaly Detection │
└─────────────────┘     └─────────────────┘     │  - Root Cause        │
     :5173                   :5000               │  - Auto-Healing      │
                                                 └──────────────────────┘
                                                          :8001
```

## Project Structure

| Folder | Description |
|--------|-------------|
| [ai-engine/](ai-engine/README.md) | Python FastAPI server with DecisionAgent, anomaly detection, auto-healing |
| [backend/](backend/README.md) | Node.js/Express server, Socket.IO, multi-node management |
| [frontend/](frontend/README.md) | React dashboard with real-time metrics and agent decision visualization |

## Quick Start

### 1. Start AI Engine
```bash
cd ai-engine
python -m venv myenv && myenv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8001
```

### 2. Start Backend
```bash
cd backend
npm install && npm run dev
```

### 3. Start Frontend
```bash
cd frontend
npm install && npm run dev
```

### 4. Run a PC Agent
```bash
cd ai-engine
python agent.py --node-id PC-1
```

**Dashboard:** http://localhost:5173

## What Makes This "Agentic AI"?

The **DecisionAgent** is an autonomous agent that:

- ✅ **Perceives** - Ingests real-time metrics
- ✅ **Remembers** - Maintains sliding window memory per node
- ✅ **Reasons** - Analyzes trends, persistence, patterns
- ✅ **Decides** - Makes autonomous decisions (ESCALATE, AUTO_HEAL, etc.)
- ✅ **Acts** - Triggers safe healing actions
- ✅ **Explains** - Provides full reasoning chains

**The agent operates independently. No prompts. No human intervention.**

## Tech Stack

- **Frontend:** React 19, Recharts, Socket.IO Client, Vite
- **Backend:** Node.js, Express, Socket.IO
- **AI Engine:** FastAPI, River ML, scikit-learn, psutil

## License

MIT
