import sqlite3
import os
from datetime import datetime

# Paths
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(os.path.dirname(DB_DIR), "database")
DB_PATH = os.path.join(DB_DIR, "logs.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000;")
    return conn

def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL;")
    except Exception as e:
        print(f"WAL mode warning: {e}")
        
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
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
    try:
        # Use exact system local time
        local_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO logs (timestamp, source_ip, destination_ip, protocol, packet_size, prediction, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (local_time_str, source_ip, destination_ip, protocol, packet_size, prediction, confidence_score))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database insert error: {e}")

def get_recent_logs(limit=100, ip_filter=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if ip_filter and ip_filter.strip():
            ip_val = ip_filter.strip()
            cursor.execute("""
                SELECT id, timestamp, source_ip, destination_ip, protocol, packet_size, prediction, confidence_score
                FROM logs
                WHERE source_ip = ? OR destination_ip = ?
                ORDER BY id DESC
                LIMIT ?
            """, (ip_val, ip_val, limit))
        else:
            cursor.execute("""
                SELECT id, timestamp, source_ip, destination_ip, protocol, packet_size, prediction, confidence_score
                FROM logs
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            raw_ts = str(row[1]) if row[1] else ""
            display_time = raw_ts.split(" ")[1] if " " in raw_ts else raw_ts
            
            logs.append({
                "id": row[0],
                "timestamp": display_time if display_time else raw_ts,
                "full_timestamp": raw_ts,
                "source_ip": row[2],
                "destination_ip": row[3],
                "protocol": row[4],
                "packet_size": row[5],
                "prediction": row[6],
                "confidence_score": row[7]
            })
        return logs
    except Exception as e:
        print(f"Error reading logs: {e}")
        return []

def get_stats(ip_filter=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if ip_filter and ip_filter.strip():
            ip_val = ip_filter.strip()
            cursor.execute("SELECT COUNT(*) FROM logs WHERE source_ip = ? OR destination_ip = ?", (ip_val, ip_val))
            total_packets = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM logs WHERE (source_ip = ? OR destination_ip = ?) AND prediction = 'Attack'", (ip_val, ip_val))
            total_attacks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM logs WHERE (source_ip = ? OR destination_ip = ?) AND prediction = 'Normal'", (ip_val, ip_val))
            total_normal = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT strftime('%H:%M:%S', timestamp) as sec, COUNT(*) 
                FROM logs 
                WHERE source_ip = ? OR destination_ip = ?
                GROUP BY sec 
                ORDER BY id DESC 
                LIMIT 15
            """, (ip_val, ip_val))
        else:
            cursor.execute("SELECT COUNT(*) FROM logs")
            total_packets = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM logs WHERE prediction = 'Attack'")
            total_attacks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM logs WHERE prediction = 'Normal'")
            total_normal = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT strftime('%H:%M:%S', timestamp) as sec, COUNT(*) 
                FROM logs 
                GROUP BY sec 
                ORDER BY id DESC 
                LIMIT 15
            """)
            
        time_series = [{"time": row[0], "count": row[1]} for row in cursor.fetchall()]
        time_series.reverse()
        
        conn.close()
        
        return {
            "total_packets": total_packets,
            "total_attacks": total_attacks,
            "total_normal": total_normal,
            "time_series": time_series,
            "followed_ip": ip_filter.strip() if (ip_filter and ip_filter.strip()) else None
        }
    except Exception as e:
        print(f"Error reading stats: {e}")
        return {
            "total_packets": 0,
            "total_attacks": 0,
            "total_normal": 0,
            "time_series": [],
            "followed_ip": None
        }


if __name__ == "__main__":
    init_db()


