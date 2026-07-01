from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .profile import Profile


@dataclass
class DirectMessage:
    id: str
    pubkey: str
    content: str
    created_at: int = 0
    tags: list = field(default_factory=list)

    sender: Optional["Profile"] = None

    @property
    def is_sent(self) -> bool:
        from echo.services.key_manager import KeyManager
        km = KeyManager.get()
        return km.pubkey == self.pubkey if km.has_key else False

    @property
    def reply_to(self):
        for tag in self.tags:
            if isinstance(tag, (list, tuple)) and len(tag) >= 2 and tag[0] == "p":
                return tag[1]
        return None

    @property
    def mentioned_pubkeys(self):
        return [tag[1] for tag in self.tags if isinstance(tag, (list, tuple)) and len(tag) >= 2 and tag[0] == "p"]
