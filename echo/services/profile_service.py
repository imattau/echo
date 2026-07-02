import json
import threading
from typing import Callable, Optional

from datetime import timedelta
from nostr_sdk import Client, Filter, Kind, PublicKey, Event
from echo.models.profile import Profile
from .async_bridge import AsyncBridge


class ProfileService:
    def __init__(self):
        self._client = Client()
        self._bridge = AsyncBridge.get()
        self._lock = threading.Lock()
        self._cache: dict[str, Profile] = {}

    def fetch_profile(self, pubkey: str, callback: Optional[Callable] = None):
        self._bridge.run(self._do_fetch(pubkey, callback))

    async def _do_fetch(self, pubkey: str, callback: Optional[Callable] = None):
        public_key = PublicKey.parse(pubkey)
        f = Filter().kinds([Kind(0)]).authors([public_key]).limit(1)
        events = await self._client.fetch_events(f, timedelta(seconds=10))
        for event in events.to_vec():
            profile = self._parse_profile(pubkey, event)
            if profile:
                with self._lock:
                    self._cache[pubkey] = profile
                if callback:
                    self._bridge.idle_add(callback, profile)

    def get_cached(self, pubkey: str) -> Optional[Profile]:
        with self._lock:
            return self._cache.get(pubkey)

    def update_profile(self, profile: Profile):
        with self._lock:
            self._cache[profile.pubkey] = profile

    def get_all_cached(self) -> list[Profile]:
        with self._lock:
            return list(self._cache.values())

    def _parse_profile(self, pubkey: str, event: Event) -> Optional[Profile]:
        try:
            data = json.loads(event.content())
            return Profile(
                pubkey=pubkey,
                name=data.get("name", ""),
                display_name=data.get("display_name", ""),
                about=data.get("about", ""),
                picture=data.get("picture", ""),
                banner=data.get("banner", ""),
                nip05=data.get("nip05", ""),
                lud16=data.get("lud16", ""),
                website=data.get("website", ""),
            )
        except (json.JSONDecodeError, AttributeError):
            return None
