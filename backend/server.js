import express from 'express';
import http from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import { setupDatabase } from './database.js';
import { scenarios, getDefaultScenario } from './attackScenarios.js';

const app = express();
app.use(cors());
const server = http.createServer(app);

// Set up Socket.io for real-time updates
const io = new Server(server, {
  cors: {
    origin: "http://localhost:5173", // Allow your React app
    methods: ["GET", "POST"]
  }
});

const PORT = 3001; // Our backend will run on this port
let db;
let isAttackRunning = false;
let attackTimeout = null; // Store the timeout ID

// --- Attack Simulation Logic (Moved from React) ---
const runAttackStep = async (socket, db, scenario, tactic, stepIndex) => {
  // Check if attack is finished
  if (stepIndex >= scenario.steps.length) {
    isAttackRunning = false;
    socket.emit("attack_complete", { message: 'Attack Simulation Completed!' });
    if(attackTimeout) clearTimeout(attackTimeout);
    attackTimeout = null;
    return;
  }

  const step = scenario.steps[stepIndex];
  
  // 1. Emit the visual step to the frontend
  socket.emit("step_update", step);

  try {
    // 2. Save Red Team Log to SQLite
    const redLog = step.redLog;
    const { lastID: redLogId } = await db.run(
      'INSERT INTO logs (techniqueId, tactic, message, severity, type) VALUES (?, ?, ?, ?, ?)',
      scenario.techniqueId, tactic, redLog.message, redLog.severity, 'RED_TEAM'
    );
    // Get the full log (with ID and timestamp) to send back
    const fullRedLog = await db.get('SELECT * FROM logs WHERE id = ?', redLogId);
    socket.emit("new_log", fullRedLog); // 3. Push to frontend

    // 4. Save Blue Team Log to SQLite (if it exists)
    if (step.blueLog) {
      const blueLog = step.blueLog;
      const { lastID: blueLogId } = await db.run(
        'INSERT INTO logs (techniqueId, tactic, message, severity, type) VALUES (?, ?, ?, ?, ?)',
        scenario.techniqueId, tactic, blueLog.message, blueLog.severity, 'BLUE_TEAM'
      );
      // Get the full log to send back
      const fullBlueLog = await db.get('SELECT * FROM logs WHERE id = ?', blueLogId);
      socket.emit("new_log", fullBlueLog); // 5. Push to frontend
    }

  } catch (error) {
    console.error("Error writing log to database: ", error);
  }

  // 6. Schedule the next step
  attackTimeout = setTimeout(() => {
    runAttackStep(socket, db, scenario, tactic, stepIndex + 1);
  }, 2500); // 2.5 second delay
};

// --- API Endpoint to get all logs on page load ---
app.get('/logs', async (req, res) => {
  try {
    const logs = await db.all('SELECT * FROM logs ORDER BY timestamp DESC');
    res.json(logs);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// --- Real-time connection logic ---
io.on('connection', (socket) => {
  console.log('A user connected:', socket.id);

  // This is the "start attack" trigger from the frontend
  socket.on('start_attack', ({ technique, tactic }) => {
    if (isAttackRunning) {
      socket.emit("attack_error", { message: "An attack is already in progress." });
      return;
    }
    
    console.log(`Attack started: ${tactic}`);
    isAttackRunning = true;
    socket.emit("attack_started"); // Tell frontend to show "Attack in progress..."

    const scenario = scenarios[tactic] || getDefaultScenario(tactic);
    
    // Start the simulation loop on the server
    runAttackStep(socket, db, scenario, tactic, 0);
  });

  socket.on('disconnect', () => {
    console.log('A user disconnected:', socket.id);
  });
});

// Start the server
server.listen(PORT, async () => {
  db = await setupDatabase();
  console.log(`Backend server running on http://localhost:${PORT}`);
});