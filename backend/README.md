# Backend

Node.js/Express server that bridges the Frontend and AI Engine via WebSockets.

## What's in This Folder

| File | Purpose |
|------|---------|
| `server.js` | Express server setup, HTTP endpoints, static file serving |
| `socket.js` | Socket.IO real-time communication with frontend |
| `services/aiEngineClient.js` | HTTP client to communicate with AI Engine |
| `services/nodeManager.js` | Multi-node state management, agent registration, metrics routing |
| `services/incidentManager.js` | Incident timeline tracking and state transitions |

## Quick Start

```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Run in production
npm start
```

## Environment Variables

Create a `.env` file:

```env
PORT=5000
AI_ENGINE_URL=http://127.0.0.1:8001
POLL_INTERVAL_MS=2000
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Backend health check |
| `/incidents` | GET | Get incident timeline |
| `/agent/register` | POST | Register a new PC agent |
| `/agent/metrics` | POST | Receive metrics from PC agents |

## WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `system_metrics` | Server → Client | Real-time metrics update (includes agent decisions) |
| `incident_event` | Server → Client | System state change alert |
| `node_connected` | Server → Client | New node came online |
| `node_disconnected` | Server → Client | Node went offline |

## Architecture

```
PC Agents → Backend → AI Engine
               ↓
           Frontend (via WebSocket)
```

The backend:
1. Receives metrics from PC agents (`/agent/metrics`)
2. Forwards to AI Engine for analysis
3. Broadcasts enriched data to frontend via Socket.IO
