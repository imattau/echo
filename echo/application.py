import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, Gtk, Gdk
from .window import EchoWindow
from pathlib import Path


class EchoApplication(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.echo.nostr",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
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
            win = EchoWindow(application=self)
        win.present()
