from typing import Optional


class ZapService:
    def __init__(self):
        self._connected = False
        self._balance = 0

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def balance(self) -> int:
        return self._balance

    def connect(self, connection_string: str) -> bool:
        return False

    def disconnect(self):
        pass

    def send_zap(self, pubkey: str, amount: int, message: str = "") -> bool:
        return False
