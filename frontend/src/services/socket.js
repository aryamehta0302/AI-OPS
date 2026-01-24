import { io } from "socket.io-client";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

const socket = io(BACKEND_URL, {
  reconnection: true,
  reconnectionAttempts: 10,
  reconnectionDelay: 1000,
});

socket.on("connect", () => {
  console.log("Connected to backend");
});

socket.on("disconnect", () => {
  console.log("Disconnected from backend");
});

socket.on("connect_error", (err) => {
  console.error("Connection error:", err.message);
});

export default socket;
