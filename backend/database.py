import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'yazaki.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # ── Users table ──────────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name    TEXT NOT NULL,
            matricule    TEXT UNIQUE NOT NULL,
            email        TEXT UNIQUE NOT NULL,
            password     TEXT NOT NULL,
            role         TEXT DEFAULT 'user',
            status       TEXT DEFAULT 'pending',
            access_mode  TEXT DEFAULT 'manual',
            last_login   TEXT DEFAULT '',
            last_activity TEXT DEFAULT '',
            created_at   TEXT DEFAULT (datetime('now'))
        )
    ''')

    # Migration: add new columns to existing databases (safe — no-op if already exists)
    for col, definition in [
        ('email',         "TEXT NOT NULL DEFAULT ''"),
        ('access_mode',   "TEXT DEFAULT 'manual'"),
        ('last_login',    "TEXT DEFAULT ''"),
        ('last_activity', "TEXT DEFAULT ''"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")
        except Exception:
            pass  # column already exists

    # ── Permissions table ────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            page_name  TEXT NOT NULL,
            can_access INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # ── Stations table ───────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stations (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            station_no   INTEGER UNIQUE NOT NULL,
            station_name TEXT,
            avg_gum      REAL DEFAULT 0,
            avg_awt      REAL DEFAULT 0,
            min_gum      REAL DEFAULT 0,
            max_gum      REAL DEFAULT 0,
            min_awt      REAL DEFAULT 0,
            max_awt      REAL DEFAULT 0,
            tact_time    REAL DEFAULT 2.09,
            cycle_time   REAL DEFAULT 0,
            updated_at   TEXT DEFAULT (datetime('now'))
        )
    ''')

    # ── Revisions table ─────────────────────────────────────
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS revisions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            summary    TEXT NOT NULL,
            revision   TEXT NOT NULL,
            date       TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')

    # ── Seed default revisions ───────────────────────────────
    cursor.execute("SELECT COUNT(*) FROM revisions")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO revisions (summary, revision, date) VALUES (?, ?, ?)",
            [
                ('Initial release', 'New', '13-Jul-23'),
                ('Update',          '1',   '2-Oct-23'),
            ]
        )

    # ── Seed default admin ───────────────────────────────────
    cursor.execute("SELECT id FROM users WHERE matricule = 'admin001'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (full_name, matricule, email, password, role, status, access_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('Administrator', 'admin001', 'admin@yazaki.com',
              hash_password('admin123'), 'admin', 'active', 'manual'))

    # ── Seed 34 stations ─────────────────────────────────────
    for i in range(1, 35):
        cursor.execute("SELECT id FROM stations WHERE station_no = ?", (i,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO stations (station_no, station_name) VALUES (?, ?)",
                (i, f'Workstation {i}')
            )

    # ── Table config table ────────────────────────────────────
    # Stores the full table as a single JSON document.
    # Columns: list of station names  ["WS 1", "WS 2", …]
    # Rows:    list of {label, values} objects
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS table_config (
            id         INTEGER PRIMARY KEY,
            data       TEXT NOT NULL,
            updated_at TEXT DEFAULT (datetime('now'))
        )
    ''')

    # Seed with the default 34-station / 14-metric data
    import json
    cursor.execute("SELECT COUNT(*) FROM table_config")
    if cursor.fetchone()[0] == 0:
        default_data = {
            "columns": [f"WS {i}" for i in range(1, 35)],
            "rows": [
                {"label": "Min GUM",                    "values": ["1.67","1.75","2.87","2.46","2.55","2.87","2.95","3.67","3.80","3.55","3.34","3.16","3.51","2.74","4.08","2.17","2.79","3.70","4.45","3.81","4.44","4.00","4.00","3.84","3.76","3.42","2.33","2.04","2.00","2.03","2.05","3.51","3.45","3.03"]},
                {"label": "Min AWT",                    "values": ["1.67","1.75","2.87","2.46","2.55","2.87","2.95","3.67","3.80","3.55","3.34","3.16","3.51","2.74","4.08","2.17","2.79","3.70","4.45","3.81","4.44","4.00","4.00","3.84","3.76","3.42","2.33","2.04","2.00","2.03","2.05","3.51","3.45","3.03"]},
                {"label": "Max GUM",                    "values": ["2.62","2.91","2.87","2.46","2.55","2.95","2.95","3.67","4.03","3.86","3.34","3.16","3.51","2.74","4.08","2.17","2.79","3.70","4.75","3.22","2.48","4.97","4.97","3.80","3.84","4.00","3.42","1.67","1.05","1.62","1.05","4.24","3.24","1.75"]},
                {"label": "Max AWT",                    "values": ["2.00","2.75","2.87","2.46","2.55","3.09","2.95","3.67","3.80","3.55","3.34","3.16","3.51","2.74","4.08","2.17","2.79","3.70","4.45","3.81","4.44","4.00","4.00","3.84","3.76","3.42","2.33","2.04","2.00","2.03","2.05","3.51","3.45","3.03"]},
                {"label": "Fluctuation (Max-Min) GUM",  "values": ["0.95","0","0","0","0","0.22","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"]},
                {"label": "Fluctuation Rate GUM",       "values": ["0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%"]},
                {"label": "Fluctuation (Max-Min) AWT",  "values": ["0","0","0","0","0","0.22","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0"]},
                {"label": "Fluctuation Rate AWT",       "values": ["0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%","0%"]},
                {"label": "Tact time",                  "values": ["2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09","2.09"]},
                {"label": "Convergence",                "values": ["1.1","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3"]},
                {"label": "(CT - CV speed ())",         "values": ["1.1","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3","1.3"]},
                {"label": "Actual Cycle Time Measured", "values": ["1.61","2.33","2.87","2.46","2.55","2.91","2.95","3.67","3.91","3.71","3.34","3.16","3.51","2.74","4.08","2.17","2.79","3.70","4.45","3.51","3.46","4.48","4.48","3.84","3.76","3.42","2.88","2.04","1.53","1.83","1.05","3.84","3.45","2.39"]},
                {"label": "Average GUM",                "values": ["1.94","2.12","2.87","2.46","2.55","2.91","2.95","3.67","3.92","3.71","3.34","3.16","3.51","2.74","4.08","2.17","2.79","3.70","4.54","3.84","3.76","3.42","2.12","2.04","2.00","2.03","2.05","3.51","3.45","3.03","0","0","0","0"]},
                {"label": "Average AWT",                "values": ["1.84","2.25","2.87","2.46","2.55","2.98","2.95","3.67","3.80","3.55","3.34","3.16","3.51","2.74","4.08","2.17","2.79","3.70","4.45","3.81","4.44","4.00","4.00","3.84","3.76","3.42","2.33","2.04","2.00","2.03","2.05","3.51","3.45","3.03"]},
            ]
        }
        cursor.execute(
            "INSERT INTO table_config (id, data) VALUES (1, ?)",
            (json.dumps(default_data),)
        )

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")

if __name__ == '__main__':
    init_db()
