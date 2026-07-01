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
        return False
