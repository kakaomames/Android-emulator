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
