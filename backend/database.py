import sqlite3
import os
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'yazaki.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            matricule TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            page_name TEXT NOT NULL,
            can_access INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS stations (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            gum_minutes REAL NOT NULL,
            position INTEGER
        );

        CREATE TABLE IF NOT EXISTS gum_awt_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id INTEGER,
            shift TEXT,
            date TEXT,
            gum REAL,
            awt REAL,
            ratio REAL,
            source TEXT DEFAULT 'simulator',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (station_id) REFERENCES stations(id)
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id INTEGER,
            level INTEGER,
            message TEXT,
            acknowledged INTEGER DEFAULT 0,
            ack_by TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS andon_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id INTEGER,
            category TEXT,
            description TEXT,
            operator_id TEXT,
            shift TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS data_collection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id INTEGER,
            part_number TEXT,
            f_number TEXT,
            working_time_min REAL,
            target_qty INTEGER,
            actual_qty INTEGER,
            npt_percent REAL,
            gum REAL,
            awt REAL,
            shift TEXT,
            date TEXT,
            entered_by TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS batches_ksk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id INTEGER,
            sk_reference TEXT,
            variant TEXT,
            status TEXT DEFAULT 'unverified',
            scanned_at DATETIME
        );

        CREATE TABLE IF NOT EXISTS revisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            variant_name TEXT,
            description TEXT,
            applied_by TEXT,
            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS shift_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shift TEXT,
            date TEXT,
            oee REAL,
            avg_ratio REAL,
            total_alerts INTEGER,
            total_andon INTEGER,
            generated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Insert 34 default stations if empty
    cursor.execute("SELECT COUNT(*) FROM stations")
    if cursor.fetchone()[0] == 0:
        stations = [(i, f"Station {i:02d}", 12.0, i) for i in range(1, 35)]
        cursor.executemany(
            "INSERT INTO stations (id, name, gum_minutes, position) VALUES (?, ?, ?, ?)",
            stations
        )

    # Insert default admin if no users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (full_name, matricule, password, role, status) VALUES (?, ?, ?, ?, ?)",
            ("Admin Yazaki", "admin001", hash_password("admin123"), "admin", "active")
        )

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

if __name__ == "__main__":
    init_db()