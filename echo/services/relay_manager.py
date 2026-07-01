from typing import Callable, Optional

from nostr_sdk import Client, RelayUrl
from echo.models.relay import Relay, RelayStatus
from .async_bridge import AsyncBridge


class RelayManager:
    def __init__(self):
        self._client = Client()
        self._bridge = AsyncBridge.get()
        self._relays: dict[str, Relay] = {}

    def add_relay(self, url: str, read: bool = True, write: bool = True):
        if url not in self._relays:
            relay = Relay(url=url, read=read, write=write, status=RelayStatus.DISCONNECTED)
            self._relays[url] = relay
        self._bridge.run(self._do_connect(url))

    async def _do_connect(self, url: str):
        relay_url = RelayUrl.parse(url)
        await self._client.add_relay(relay_url)
        await self._client.connect()
        if url in self._relays:
            self._relays[url].status = RelayStatus.CONNECTED

    def remove_relay(self, url: str):
        self._bridge.run(self._do_remove(url))

    async def _do_remove(self, url: str):
        relay_url = RelayUrl.parse(url)
        await self._client.remove_relay(relay_url)
        self._relays.pop(url, None)

    def get_relays(self) -> list[Relay]:
        return list(self._relays.values())

    def get_connected_relays(self) -> list[Relay]:
        return [r for r in self._relays.values() if r.status == RelayStatus.CONNECTED]

    def connect_all(self):
        for url in list(self._relays.keys()):
            self._bridge.run(self._do_connect(url))

    def disconnect_all(self):
        for url in list(self._relays.keys()):
            self._bridge.run(self._do_remove(url))

    def update_status_from_relay(self, url: str, status: RelayStatus, latency_ms: int = 0):
        if url in self._relays:
            self._relays[url].status = status
            self._relays[url].latency_ms = latency_ms
