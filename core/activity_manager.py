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

# core/activity_manager.py

from core.intent import Intent

class ActivityNotFound(Exception):
    pass

class ActivityManager:
    def __init__(self, app_registry):
        self.app_registry = app_registry  # パッケージIDごとにアプリ情報が格納されている辞書

    def start_activity(self, intent: Intent):
        if not intent.component:
            raise ActivityNotFound("Intentにcomponentが指定されていません。")

        package_name, activity_name = self._parse_component(intent.component)

        app = self.app_registry.get(package_name)
        if not app or activity_name not in app['activities']:
            raise ActivityNotFound(f"{intent.component} が見つかりません。")

        # 起動シミュレーション（ログ or 関数実行など）
        print(f"[ActivityManager] {intent.component} を起動中…")
        activity_handler = app['activities'][activity_name]
        activity_handler(intent)

    def _parse_component(self, component: str):
        # 例: "com.example.app/.MainActivity" → ("com.example.app", ".MainActivity")
        if '/' not in component:
            raise ValueError("component はパッケージ名/Activity名の形式で指定してください。")
        package, activity = component.split('/')
        return package, activity
