from typing import Optional

from nostr_sdk import Keys, EventBuilder, Event, Kind, Tag, PublicKey, Contact, RelayUrl


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
        builder = EventBuilder.text_note(content)
        if tags:
            builder = builder.tags([Tag.parse(t) for t in tags])
        return builder.sign_with_keys(self._keys)

    def sign_metadata(self, metadata: dict) -> Event:
        builder = EventBuilder(Kind(0), str(metadata))
        return builder.sign_with_keys(self._keys)

    def sign_reaction(self, event: Event, emoji: str = "+") -> Event:
        builder = EventBuilder.reaction(event, emoji)
        return builder.sign_with_keys(self._keys)

    def sign_repost(self, event: Event) -> Event:
        builder = EventBuilder.repost(event, None)
        return builder.sign_with_keys(self._keys)

    def sign_delete(self, event_ids: list[str]) -> Event:
        builder = EventBuilder.text_note("deleting")
        tags = [Tag.parse(["e", eid]) for eid in event_ids]
        builder = builder.tags(tags)
        return builder.sign_with_keys(self._keys)

    def sign_contact_list(self, contacts: list[tuple[str, str, str]]) -> Event:
        contact_objects = []
        for pubkey, relay, _ in contacts:
            pk = PublicKey.parse(pubkey)
            rl = RelayUrl.parse(relay) if relay else None
            contact_objects.append(Contact(public_key=pk, relay_url=rl))
        builder = EventBuilder.contact_list(contact_objects)
        return builder.sign_with_keys(self._keys)

    def sign_bookmarks_list(self, event_ids: list[str]) -> Event:
        builder = EventBuilder.text_note("bookmarks")
        tags = [Tag.parse(["a", f"30023:{eid}:", ""]) for eid in event_ids]
        builder = builder.tags(tags)
        return builder.sign_with_keys(self._keys)