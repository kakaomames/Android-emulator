import sqlite3
from pathlib import Path

DB_PATH = Path("db/packages.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    with open("schema.sql") as f:
        cur.executescript(f.read())
    conn.commit()
    conn.close()

def register_package(package_info):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO packages 
        (package_name, version_code, version_name, label, icon_path, apk_path)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        package_info["package_name"],
        package_info["version_code"],
        package_info["version_name"],
        package_info["label"],
        package_info["icon_path"],
        package_info["apk_path"]
    ))

    for act in package_info.get("activities", []):
        cur.execute("""
            INSERT INTO activities (package_name, name, exported, intent_filters)
            VALUES (?, ?, ?, ?)
        """, (
            package_info["package_name"],
            act["name"],
            int(act["exported"]),
            act["intent_filters"]
        ))

    for perm in package_info.get("permissions", []):
        cur.execute("""
            INSERT INTO permissions (package_name, name)
            VALUES (?, ?)
        """, (package_info["package_name"], perm))

    for sig in package_info.get("signatures", []):
        cur.execute("""
            INSERT INTO signatures (package_name, cert_sha256)
            VALUES (?, ?)
        """, (package_info["package_name"], sig))

    conn.commit()
    conn.close()
