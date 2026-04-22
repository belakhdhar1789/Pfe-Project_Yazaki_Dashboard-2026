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

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")

if __name__ == '__main__':
    init_db()
