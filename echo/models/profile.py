from dataclasses import dataclass, field
from typing import Optional


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
        return self.pubkey

    @property
    def handle(self) -> str:
        return self.display_name or self.name or self.pubkey[:8]
