from typing import Optional

from nostr_sdk import Keys, EventBuilder, Event, Kind, Tag, PublicKey


class EventSigner:
    def __init__(self, keys: Keys):
        self._keys = keys

    @property
    def pubkey(self) -> str:
        return self._keys.public_key().to_hex()

    @property
    def npub(self) -> str:
        return self._keys.public_key().to_bech32()

    def sign_text_note(self, content: str, tags: Optional[list[list[str]]] = None) -> Event:
        builder = EventBuilder.text_note(content, tags or [])
        return builder.sign_with_keys(self._keys)

    def sign_metadata(self, metadata: dict) -> Event:
        kind0_kind = Kind(0)
        builder = EventBuilder(kind0_kind, str(metadata))
        return builder.sign_with_keys(self._keys)

    def sign_reaction(self, event_id: str, pubkey: str, emoji: str = "+") -> Event:
        tags = [
            ["e", event_id],
            ["p", pubkey],
        ]
        builder = EventBuilder.reaction(emoji, tags)
        return builder.sign_with_keys(self._keys)

    def sign_repost(self, event_id: str, pubkey: str) -> Event:
        tags = [
            ["e", event_id],
            ["p", pubkey],
        ]
        kind6 = Kind(6)
        builder = EventBuilder(kind6, "", tags)
        return builder.sign_with_keys(self._keys)

    def sign_delete(self, event_ids: list[str]) -> Event:
        kind5 = Kind(5)
        tags = [["e", eid] for eid in event_ids]
        builder = EventBuilder(kind5, "", tags)
        return builder.sign_with_keys(self._keys)

    def sign_contact_list(self, contacts: list[tuple[str, str, str]]) -> Event:
        kind3 = Kind(3)
        tags = [["p", pubkey, relay] for pubkey, relay, _ in contacts]
        builder = EventBuilder(kind3, "", tags)
        return builder.sign_with_keys(self._keys)

    def sign_bookmarks_list(self, event_ids: list[str]) -> Event:
        kind10003 = Kind(10003)
        tags = [["a", f"30023:{eid}:", ""] for eid in event_ids]
        builder = EventBuilder(kind10003, "", tags)
        return builder.sign_with_keys(self._keys)
