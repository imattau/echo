import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, Gtk, Gdk
from .window import EchoWindow
from .services.key_manager import KeyManager
from .views.onboarding.controller import OnboardingController
from pathlib import Path


class EchoApplication(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.echo.nostr",
            flags=0,
        )
        self.connect("startup", self.on_startup)
        self.connect("activate", self.on_activate)

    def on_startup(self, *args):
        provider = Gtk.CssProvider()
        css_path = Path(__file__).parent / "theme" / "style.css"
        provider.load_from_path(str(css_path))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def on_activate(self, *args):
        win = self.props.active_window
        if not win:
            key_manager = KeyManager.get()
            has_identity = key_manager.load_from_keyring()

            if has_identity:
                win = EchoWindow(application=self, key_manager=key_manager)
            else:
                win = OnboardingController()
                win.connect("done", self._on_onboarding_done)

        win.present()

    def _on_onboarding_done(self, controller):
        key_manager = KeyManager.get()
        main_win = EchoWindow(application=self, key_manager=key_manager)
        main_win.present()
