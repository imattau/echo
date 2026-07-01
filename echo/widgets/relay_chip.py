import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


class RelayChip(Gtk.Box):
    def __init__(self, label: str = "READ"):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.add_css_class("relay-chip")

        text = Gtk.Label(label=label)
        text.set_css_classes(["relay-chip-text"])
        self.append(text)
