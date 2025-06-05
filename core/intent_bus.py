# core/intent_bus.py

from typing import Callable, Dict, List

# BroadcastReceiverのリスナーマップ
_broadcast_listeners: Dict[str, List[Callable]] = {}

def register_broadcast(action: str, callback: Callable):
    if action not in _broadcast_listeners:
        _broadcast_listeners[action] = []
    _broadcast_listeners[action].append(callback)
    print(f"[REGISTER] Broadcast listener registered for '{action}'")

def send_broadcast(action: str, extras: dict = None):
    print(f"[BROADCAST] Sending: {action}")
    listeners = _broadcast_listeners.get(action, [])
    for callback in listeners:
        callback(extras or {})
