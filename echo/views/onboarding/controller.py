import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject
from .welcome_view import WelcomeView
from .import_key_view import ImportKeyView
from .backup_key_view import BackupKeyView
from .remote_signer_view import RemoteSignerView
from echo.services.key_manager import KeyManager
from echo.services.relay_manager import RelayManager
from echo.utils.config import Config, Settings


class OnboardingController(Adw.Window):
    __gsignals__ = {
        "done": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__()
        self.set_title("Welcome to Echo")
        self.set_default_size(640, 520)
        self.set_modal(True)

        self._key_manager = KeyManager.get()
        self._relay_manager = RelayManager()
        self._stack = Gtk.Stack()
        self._stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)

        self._welcome = WelcomeView()
        self._import_key = ImportKeyView()
        self._backup_key = None
        self._remote_signer = RemoteSignerView()

        self._stack.add_named(self._welcome, "welcome")
        self._stack.add_named(self._import_key, "import-key")
        self._stack.add_named(self._remote_signer, "remote-signer")

        self._welcome.connect("create-identity", self._on_create_identity)
        self._welcome.connect("import-key", self._on_import_key)
        self._welcome.connect("remote-signer", self._on_remote_signer)

        self._import_key.connect("back", self._on_back_to_welcome)
        self._import_key.connect("import-key", self._on_import_key_submit)

        self._remote_signer.connect("back", self._on_back_to_welcome)
        self._remote_signer.connect("connect-signer", self._on_remote_signer_connect)

        self.set_content(self._stack)
        self._stack.set_visible_child_name("welcome")

    def _show(self, name):
        self._stack.set_visible_child_name(name)

    def _on_back_to_welcome(self, _view):
        self._show("welcome")

    def _on_create_identity(self, _view):
        nsec, npub = self._key_manager.generate_keypair()
        self._key_manager.save_to_keyring()

        self._backup_key = BackupKeyView(nsec=nsec, npub=npub)
        self._backup_key.connect("back", self._on_back_to_welcome)
        self._backup_key.connect("continue", self._on_backup_complete)
        self._stack.add_named(self._backup_key, "backup-key")
        self._show("backup-key")

    def _on_backup_complete(self, _view):
        self._connect_default_relays()
        self._finish()

    def _on_import_key(self, _view):
        self._show("import-key")

    def _on_import_key_submit(self, _view, key: str):
        if self._key_manager.import_key(key):
            self._key_manager.save_to_keyring()
            self._connect_default_relays()
            self._finish()
        else:
            pass

    def _on_remote_signer(self, _view):
        self._show("remote-signer")

    def _on_remote_signer_connect(self, _view, url: str):
        self._connect_default_relays()
        self._finish()

    def _connect_default_relays(self):
        for url in Config.DEFAULT_RELAYS:
            self._relay_manager.add_relay(url)

    def _finish(self):
        Settings.get().set_bool("onboarding-completed", True)
        self.emit("done")
        self.close()
