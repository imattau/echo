import asyncio
import json
import threading
from pathlib import Path
from typing import Optional, Callable

from nostr_sdk import Keys, SecretKey, PublicKey

from echo.utils.config import Config
from .async_bridge import AsyncBridge


class KeyManager:
    _instance: Optional["KeyManager"] = None
    _instance_lock: threading.Lock = threading.Lock()

    def __init__(self):
        self._keys: Optional[Keys] = None
        self._key_file = Config.STATE_DIR / "identity.json"

    @classmethod
    def get(cls) -> "KeyManager":
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @property
    def has_key(self) -> bool:
        return self._keys is not None

    @property
    def keys(self) -> Optional[Keys]:
        return self._keys

    @property
    def pubkey(self) -> Optional[str]:
        if self._keys:
            return self._keys.public_key().to_hex()
        return None

    @property
    def npub(self) -> Optional[str]:
        if self._keys:
            return self._keys.public_key().to_bech32()
        return None

    @property
    def nsec(self) -> Optional[str]:
        if self._keys:
            return self._keys.secret_key().to_bech32()
        return None

    def generate_keypair(self) -> tuple[str, str]:
        self._keys = Keys.generate()
        return (self.nsec or "", self.npub or "")

    def import_key(self, nsec_or_hex: str) -> bool:
        try:
            secret_key = SecretKey.parse(nsec_or_hex)
            self._keys = Keys(secret_key)
            return True
        except Exception:
            return False

    def save_to_keyring(self) -> bool:
        AsyncBridge.get().run(self._do_save_to_keyring())
        return True

    async def _do_save_to_keyring(self):
        try:
            import secretstorage
            loop = asyncio.get_running_loop()
            def _blocking_save():
                connection = secretstorage.dbus_init()
                collection = secretstorage.get_default_collection(connection)
                collection.create_item(
                    f"{Config.APP_ID} - nsec",
                    {"application": Config.APP_ID},
                    (self.nsec or "").encode(),
                )
            await loop.run_in_executor(None, _blocking_save)
        except Exception:
            self._save_to_file()

    def load_from_keyring(self) -> bool:
        try:
            import secretstorage
            connection = secretstorage.dbus_init()
            collection = secretstorage.get_default_collection(connection)
            for item in collection.get_all_items():
                if item.get_label() == f"{Config.APP_ID} - nsec":
                    secret = item.get_secret().decode()
                    return self.import_key(secret)
            return self._load_from_file()
        except Exception:
            return self._load_from_file()

    def load_from_keyring_async(self, callback: Callable[[bool], None]):
        AsyncBridge.get().run(self._do_load_from_keyring(callback))

    async def _do_load_from_keyring(self, callback: Callable[[bool], None]):
        result = False
        try:
            import secretstorage
            loop = asyncio.get_running_loop()
            def _blocking_load():
                connection = secretstorage.dbus_init()
                collection = secretstorage.get_default_collection(connection)
                for item in collection.get_all_items():
                    if item.get_label() == f"{Config.APP_ID} - nsec":
                        return item.get_secret().decode()
                return None
            secret = await loop.run_in_executor(None, _blocking_load)
            if secret:
                result = self.import_key(secret)
            if not result:
                result = self._load_from_file()
        except Exception:
            result = self._load_from_file()
        AsyncBridge.get().idle_add(callback, result)

    def clear_key(self):
        self._keys = None
        if self._key_file.exists():
            self._key_file.unlink()

    def _save_to_file(self) -> bool:
        if not self._keys:
            return False
        try:
            Config.STATE_DIR.mkdir(parents=True, exist_ok=True)
            self._key_file.write_text(json.dumps({"nsec": self.nsec}))
            self._key_file.chmod(0o600)
            return True
        except Exception:
            return False

    def _load_from_file(self) -> bool:
        try:
            if self._key_file.exists():
                data = json.loads(self._key_file.read_text())
                return self.import_key(data["nsec"])
            return False
        except Exception:
            return False
