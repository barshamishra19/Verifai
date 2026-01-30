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

def get_analysis_history(limit: int = 50):
    """Retrieve analysis history"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM analysis_results 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_statistics():
    """Get overall statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total analyses
    cursor.execute('SELECT COUNT(*) FROM analysis_results')
    total = cursor.fetchone()[0]
    
    # AI vs Real count
    cursor.execute('SELECT COUNT(*) FROM analysis_results WHERE classification = "AI-Generated"')
    ai_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM analysis_results WHERE classification = "Real"')
    real_count = cursor.fetchone()[0]
    
    # Average confidence
    cursor.execute('SELECT AVG(confidence) FROM analysis_results')
    avg_confidence = cursor.fetchone()[0] or 0.0
    
    # Average scores by engine
    cursor.execute('SELECT AVG(spatial_score), AVG(temporal_score), AVG(forensic_score), AVG(metadata_score) FROM analysis_results')
    avg_scores = cursor.fetchone()
    
    conn.close()
    
    return {
        'total_analyses': total,
        'ai_generated_count': ai_count,
        'real_count': real_count,
        'ai_percentage': round((ai_count / total * 100) if total > 0 else 0, 2),
        'average_confidence': round(avg_confidence, 4),
        'average_engine_scores': {
            'spatial': round(avg_scores[0] or 0, 4),
            'temporal': round(avg_scores[1] or 0, 4),
            'forensic': round(avg_scores[2] or 0, 4),
            'metadata': round(avg_scores[3] or 0, 4)
        }
    }

def get_result_by_id(job_id: str):
    """Get specific result by job ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM analysis_results WHERE job_id = ?', (job_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def clear_history():
    """Clear all history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM analysis_results')
    count = cursor.fetchone()[0]
    
    cursor.execute('DELETE FROM analysis_results')
    conn.commit()
    conn.close()
    
    return count