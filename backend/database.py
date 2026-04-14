import sqlite3
import os
from datetime import datetime

# Paths
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(os.path.dirname(DB_DIR), "database")
DB_PATH = os.path.join(DB_DIR, "logs.db")

def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source_ip TEXT,
            destination_ip TEXT,
            protocol TEXT,
            packet_size INTEGER,
            prediction TEXT,
            confidence_score REAL
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized.")

def insert_log(source_ip, destination_ip, protocol, packet_size, prediction, confidence_score):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (source_ip, destination_ip, protocol, packet_size, prediction, confidence_score)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (source_ip, destination_ip, protocol, packet_size, prediction, confidence_score))
    conn.commit()
    conn.close()

def get_recent_logs(limit=50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, source_ip, destination_ip, protocol, packet_size, prediction, confidence_score
        FROM logs
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    logs = []
    for row in rows:
        logs.append({
            "id": row[0],
            "timestamp": row[1],
            "source_ip": row[2],
            "destination_ip": row[3],
            "protocol": row[4],
            "packet_size": row[5],
            "prediction": row[6],
            "confidence_score": row[7]
        })
    return logs

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM logs")
    total_packets = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM logs WHERE prediction = 'Attack'")
    total_attacks = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM logs WHERE prediction = 'Normal'")
    total_normal = cursor.fetchone()[0]
    
    # Get last 10 minutes traffic stats per minute (approximate)
    # SQLite datetime is string "YYYY-MM-DD HH:MM:SS"
    cursor.execute("""
        SELECT strftime('%H:%M', timestamp) as mn, COUNT(*) 
        FROM logs 
        GROUP BY mn 
        ORDER BY mn DESC 
        LIMIT 10
    """)
    time_series = [{"time": row[0], "count": row[1]} for row in cursor.fetchall()]
    time_series.reverse() # chronological
    
    conn.close()
    
    return {
        "total_packets": total_packets,
        "total_attacks": total_attacks,
        "total_normal": total_normal,
        "time_series": time_series
    }

if __name__ == "__main__":
    init_db()
