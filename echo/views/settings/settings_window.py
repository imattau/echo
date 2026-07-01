import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw
from ..relays.relays_view import RelaysPage


class SettingsWindow(Adw.Window):
    def __init__(self, parent):
        super().__init__(transient_for=parent, modal=True)
        self.set_title("Preferences")
        self.set_default_size(960, 640)

        nav = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        sidebar.set_size_request(200, -1)
        sidebar.add_css_class("sidebar")

        prefs_label = Gtk.Label(label="PREFERENCES")
        prefs_label.set_margin_start(12)
        prefs_label.set_margin_top(16)
        prefs_label.set_margin_bottom(8)
        sidebar.append(prefs_label)

        items = [
            "General",
            "Appearance",
            "Relays",
            "Accounts",
            "Wallet",
            "Notifications",
        ]

        self._stack = Gtk.Stack()
        self._stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)

        from .general_page import GeneralPage
        from .appearance_page import AppearancePage
        from .wallet_page import WalletPage
        from .accounts_page import AccountsPage
        from .notifications_page import NotificationsPage

        pages = {
            "General": GeneralPage(),
            "Appearance": AppearancePage(),
            "Relays": RelaysPage(),
            "Wallet": WalletPage(),
            "Accounts": AccountsPage(),
            "Notifications": NotificationsPage(),
        }

        self._nav_buttons = {}
        for i, name in enumerate(items):
            btn = Gtk.Button(label=name)
            btn.set_halign(Gtk.Align.START)
            btn.set_margin_start(8)
            btn.set_margin_end(8)
            page = pages.get(name)
            if page:
                self._stack.add_named(page, name.lower())
                if i == 0:
                    self._stack.set_visible_child_name(name.lower())
                    self._set_active(btn)
            btn.connect("clicked", self._on_nav, btn, name.lower())
            self._nav_buttons[name.lower()] = btn
            sidebar.append(btn)

        nav.append(sidebar)
        nav.append(self._stack)

        self.set_content(nav)

    def _set_active(self, active_btn):
        for btn in self._nav_buttons.values():
            if btn is active_btn:
                if "nav-active" not in btn.get_css_classes():
                    btn.add_css_class("nav-active")
            else:
                if "nav-active" in btn.get_css_classes():
                    btn.remove_css_class("nav-active")

    def _on_nav(self, btn, page_name: str):
        self._set_active(btn)
        self._stack.set_visible_child_name(page_name)
