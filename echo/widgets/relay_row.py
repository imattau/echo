import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject
from .relay_chip import RelayChip


class RelayRow(Gtk.Box):
    __gsignals__ = {
        "menu": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, url="", latency="", status="disconnected", read=True, write=True):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.set_margin_start(14)
        self.set_margin_end(14)
        self.set_margin_top(12)
        self.set_margin_bottom(12)

        status_str = status.name.lower() if hasattr(status, "name") else str(status).lower()

        status_dot = Gtk.DrawingArea()
        status_dot.set_size_request(9, 9)
        status_dot.add_css_class("status-dot")
        status_dot.add_css_class(f"status-{status_str}")
        self.append(status_dot)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        url_label = Gtk.Label(label=url)
        url_label.set_halign(Gtk.Align.START)
        latency_label = Gtk.Label(label=latency)
        latency_label.set_halign(Gtk.Align.START)
        info.append(url_label)
        info.append(latency_label)
        self.append(info)

        if read:
            self.append(RelayChip("READ"))
        if write:
            self.append(RelayChip("WRITE"))

        menu_btn = Gtk.Button(label="⋯")
        menu_btn.connect("clicked", lambda _: self.emit("menu"))
        self.append(menu_btn)
