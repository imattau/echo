import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk
from .widgets.sidebar import Sidebar
from .views.feed.feed_view import FeedView
from .views.discover.discover_view import DiscoverView
from .views.dms.dm_list import DMListView
from .views.bookmarks.bookmarks_view import BookmarksView
from .views.relays.relays_view import RelaysView
from .views.modals.compose_dialog import ComposeDialog
from .views.modals.account_switcher import AccountSwitcherPopover
from .views.settings.settings_window import SettingsWindow
from .views.onboarding.import_key_view import ImportKeyView
from echo.services.key_manager import KeyManager
from echo.services.relay_manager import RelayManager
from echo.services.profile_service import ProfileService
from echo.utils.config import Config


class EchoWindow(Adw.ApplicationWindow):
    def __init__(self, key_manager=None, relay_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Echo")
        self.set_default_size(1200, 800)

        self._key_manager = key_manager or KeyManager.get()
        self._relay_manager = relay_manager or RelayManager()
        self._profile_service = ProfileService()

        self.sidebar = Sidebar(key_manager=self._key_manager)
        self.sidebar.set_size_request(240, -1)

        self.content = Gtk.Stack()
        self.content.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)

        self._pages = {}
        for name, page_cls in [
            ("feed", FeedView),
            ("following", FeedView),
            ("discover", DiscoverView),
            ("dms", DMListView),
            ("bookmarks", BookmarksView),
            ("relays", RelaysView),
        ]:
            if page_cls is FeedView:
                page = FeedView(title_text="Following" if name == "following" else "Home")
            else:
                page = page_cls()
            self._pages[name] = page
            self.content.add_named(page, name)

        self.content.set_visible_child_name("feed")

        self.sidebar.connect("nav-changed", self._on_nav_changed)
        self.sidebar.connect("new-note", self._on_new_note)
        self.sidebar.connect("account-switch", self._on_account_switch)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_start_child(self.sidebar)
        paned.set_end_child(self.content)
        paned.set_shrink_start_child(False)
        paned.set_shrink_end_child(False)
        paned.set_position(240)

        self.set_content(paned)

        self._connect_default_relays()

    def _connect_default_relays(self):
        if self._key_manager.has_key:
            for url in Config.DEFAULT_RELAYS:
                self._relay_manager.add_relay(url)

    def _on_nav_changed(self, _sidebar, page_name: str):
        self.sidebar.set_active(page_name)
        if page_name == "settings":
            window = SettingsWindow(self)
            window.present()
        elif page_name in self._pages:
            self.content.set_visible_child_name(page_name)

    def _on_new_note(self, _sidebar):
        dialog = ComposeDialog(self)
        dialog.present()

    def _on_account_switch(self, _sidebar):
        popover = AccountSwitcherPopover()
        popover.set_parent(self.sidebar)
        popover.connect("add-account", self._on_add_account)
        popover.popup()

    def _on_add_account(self, _popover):
        import_view = ImportKeyView()
        window = Adw.Window(transient_for=self, modal=True)
        window.set_title("Import Existing Key")
        window.set_default_size(560, 400)
        window.set_content(import_view)
        import_view.connect("import-key", self._on_import_key_from_switcher)
        import_view.connect("back", lambda v: window.close())
        window.present()

    def _on_import_key_from_switcher(self, _view, key: str):
        if self._key_manager.import_key(key):
            self._key_manager.save_to_keyring()
