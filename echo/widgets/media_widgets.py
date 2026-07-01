import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


class VideoOverlay(Gtk.Box):
    def __init__(self, width=296, height=140, duration="1:12"):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_size_request(width, height)
        self.add_css_class("video-overlay")
        self.set_halign(Gtk.Align.CENTER)

        center = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        center.set_halign(Gtk.Align.CENTER)
        center.set_valign(Gtk.Align.CENTER)
        center.set_hexpand(True)
        center.set_vexpand(True)

        play_btn = Gtk.DrawingArea()
        play_btn.set_size_request(48, 48)
        center.append(play_btn)

        self.append(center)

        bottom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        bottom.set_halign(Gtk.Align.END)
        bottom.set_valign(Gtk.Align.END)
        bottom.set_margin_end(8)
        bottom.set_margin_bottom(8)

        badge = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        badge.add_css_class("duration-badge")
        duration_lbl = Gtk.Label(label=duration)
        badge.append(duration_lbl)
        bottom.append(badge)

        self.append(bottom)


class ImagePlaceholder(Gtk.Box):
    def __init__(self, width=296, height=140):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_size_request(width, height)
        self.add_css_class("image-placeholder")
        self.set_halign(Gtk.Align.CENTER)
