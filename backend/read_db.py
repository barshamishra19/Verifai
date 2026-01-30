import sqlite3
import os

db_path = 'verifai_results.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM analysis_results ORDER BY timestamp DESC LIMIT 1')
    row = c.fetchone()
    if row:
        with open('latest_result.txt', 'w') as f:
            for k in row.keys():
                f.write(f"{k}: {row[k]}\n")
    conn.close()
