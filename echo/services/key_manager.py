from typing import Optional


class KeyManager:
    def __init__(self):
        self._nsec: Optional[str] = None
        self._npub: Optional[str] = None

    @property
    def has_key(self) -> bool:
        return self._nsec is not None

    @property
    def pubkey(self) -> Optional[str]:
        return self._npub

    def generate_keypair(self) -> tuple[str, str]:
        return "", ""

    def import_key(self, nsec_or_hex: str) -> bool:
        return False

    def save_to_keyring(self) -> bool:
        return False

    def load_from_keyring(self) -> bool:
        return False

    def clear_key(self):
        self._nsec = None
        self._npub = None
