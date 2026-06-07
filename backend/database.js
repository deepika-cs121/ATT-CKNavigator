import { open } from 'sqlite';
import sqlite3 from 'sqlite3';

// This function opens the database and creates the 'logs' table if it doesn't exist
export async function setupDatabase() {
  const db = await open({
    filename: './database.db',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      techniqueId TEXT NOT NULL,
      tactic TEXT NOT NULL,
      message TEXT NOT NULL,
      severity TEXT NOT NULL,
      type TEXT NOT NULL
    );
  `);

  return db;
}