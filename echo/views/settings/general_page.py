import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw
from echo.utils.config import Settings


class GeneralPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.set_margin_start(14)
        self.set_margin_end(14)
        self.set_margin_top(24)

        title = Gtk.Label(label="General")
        title.set_css_classes(["settings-title"])
        title.set_halign(Gtk.Align.START)
        self.append(title)

        settings = Settings.get()
        for label_text, key in [
            ("Open to Following feed", "open-to-following-feed"),
            ("Restore last window state", "restore-last-window-state"),
            ("Confirm before posting", "confirm-before-posting"),
        ]:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            label = Gtk.Label(label=label_text)
            label.set_hexpand(True)
            label.set_halign(Gtk.Align.START)
            switch = Gtk.Switch()
            settings.bind(switch, key)
            row.append(label)
            row.append(switch)
            self.append(row)
