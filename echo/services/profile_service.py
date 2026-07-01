from typing import Optional


class ProfileService:
    def __init__(self):
        self._cache: dict = {}

    def fetch_profile(self, pubkey: str):
        pass

    def get_cached(self, pubkey: str) -> Optional[dict]:
        return self._cache.get(pubkey)

    def update_profile(self, profile):
        pass
