import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk, Gdk
from math import pi


class Avatar(Gtk.DrawingArea):
    def __init__(self, size: int = 40, initials: str = "", color: str = "#99BF8C"):
        super().__init__()
        self.set_size_request(size, size)
        self._initials = initials[:2].upper() or "?"
        self._size = size
        self._font_size = size * 0.4

        rgba = Gdk.RGBA()
        if not rgba.parse(color):
            rgba.parse("#99BF8C")
        self._red = rgba.red
        self._green = rgba.green
        self._blue = rgba.blue

        self.set_draw_func(self._draw)

    def _draw(self, area: Gtk.DrawingArea, cr, w: int, h: int):
        cr.arc(w / 2, h / 2, w / 2, 0, 2 * pi)
        cr.set_source_rgb(self._red, self._green, self._blue)
        cr.fill()

        cr.set_source_rgb(1, 1, 1)
        cr.set_font_size(self._font_size)
        extents = cr.text_extents(self._initials)
        cr.move_to(
            (w - extents.width) / 2,
            (h + extents.height) / 2,
        )
        cr.show_text(self._initials)
