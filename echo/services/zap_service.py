import threading
from typing import Callable, Optional

from nostr_sdk import (
    Keys, EventBuilder, ZapRequestData, PublicKey, RelayUrl,
    nip57_anonymous_zap_request, Nwc, NostrWalletConnectUri,
)
from .async_bridge import AsyncBridge


class ZapService:
    def __init__(self):
        self._bridge = AsyncBridge.get()
        self._lock = threading.Lock()
        self._nwc: Optional[Nwc] = None
        self._connected = False
        self._balance = 0

    @property
    def is_connected(self) -> bool:
        with self._lock:
            return self._connected

    @property
    def balance(self) -> int:
        with self._lock:
            return self._balance

    def connect(self, connection_string: str, callback: Optional[Callable] = None):
        self._bridge.run(self._do_connect(connection_string, callback))

    async def _do_connect(self, connection_string: str, callback: Optional[Callable] = None):
        try:
            uri = NostrWalletConnectUri.parse(connection_string)
            nwc = Nwc(uri)
            info = await nwc.get_info()
            name = info.alias or ""
            balance = 0
            try:
                balance_resp = await nwc.get_balance()
                balance = balance_resp.balance if hasattr(balance_resp, "balance") else 0
            except Exception:
                pass
            with self._lock:
                self._nwc = nwc
                self._connected = True
                self._balance = balance
            if callback:
                self._bridge.idle_add(callback, True, name, str(balance))
        except Exception as e:
            with self._lock:
                self._connected = False
                self._nwc = None
            if callback:
                self._bridge.idle_add(callback, False, str(e), "")

    def disconnect(self):
        with self._lock:
            self._nwc = None
            self._connected = False
            self._balance = 0

    def send_zap(self, pubkey: str, amount: int, message: str = "") -> bool:
        self._bridge.run(self._do_zap(pubkey, amount, message))
        return True

    async def _do_zap(self, pubkey: str, amount: int, message: str):
        try:
            with self._lock:
                nwc = self._nwc
            if not nwc:
                return
            from nostr_sdk import PayInvoiceRequest
            recipient_pk = PublicKey.parse(pubkey)
            relay_list = [RelayUrl.parse("wss://relay.damus.io")]
            zap_data = ZapRequestData(recipient_pk, relay_list).message(message) if message else ZapRequestData(recipient_pk, relay_list)
            zap_event = nip57_anonymous_zap_request(zap_data)
            invoice = zap_event.as_json() if hasattr(zap_event, "as_json") else str(zap_event)
            request = PayInvoiceRequest(invoice=invoice, amount=amount * 1000)
            await self._nwc.pay_invoice(request)
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