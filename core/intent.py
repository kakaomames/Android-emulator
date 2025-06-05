class Intent:
    def __init__(self, action: str = "", data: str = "", category: str = "", component: str = ""):
        self.action = action
        self.data = data
        self.category = category
        self.component = component  # "com.example/.MainActivity" の形式

# core/intent.py

from typing import Optional, Dict

class Intent:
    def __init__(self, action: Optional[str] = None, component: Optional[str] = None, extras: Optional[Dict] = None):
        self.action = action            # 例: android.intent.action.VIEW
        self.component = component      # 例: com.example.app/.MainActivity
        self.extras = extras or {}      # Intent.putExtra相当

    def put_extra(self, key: str, value):
        self.extras[key] = value

    def get_extra(self, key: str, default=None):
        return self.extras.get(key, default)

    def __repr__(self):
        return f"<Intent action={self.action}, component={self.component}, extras={self.extras}>"
