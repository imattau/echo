import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, cairo
from math import pi


class Avatar(Gtk.DrawingArea):
    def __init__(self, size: int = 40, initials: str = "", color: str = "#99BF8C"):
        super().__init__()
        self.set_size_request(size, size)
        self._initials = initials[:2].upper() or "?"
        self._color = color
        self._size = size
        self.set_draw_func(self._draw)

    def _draw(self, area: Gtk.DrawingArea, cr: cairo.Context, w: int, h: int):
        r = int(self._color[1:3], 16) / 255
        g = int(self._color[3:5], 16) / 255
        b = int(self._color[5:7], 16) / 255

        cr.arc(w / 2, h / 2, w / 2, 0, 2 * pi)
        cr.set_source_rgb(r, g, b)
        cr.fill()

        cr.set_source_rgb(1, 1, 1)
        cr.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(self._size * 0.4)
        extents = cr.text_extents(self._initials)
        cr.move_to(
            (w - extents.width) / 2,
            (h + extents.height) / 2,
        )
        cr.show_text(self._initials)
