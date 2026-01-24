# AIOps System Health Platform

A real-time AI-powered operations monitoring platform with anomaly detection, health scoring, and root-cause analysis.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│    Backend      │────▶│   AI Engine     │
│   (React)       │◀────│   (Node.js)     │◀────│   (FastAPI)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
     :3000              Socket.IO :5000          REST API :8001
```

## Features

- **Real-time System Monitoring** - CPU, Memory, Disk, Network metrics
- **ML-based Anomaly Detection** - Using River's Half-Space Trees (streaming ML)
- **Health Scoring** - Automatic health calculation with risk levels
- **Root Cause Analysis** - AI-powered attribution with confidence scores
- **Incident Timeline** - Track system state transitions
- **Beautiful Dashboard** - Modern dark theme with real-time charts

## Quick Start

### 1. Start the AI Engine (Python)

```bash
cd ai-engine

# Create virtual environment (first time only)
python -m venv myenv
myenv\Scripts\activate  # Windows
# source myenv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the AI engine
uvicorn app:app --reload --port 8001
```

### 2. Start the Backend (Node.js)

```bash
cd backend

# Install dependencies
npm install

# Run the backend
npm run dev
```

### 3. Start the Frontend (React)

```bash
cd frontend

# Install dependencies
npm install

# Run the frontend
npm run dev
```

### 4. Open the Dashboard

Visit `http://localhost:5173` in your browser.

## Environment Variables

### Backend (.env)
```
PORT=5000
AI_ENGINE_URL=http://127.0.0.1:8001
POLL_INTERVAL_MS=2000
```

### Frontend (.env)
```
VITE_BACKEND_URL=http://localhost:5000
```

## API Endpoints

### AI Engine (Port 8001)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/metrics` | GET | Get system metrics with AI analysis |

### Backend (Port 5000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Backend health check |
| `/incidents` | GET | Get incident timeline |

### WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `system_metrics` | Server → Client | Real-time metrics update |
| `incident_event` | Server → Client | System state change alert |

## Tech Stack

- **Frontend**: React 19, Recharts, Socket.IO Client, Vite
- **Backend**: Node.js, Express, Socket.IO
- **AI Engine**: FastAPI, River ML, scikit-learn, psutil

## License

MIT
