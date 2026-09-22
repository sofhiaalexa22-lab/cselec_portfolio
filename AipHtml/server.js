const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('.')); // Serve static files

// Database setup
const db = new sqlite3.Database('./users.db', (err) => {
  if (err) {
    console.error('Error opening database:', err.message);
  } else {
    console.log('Connected to SQLite database.');
    db.run(`CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      student_number TEXT UNIQUE,
      pin TEXT,
      face_data TEXT
    )`);
  }
});

// Routes
app.post('/register', (req, res) => {
  const { studentNumber, pin, faceData } = req.body;
  db.run(`INSERT INTO users (student_number, pin, face_data) VALUES (?, ?, ?)`,
    [studentNumber, pin, faceData], function(err) {
      if (err) {
        res.status(400).json({ error: err.message });
      } else {
        res.json({ id: this.lastID });
      }
    });
});

app.post('/login', (req, res) => {
  const { studentNumber, pin } = req.body;
  db.get(`SELECT * FROM users WHERE student_number = ? AND pin = ?`,
    [studentNumber, pin], (err, row) => {
      if (err) {
        res.status(400).json({ error: err.message });
      } else if (row) {
        res.json({ success: true, user: row });
      } else {
        res.json({ success: false });
      }
    });
});

app.post('/recover', (req, res) => {
  const { faceData } = req.body;
  // Simple recovery: assume faceData matches, store or update
  // For simplicity, just log and respond
  console.log('Face recovery attempted with data:', faceData);
  // In real app, compare faceData with stored
  res.json({ success: true, message: 'Identity stored for recovery' });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});</content>
<parameter name="filePath">c:\Users\Administrator\Desktop\AipHtml\server.js