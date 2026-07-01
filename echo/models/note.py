from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .profile import Profile


@dataclass
class Note:
    id: str
    pubkey: str
    content: str
    kind: int = 1
    tags: list = field(default_factory=list)
    sig: str = ""
    created_at: int = 0

    profile: Optional["Profile"] = None

    reply_count: int = 0
    repost_count: int = 0
    like_count: int = 0
    zap_count: int = 0
    zap_amount: int = 0

    @property
    def is_reply(self):
        for tag in self.tags:
            if tag[0] == "e" and len(tag) >= 4 and tag[3] == "reply":
                return True
        return False

    @property
    def reply_to(self):
        for tag in self.tags:
            if tag[0] == "e":
                return tag[1]
        return None

    @property
    def mentioned_pubkeys(self):
        return [tag[1] for tag in self.tags if tag[0] == "p"]
