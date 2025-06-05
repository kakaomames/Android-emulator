from collections import defaultdict
from core.intent import Intent

# action: [callback1, callback2, ...]
broadcast_receivers = defaultdict(list)

def register_receiver(action: str, callback):
    broadcast_receivers[action].append(callback)
    print(f"📡 Receiver registered for: {action}")

def send_broadcast(intent: Intent):
    print(f"📨 Sending broadcast: {intent.action}")
    for callback in broadcast_receivers.get(intent.action, []):
        callback(intent)


# core/broadcast_bus.py

from typing import Callable, Dict, List
from core.intent import Intent

class BroadcastBus:
    def __init__(self):
        # action -> [handler, ...]
        self.receivers: Dict[str, List[Callable[[Intent], None]]] = {}

    def register_receiver(self, action: str, handler: Callable[[Intent], None]):
        if action not in self.receivers:
            self.receivers[action] = []
        self.receivers[action].append(handler)
        print(f"[BroadcastBus] 登録: action={action}")

    def send_broadcast(self, intent: Intent):
        handlers = self.receivers.get(intent.action, [])
        if not handlers:
            print(f"[BroadcastBus] {intent.action} に対する受信者は存在しません。")
            return

        print(f"[BroadcastBus] {intent.action} を {len(handlers)} 個のreceiverに送信中…")
        for handler in handlers:
            handler(intent)
