# backend/database.py
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "verifai_results.db")

def init_db():
    """Creates the database table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            job_id TEXT PRIMARY KEY,
            filename TEXT,
            classification TEXT,
            confidence REAL,
            spatial_score REAL,
            temporal_score REAL,
            forensic_score REAL,
            metadata_score REAL,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database Initialized")

def save_analysis_result(job_id, filename, report, breakdown):
    """Saves the scan data to SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO analysis_results 
        (job_id, filename, classification, confidence, spatial_score, temporal_score, forensic_score, metadata_score, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        job_id, 
        filename, 
        report.get('classification'), 
        report.get('final_confidence'),
        breakdown.get('spatial'),
        breakdown.get('temporal'),
        breakdown.get('forensic'),
        breakdown.get('metadata'),
        datetime.now()
    ))
    conn.commit()
    conn.close()