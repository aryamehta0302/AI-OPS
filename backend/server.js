require("dotenv").config();
const express = require("express");
const http = require("http");
const cors = require("cors");
const { Server } = require("socket.io");
const setupSocket = require("./socket");

const app = express();
app.use(cors());

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*"
  }
});

setupSocket(io);

app.get("/health", (req, res) => {
  res.json({ status: "Backend running" });
});

const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`Backend listening on port ${PORT}`);
});
