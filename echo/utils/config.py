from pathlib import Path


class Config:
    APP_ID = "com.echo.nostr"
    APP_NAME = "Echo"
    VERSION = "0.1.0"

    DATA_DIR = Path.home() / ".local" / "share" / "echo"
    CONFIG_DIR = Path.home() / ".config" / "echo"
    CACHE_DIR = Path.home() / ".cache" / "echo"

    DEFAULT_RELAYS = [
        "wss://relay.damus.io",
        "wss://nos.lol",
        "wss://relay.nostr.band",
        "wss://relay.snort.social",
    ]

    DEFAULT_ZAP_AMOUNT = 500
    MAX_NOTE_LENGTH = 280
