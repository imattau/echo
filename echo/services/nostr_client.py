import threading
from typing import Callable, Optional

from datetime import timedelta
from nostr_sdk import Client, Filter, Kind, PublicKey, Event, RelayUrl, Keys, NostrSigner
from .async_bridge import AsyncBridge


class NostrClient:
    def __init__(self, client: Optional[Client] = None):
        if client is not None:
            self._client = client
            self._owns_client = False
        else:
            self._client = Client()
            self._owns_client = True
        self._bridge = AsyncBridge.get()
        self._lock = threading.Lock()
        self._relays: dict[str, bool] = {}

    def connect_relay(self, url: str):
        self._bridge.run(self._do_connect(url))

    async def _do_connect(self, url: str):
        relay_url = RelayUrl.parse(url)
        await self._client.add_relay(relay_url)
        await self._client.connect()
        with self._lock:
            self._relays[url] = True

    def disconnect_relay(self, url: str):
        self._bridge.run(self._do_disconnect(url))

    async def _do_disconnect(self, url: str):
        relay_url = RelayUrl.parse(url)
        await self._client.remove_relay(relay_url)
        with self._lock:
            self._relays.pop(url, None)

    def publish_event(self, event):
        self._bridge.run(self._client.send_event(event))

    def subscribe(self, filters: Filter, callback: Callable, done_callback: Optional[Callable] = None, sub_id: str = ""):
        self._bridge.run(self._do_subscribe(filters, callback, done_callback))
        return sub_id

    async def _do_subscribe(self, filters: Filter, callback: Callable, done_callback: Optional[Callable] = None):
        events = await self._client.fetch_events(filters, timedelta(seconds=10))
        event_list = events.to_vec()
        batch_size = 10
        for i in range(0, len(event_list), batch_size):
            batch = event_list[i:i + batch_size]
            self._bridge.idle_add(self._process_event_batch, callback, batch)
        if done_callback is not None:
            self._bridge.idle_add(done_callback)

    def _process_event_batch(self, callback: Callable, batch):
        for event in batch:
            callback(event)

    def send_private_msg(self, keys: Keys, receiver: PublicKey, text: str):
        self._bridge.run(self._do_send_private_msg(keys, receiver, text))

    async def _do_send_private_msg(self, keys: Keys, receiver: PublicKey, text: str):
        signer = NostrSigner.keys(keys)
        self._client.signer = signer
        try:
            await self._client.send_private_msg(receiver, text)
        finally:
            self._client.signer = None

    def unsubscribe(self, sub_id: str):
        pass

    def get_relay_status(self) -> dict:
        with self._lock:
            return dict(self._relays)

    def close(self):
        if not self._owns_client:
            return
        with self._lock:
            urls = list(self._relays.keys())
        for url in urls:
            self.disconnect_relay(url)


class NostrClientFactory:
    @staticmethod
    def create() -> NostrClient:
        return NostrClient()
