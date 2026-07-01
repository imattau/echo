from typing import Optional

from nostr_sdk import (
    Keys, EventBuilder, ZapRequestData, PublicKey, RelayUrl,
    nip57_anonymous_zap_request, NostrWalletConnect,
)
from .async_bridge import AsyncBridge


class ZapService:
    def __init__(self):
        self._bridge = AsyncBridge.get()
        self._nwc: Optional[NostrWalletConnect] = None
        self._connected = False
        self._balance = 0

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def balance(self) -> int:
        return self._balance

    def connect(self, connection_string: str) -> bool:
        self._bridge.run(self._do_connect(connection_string))
        return True

    async def _do_connect(self, connection_string: str):
        try:
            self._nwc = NostrWalletConnect(connection_string)
            info = await self._nwc.get_info()
            self._connected = True
            if hasattr(info, "balance"):
                self._balance = info.balance
        except Exception:
            self._connected = False

    def disconnect(self):
        self._nwc = None
        self._connected = False
        self._balance = 0

    def send_zap(self, pubkey: str, amount: int, message: str = "") -> bool:
        self._bridge.run(self._do_zap(pubkey, amount, message))
        return True

    async def _do_zap(self, pubkey: str, amount: int, message: str):
        try:
            if self._nwc:
                public_key = PublicKey.parse(pubkey)
                relay_list = [RelayUrl.parse("wss://relay.damus.io")]
                data = ZapRequestData(public_key, relay_list)
                if message:
                    data = data.message(message)
                zap_event = nip57_anonymous_zap_request(data)
                await self._nwc.pay_invoice(zap_event, amount * 1000)
        except Exception:
            pass

    def build_zap_request(self, pubkey: str, amount: int, message: str = ""):
        try:
            public_key = PublicKey.parse(pubkey)
            relay_list = [RelayUrl.parse("wss://relay.damus.io")]
            data = ZapRequestData(public_key, relay_list).message(message) if message else ZapRequestData(public_key, relay_list)
            return nip57_anonymous_zap_request(data)
        except Exception:
            return None
