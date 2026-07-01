from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .profile import Profile

IMETA_URL_RE = re.compile(r"imeta[:\s]url[:\s](\S+)", re.IGNORECASE)


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

    PREVIEW_MAX = 500

    @property
    def is_reply(self):
        for tag in self.tags:
            if isinstance(tag, (list, tuple)) and len(tag) >= 1 and tag[0] == "e":
                if len(tag) >= 4 and tag[3] == "reply":
                    return True
        return False

    @property
    def reply_to(self):
        for tag in self.tags:
            if isinstance(tag, (list, tuple)) and len(tag) >= 2 and tag[0] == "e":
                return tag[1]
        return None

    @property
    def mentioned_pubkeys(self):
        return [tag[1] for tag in self.tags if isinstance(tag, (list, tuple)) and len(tag) >= 2 and tag[0] == "p"]

    @property
    def truncated_content(self) -> str:
        if len(self.content) > self.PREVIEW_MAX:
            return self.content[:self.PREVIEW_MAX] + "…"
        return self.content

    @property
    def is_truncated(self) -> bool:
        return len(self.content) > self.PREVIEW_MAX

    @property
    def media_urls(self) -> list[str]:
        urls = []
        for tag in self.tags:
            if isinstance(tag, (list, tuple)) and len(tag) >= 2:
                if tag[0] == "imeta" and ":" in str(tag[1]):
                    match = IMETA_URL_RE.search(":".join(str(t) for t in tag))
                    if match:
                        urls.append(match.group(1))
                elif tag[0] in ("image", "video") and len(tag) >= 2:
                    urls.append(tag[1])
        return urls
