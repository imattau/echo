from typing import Callable, Optional


class NostrClient:
    def __init__(self):
        self.relays: dict = {}

    def connect_relay(self, url: str):
        pass

    def disconnect_relay(self, url: str):
        pass

    def publish_event(self, event):
        pass

    def subscribe(self, filters: dict, callback: Callable) -> str:
        return ""

    def unsubscribe(self, sub_id: str):
        pass

    def close(self):
        for url in list(self.relays.keys()):
            self.disconnect_relay(url)
