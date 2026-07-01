import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk, Gdk, GObject
from echo.widgets.avatar import Avatar
from echo.views.media.media_view import MediaItem


class MediaLightbox(Adw.Window):
    __gsignals__ = {
        "closed": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, parent, items: list[MediaItem], start_index: int = 0):
        super().__init__(
            transient_for=parent,
            modal=True,
            decorated=False,
            default_width=1200,
            default_height=800,
        )
        self._items = items
        self._current = max(0, min(start_index, len(items) - 1))

        self.set_title("")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.add_css_class("lightbox-root")

        overlay = Gtk.Overlay()
        overlay.set_vexpand(True)
        overlay.set_hexpand(True)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.set_vexpand(True)
        main_box.set_hexpand(True)

        center_area = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        center_area.set_vexpand(True)
        center_area.set_hexpand(True)
        center_area.set_halign(Gtk.Align.CENTER)
        center_area.set_valign(Gtk.Align.CENTER)

        self._image_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._image_frame.set_size_request(620, 460)
        self._image_frame.add_css_class("lightbox-image-frame")

        self._image_placeholder = Gtk.Label(label="")
        self._image_placeholder.set_size_request(620, 460)
        self._image_placeholder.add_css_class("lightbox-image-placeholder")
        self._image_frame.append(self._image_placeholder)
        center_area.append(self._image_frame)
        main_box.append(center_area)

        self._caption_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self._caption_bar.add_css_class("lightbox-caption-bar")
        self._caption_bar.set_hexpand(True)

        self._caption_avatar = Avatar(size=40, initials="?", color="#99BF8C")
        self._caption_bar.append(self._caption_avatar)

        caption_text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        caption_text_box.set_hexpand(True)

        self._caption_name = Gtk.Label(label="")
        self._caption_name.add_css_class("lightbox-caption-name")
        self._caption_name.set_halign(Gtk.Align.START)
        caption_text_box.append(self._caption_name)

        self._caption_content = Gtk.Label(label="")
        self._caption_content.add_css_class("lightbox-caption-content")
        self._caption_content.set_halign(Gtk.Align.START)
        self._caption_content.set_wrap(True)
        self._caption_content.set_max_width_chars(60)
        caption_text_box.append(self._caption_content)

        self._caption_bar.append(caption_text_box)

        self._engagement_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        self._engagement_box.add_css_class("lightbox-engagement")
        self._caption_bar.append(self._engagement_box)

        main_box.append(self._caption_bar)
        overlay.set_child(main_box)

        top_overlay = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        top_overlay.set_halign(Gtk.Align.FILL)
        top_overlay.set_valign(Gtk.Align.START)
        top_overlay.set_margin_top(20)
        top_overlay.set_margin_start(20)
        top_overlay.set_margin_end(20)

        self._counter = Gtk.Label(label="")
        self._counter.add_css_class("lightbox-counter")
        self._counter.set_halign(Gtk.Align.START)
        self._counter.set_hexpand(True)
        top_overlay.append(self._counter)

        close_btn = Gtk.Button(label="✕")
        close_btn.add_css_class("lightbox-close-btn")
        close_btn.set_halign(Gtk.Align.END)
        close_btn.connect("clicked", lambda _: self._close())
        top_overlay.append(close_btn)

        overlay.add_overlay(top_overlay, "north")

        prev_btn = Gtk.Button(label="‹")
        prev_btn.add_css_class("lightbox-nav-btn")
        prev_btn.set_halign(Gtk.Align.START)
        prev_btn.set_valign(Gtk.Align.CENTER)
        prev_btn.set_margin_start(24)
        prev_btn.connect("clicked", lambda _: self._navigate(-1))
        overlay.add_overlay(prev_btn)

        next_btn = Gtk.Button(label="›")
        next_btn.add_css_class("lightbox-nav-btn")
        next_btn.set_halign(Gtk.Align.END)
        next_btn.set_valign(Gtk.Align.CENTER)
        next_btn.set_margin_end(24)
        next_btn.connect("clicked", lambda _: self._navigate(1))
        overlay.add_overlay(next_btn)

        box.append(overlay)

        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        box.add_controller(key_controller)

        self.set_content(box)
        self._update()

    def _update(self):
        if not self._items:
            self._close()
            return
        item = self._items[self._current]
        total = len(self._items)
        self._counter.set_text(f"{self._current + 1} / {total}")

        name = item.note_content[:50] + ("…" if len(item.note_content) > 50 else "")
        self._caption_name.set_text(name)
        self._caption_content.set_text(item.note_content)

        child = self._engagement_box.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self._engagement_box.remove(child)
            child = nxt

        eng_labels = [
            f"↩ {item.reply_count}",
            f"⟲ {item.repost_count}",
            f"♥ {item.like_count}",
        ]
        for text in eng_labels:
            lbl = Gtk.Label(label=text)
            lbl.add_css_class("lightbox-eng-item")
            self._engagement_box.append(lbl)
        zap_text = f"⚡ {item.zap_amount or item.zap_count}"
        zap_lbl = Gtk.Label(label=zap_text)
        zap_lbl.add_css_class("lightbox-zap-item")
        self._engagement_box.append(zap_lbl)

    def _navigate(self, direction: int):
        new_index = self._current + direction
        if 0 <= new_index < len(self._items):
            self._current = new_index
            self._update()

    def _close(self):
        self.emit("closed")
        self.close()

    def _on_key_pressed(self, _controller, keyval, _code, _state):
        if keyval == Gdk.KEY_Escape:
            self._close()
            return True
        elif keyval == Gdk.KEY_Left:
            self._navigate(-1)
            return True
        elif keyval == Gdk.KEY_Right:
            self._navigate(1)
            return True
        return False
