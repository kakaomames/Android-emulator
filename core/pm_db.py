import sqlite3

DB_PATH = "data/packages.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            id TEXT PRIMARY KEY,
            version_name TEXT,
            version_code INTEGER,
            icon_path TEXT,
            label TEXT,
            apk_path TEXT,
            native_lib_dir TEXT
        )
        """)
        conn.commit()

def insert_package(pkg):
    with get_conn() as conn:
        conn.execute("""
        INSERT OR REPLACE INTO packages
        (id, version_name, version_code, icon_path, label, apk_path, native_lib_dir)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            pkg["id"], pkg["version_name"], pkg["version_code"],
            pkg["icon_path"], pkg["label"], pkg["apk_path"], pkg["native_lib_dir"]
        ))
        conn.commit()

def get_package(package_id):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM packages WHERE id=?", (package_id,))
        return cur.fetchone()
