from __future__ import annotations

import os
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

    _SCHEMA_DIR = str(Path(__file__).parent.parent.parent / "data")


# Point GSettings at our local schema if not installed system-wide
if "GSETTINGS_SCHEMA_DIR" not in os.environ:
    schema_xml = Path(Config._SCHEMA_DIR) / f"{Config.APP_ID}.gschema.xml"
    if schema_xml.exists():
        os.environ["GSETTINGS_SCHEMA_DIR"] = Config._SCHEMA_DIR


class _DictSettingsBackend:
    """Fallback when GSettings schema is unavailable."""

    _DEFAULTS: dict = {
        "open-to-following-feed": False,
        "restore-last-window-state": True,
        "confirm-before-posting": False,
        "default-relays": [
            "wss://relay.damus.io",
            "wss://nos.lol",
            "wss://relay.nostr.band",
            "wss://relay.snort.social",
        ],
        "theme": "system",
        "accent-color": "#3584E4",
        "compact-mode": False,
        "show-media-previews": True,
        "language": "en-AU",
        "default-zap-amount": 500,
        "auto-zap-on-like": False,
        "skip-zap-confirmation-under": 1000,
        "notify-replies": True,
        "notify-zaps": True,
        "notify-dms": True,
        "notify-sound": False,
    }

    def __init__(self):
        self._store = dict(self._DEFAULTS)

    def get_boolean(self, key):
        return bool(self._store.get(key, False))

    def get_int(self, key):
        return int(self._store.get(key, 0))

    def get_string(self, key):
        return str(self._store.get(key, ""))

    def get_strv(self, key):
        val = self._store.get(key, [])
        return list(val) if isinstance(val, (list, tuple)) else []

    def set_boolean(self, key, value):
        self._store[key] = value

    def set_int(self, key, value):
        self._store[key] = value

    def set_string(self, key, value):
        self._store[key] = value

    def set_strv(self, key, value):
        self._store[key] = list(value)

    def bind(self, widget, key, prop="active"):
        initial = self._store.get(key, self._DEFAULTS.get(key))
        if initial is not None:
            widget.set_property(prop, initial)

        def _on_widget_changed(*args):
            self._store[key] = widget.get_property(prop)

        widget.connect(f"notify::{prop}", _on_widget_changed)

    def bind_inverted(self, widget, key, prop="active"):
        initial = self._store.get(key, self._DEFAULTS.get(key))
        if initial is not None:
            widget.set_property(prop, not initial)

        def _on_widget_changed(*args):
            self._store[key] = not widget.get_property(prop)

        widget.connect(f"notify::{prop}", _on_widget_changed)

    def connect(self, key, callback):
        pass

    def reset(self, key):
        self._store[key] = self._DEFAULTS.get(key)

    def sync(self):
        pass


class Settings:
    _instance: Optional["Settings"] = None

    def __init__(self):
        schema_source = Gio.SettingsSchemaSource.get_default()
        schema = schema_source.lookup(Config.APP_ID, True) if schema_source else None
        if schema is not None:
            self._settings = Gio.Settings(schema_id=Config.APP_ID)
        else:
            self._settings = _DictSettingsBackend()

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
