from echo.services.nostr_client import NostrClient
from echo.services.key_manager import KeyManager
from echo.services.relay_manager import RelayManager
from echo.services.profile_service import ProfileService
from echo.services.zap_service import ZapService


class TestNostrClient:
    def test_init(self):
        client = NostrClient()
        assert client.get_relay_status() == {}


class TestKeyManager:
    def test_no_key_by_default(self):
        km = KeyManager()
        assert not km.has_key
        assert km.pubkey is None


class TestRelayManager:
    def test_init(self):
        rm = RelayManager()
        assert rm.get_relays() == []


class TestProfileService:
    def test_empty_cache(self):
        ps = ProfileService()
        assert ps.get_cached("abc") is None


class TestZapService:
    def test_not_connected_by_default(self):
        zs = ZapService()
        assert not zs.is_connected
        assert zs.balance == 0
