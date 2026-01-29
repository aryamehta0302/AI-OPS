# Frontend

React dashboard for real-time AIOps monitoring and agent decision visualization.

## What's in This Folder

| File/Folder | Purpose |
|-------------|---------|
| `src/App.jsx` | Main application component |
| `src/components/` | UI components |
| `src/services/socket.js` | Socket.IO client for real-time updates |
| `vite.config.js` | Vite build configuration |
| `index.html` | Entry HTML file |

## Key Components

| Component | Purpose |
|-----------|---------|
| `AgentDecisionPanel.jsx` | Displays autonomous agent decisions and reasoning |
| `MetricsChart.jsx` | Real-time CPU, Memory, Disk, Network charts |
| `HealthCard.jsx` | System health score and risk level |
| `RootCauseCard.jsx` | AI-identified root cause of issues |
| `HealingStatus.jsx` | Auto-healing action status |
| `NodeGrid.jsx` | Multi-node overview grid |
| `NodeSelector.jsx` | Switch between monitored nodes |
| `IncidentTimeline.jsx` | System state change history |
| `AlertBanner.jsx` | Critical alert notifications |
| `ConnectionIndicator.jsx` | Backend connection status |
| `PredictionCard.jsx` | Future risk predictions |

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Environment Variables

Create a `.env` file:

```env
VITE_BACKEND_URL=http://localhost:5000
```

## Tech Stack

- **React 19** - UI framework
- **Vite** - Build tool with HMR
- **Recharts** - Charting library
- **Socket.IO Client** - Real-time WebSocket communication
- **CSS** - Custom dark theme styling

## Dashboard Features

- **Real-time Metrics** - Live CPU, Memory, Disk, Network visualization
- **Agent Decisions** - See autonomous AI decisions with full reasoning chains
- **Multi-Node Support** - Monitor multiple PCs from one dashboard
- **Health Scoring** - Visual health indicators (NORMAL, WARNING, CRITICAL)
- **Root Cause Analysis** - AI-identified sources of issues
- **Auto-Healing Status** - Track automated remediation actions
