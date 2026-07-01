from typing import Callable


class RelayManager:
    def __init__(self):
        self.relays: dict = {}

    def add_relay(self, url: str, read: bool = True, write: bool = True):
        pass

    def remove_relay(self, url: str):
        pass

    def get_relays(self) -> list:
        return list(self.relays.values())

    def connect_all(self):
        pass

    def disconnect_all(self):
        pass
