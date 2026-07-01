from __future__ import annotations

from pathlib import Path
from typing import Optional

import gi

gi.require_version("GLib", "2.0")
gi.require_version("Gio", "2.0")

from gi.repository import GLib, Gio


class Config:
    APP_ID = "com.echo.nostr"
    APP_NAME = "Echo"
    VERSION = "0.1.0"

    DATA_DIR = Path(GLib.get_user_data_dir()) / "echo"
    CONFIG_DIR = Path(GLib.get_user_config_dir()) / "echo"
    CACHE_DIR = Path(GLib.get_user_cache_dir()) / "echo"
    STATE_DIR = Path(GLib.get_user_state_dir()) / "echo"

    DEFAULT_RELAYS = [
        "wss://relay.damus.io",
        "wss://nos.lol",
        "wss://relay.nostr.band",
        "wss://relay.snort.social",
    ]

    DEFAULT_ZAP_AMOUNT = 500
    MAX_NOTE_LENGTH = 280


class Settings:
    _instance: Optional["Settings"] = None

    def __init__(self):
        self._settings = Gio.Settings(schema_id=Config.APP_ID)

    @classmethod
    def get(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_bool(self, key: str) -> bool:
        return self._settings.get_boolean(key)

    def get_int(self, key: str) -> int:
        return self._settings.get_int(key)

    def get_string(self, key: str) -> str:
        return self._settings.get_string(key)

    def get_strv(self, key: str) -> list[str]:
        return list(self._settings.get_strv(key))

    def set_bool(self, key: str, value: bool):
        self._settings.set_boolean(key, value)

    def set_int(self, key: str, value: int):
        self._settings.set_int(key, value)

    def set_string(self, key: str, value: str):
        self._settings.set_string(key, value)

    def set_strv(self, key: str, value: list[str]):
        self._settings.set_strv(key, value)

    def bind(self, widget, key: str, prop: str = "active"):
        self._settings.bind(key, widget, prop, Gio.SettingsBindFlags.DEFAULT)

    def bind_inverted(self, widget, key: str, prop: str = "active"):
        self._settings.bind(key, widget, prop, Gio.SettingsBindFlags.INVERT_BOOLEAN)

    def connect(self, key: str, callback):
        self._settings.connect(f"changed::{key}", callback)

    def reset(self, key: str):
        self._settings.reset(key)

    def sync(self):
        self._settings.sync()
