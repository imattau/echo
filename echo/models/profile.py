from dataclasses import dataclass, field
from typing import Optional


def _pubkey_to_npub(pubkey: str) -> str:
    try:
        from nostr_sdk import PublicKey
        return PublicKey.parse(pubkey).to_bech32()
    except Exception:
        return pubkey[:16]


def _deterministic_color(pubkey: str) -> str:
    colors = [
        "#3584E4", "#99BF8C", "#D99926", "#CC4D4D",
        "#33C7DE", "#8A5CF5", "#E06666", "#6AA84F",
        "#674EA7", "#A64D79", "#3D85C6", "#B45F06",
        "#45818E", "#5B6F55", "#7F6000", "#85200C",
    ]
    idx = sum(ord(c) for c in pubkey[:16]) % len(colors) if pubkey else 0
    return colors[idx]


@dataclass
class Profile:
    pubkey: str
    name: str = ""
    display_name: str = ""
    about: str = ""
    picture: str = ""
    banner: str = ""
    nip05: str = ""
    lud16: str = ""
    website: str = ""

    following_count: int = 0
    followers_count: int = 0
    notes_count: int = 0

    @property
    def npub(self) -> str:
        return _pubkey_to_npub(self.pubkey)

    @property
    def handle(self) -> str:
        return self.display_name or self.name or self.pubkey[:8]

    @property
    def initials(self) -> str:
        return self.handle[:2].upper()

    @property
    def avatar_color(self) -> str:
        return _deterministic_color(self.pubkey)
