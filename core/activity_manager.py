import sqlite3
from core.intent import Intent

DB_PATH = "db/packages.db"

def start_activity(intent: Intent):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if intent.component:
        pkg, activity = intent.component.split("/", 1)
        c.execute("SELECT * FROM activities WHERE package_name = ? AND name = ?", (pkg, activity))
        row = c.fetchone()
        if row:
            print(f"✅ Activity started: {pkg}/{activity}")
            return True
        else:
            print("❌ Activity not found.")
            return False
    else:
        # TODO: intent-filtersで解決
        print("🔍 非component指定は未対応")
        return False
