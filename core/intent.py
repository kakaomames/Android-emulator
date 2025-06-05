class Intent:
    def __init__(self, action: str = "", data: str = "", category: str = "", component: str = ""):
        self.action = action
        self.data = data
        self.category = category
        self.component = component  # "com.example/.MainActivity" の形式
