from typing import Callable, Optional

from datetime import timedelta
from nostr_sdk import Client, Filter, Kind, PublicKey, Event, RelayUrl, ReqTarget
from .async_bridge import AsyncBridge


class NostrClient:
    def __init__(self):
        self._client = Client()
        self._bridge = AsyncBridge.get()
        self._relays: dict[str, bool] = {}

    def connect_relay(self, url: str):
        self._bridge.run(self._do_connect(url))

    async def _do_connect(self, url: str):
        relay_url = RelayUrl.parse(url)
        await self._client.add_relay(relay_url)
        await self._client.connect()
        self._relays[url] = True

    def disconnect_relay(self, url: str):
        self._bridge.run(self._do_disconnect(url))

    async def _do_disconnect(self, url: str):
        relay_url = RelayUrl.parse(url)
        await self._client.remove_relay(relay_url)
        self._relays.pop(url, None)

    def publish_event(self, event):
        self._bridge.run(self._client.send_event(event))

    def subscribe(self, filters: Filter, callback: Callable, sub_id: str = "") -> str:
        self._bridge.run(self._do_subscribe(filters, callback, sub_id))
        return sub_id

    async def _do_subscribe(self, filters: Filter, callback: Callable, sub_id: str):
        target = ReqTarget.auto([filters])
        events = await self._client.fetch_events(target, timedelta(seconds=10))
        for event in events.to_vec():
            self._bridge.idle_add(callback, event)

    def unsubscribe(self, sub_id: str):
        pass

    def get_relay_status(self) -> dict:
        return dict(self._relays)

    def close(self):
        for url in list(self._relays.keys()):
            self.disconnect_relay(url)


class NostrClientFactory:
    @staticmethod
    def create() -> NostrClient:
        return NostrClient()
