-- Initial schema for eCFR Analyzer database

CREATE TABLE IF NOT EXISTS titles (
  id INTEGER PRIMARY KEY,
  title_number INTEGER NOT NULL,
  title_name TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agencies (
  id INTEGER PRIMARY KEY,
  agency_name TEXT NOT NULL,
  agency_code TEXT,
  title_id INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (title_id) REFERENCES titles(id)
);

CREATE TABLE IF NOT EXISTS metrics (
  id INTEGER PRIMARY KEY,
  title_id INTEGER,
  agency_id INTEGER,
  word_count INTEGER,
  sentence_count INTEGER,
  complexity_score REAL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (title_id) REFERENCES titles(id),
  FOREIGN KEY (agency_id) REFERENCES agencies(id)
);