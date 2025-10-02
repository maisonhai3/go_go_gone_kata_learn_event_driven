# event_broker.py
from collections import defaultdict
from typing import Callable, Any

class EventBroker:
    def __init__(self):
        print("Event Broker initialized.")
        self._subscribers = defaultdict(list)

    def subscribe(self, event_type: str, callback: Callable):
        """Đăng ký một hàm callback để lắng nghe một loại sự kiện."""
        print(f"New subscription: {callback.__qualname__} is listening for '{event_type}'")
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, data: Any):
        """Phát một sự kiện đến tất cả những người đã đăng ký."""
        print(f"\n📢 Publishing event '{event_type}' with data: {data}")
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error calling callback {callback.__qualname__}: {e}")

# Tạo một instance duy nhất để toàn bộ hệ thống sử dụng
broker = EventBroker()
