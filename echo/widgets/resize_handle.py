import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


class ResizeHandle(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.set_size_request(6, -1)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.add_css_class("resize-handle")

        for _ in range(3):
            dot = Gtk.DrawingArea()
            dot.set_size_request(3, 3)
            dot.add_css_class("resize-dot")
            self.append(dot)
