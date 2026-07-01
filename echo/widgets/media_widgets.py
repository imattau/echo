import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


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

        play_btn = Gtk.Image.new_from_icon_name("media-playback-start-symbolic")
        play_btn.set_pixel_size(48)
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


class MediaThumbnail(Gtk.Box):
    __gsignals__ = {
        "clicked": (GObject.SignalFlags.RUN_FIRST, None, (int,)),
    }

    THUMB_SIZE = 208
    PALETTE = ["#CCDBF0", "#292E38", "#E5D9C7", "#D9E5D1"]

    def __init__(self, media_index: int, url: str, media_type: str = "image",
                 has_multi: bool = False, duration: str = ""):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._index = media_index
        self._url = url
        self._media_type = media_type
        self._has_multi = has_multi
        self._duration = duration

        self.set_size_request(self.THUMB_SIZE, self.THUMB_SIZE)
        self.add_css_class("media-thumbnail")

        color = self.PALETTE[media_index % len(self.PALETTE)]
        self._bg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._bg.set_size_request(self.THUMB_SIZE, self.THUMB_SIZE)
        self._bg.add_css_class("media-thumbnail-bg")
        ctx = self._bg.get_style_context()
        if media_type == "video":
            ctx.add_class("media-thumbnail-video")
        else:
            ctx.add_class("media-thumbnail-image")
        self._bg.set_halign(Gtk.Align.FILL)
        self._bg.set_valign(Gtk.Align.FILL)

        if media_type == "video":
            center = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            center.set_halign(Gtk.Align.CENTER)
            center.set_valign(Gtk.Align.CENTER)
            center.set_hexpand(True)
            center.set_vexpand(True)
            play_btn = Gtk.Image.new_from_icon_name("media-playback-start-symbolic")
            play_btn.set_pixel_size(36)
            center.append(play_btn)
            self._bg.append(center)

            bottom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
            bottom.set_halign(Gtk.Align.END)
            bottom.set_valign(Gtk.Align.END)
            bottom.set_margin_end(8)
            bottom.set_margin_bottom(8)
            badge = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            badge.add_css_class("duration-badge")
            dur_lbl = Gtk.Label(label=duration or "0:00")
            badge.append(dur_lbl)
            bottom.append(badge)
            self._bg.append(bottom)

        if has_multi:
            multi_badge = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
            multi_badge.add_css_class("multi-badge")
            multi_badge.set_halign(Gtk.Align.START)
            multi_badge.set_valign(Gtk.Align.START)
            multi_badge.set_margin_start(8)
            multi_badge.set_margin_top(8)
            icon = Gtk.Image.new_from_icon_name("media-playlist-repeat-symbolic")
            icon.set_pixel_size(12)
            multi_badge.append(icon)
            self._bg.append(multi_badge)

        self.append(self._bg)

        gesture = Gtk.GestureClick()
        gesture.connect("pressed", lambda _g, _n, _x, _y: self.emit("clicked", self._index))
        self.add_controller(gesture)
