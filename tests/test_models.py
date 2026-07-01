from echo.models import Note, Profile, Relay, DirectMessage


class TestNote:
    def test_is_reply(self):
        note = Note(id="1", pubkey="abc", content="hello", tags=[["e", "parent_id", "", "reply"]])
        assert note.is_reply
        assert note.reply_to == "parent_id"

    def test_not_reply(self):
        note = Note(id="2", pubkey="abc", content="hello")
        assert not note.is_reply
        assert note.reply_to is None

    def test_mentioned_pubkeys(self):
        note = Note(id="3", pubkey="abc", content="hello", tags=[["p", "pk1"], ["p", "pk2"]])
        assert note.mentioned_pubkeys == ["pk1", "pk2"]


class TestProfile:
    def test_handle_falls_back(self):
        profile = Profile(pubkey="abc")
        assert profile.handle == "abc"[:8]

    def test_handle_uses_display_name(self):
        profile = Profile(pubkey="abc", display_name="Alice")
        assert profile.handle == "Alice"


class TestRelay:
    def test_default_status(self):
        relay = Relay(url="wss://relay.damus.io")
        from echo.models.relay import RelayStatus
        assert relay.status == RelayStatus.DISCONNECTED


class TestDirectMessage:
    def test_not_sent_by_default(self):
        dm = DirectMessage(id="1", pubkey="abc", content="hi")
        assert not dm.is_sent
