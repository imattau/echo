import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject
from echo.utils.config import Config


class ComposeDialog(Adw.Window):
    __gsignals__ = {
        "submit": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self, parent):
        super().__init__(transient_for=parent, modal=True)
        self.set_title("New Note")
        self.set_default_size(560, 400)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content.set_margin_start(16)
        content.set_margin_end(16)
        content.set_margin_top(16)
        content.set_margin_bottom(16)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        title = Gtk.Label(label="New Note")
        title.set_hexpand(True)
        close_btn = Gtk.Button(label="✕")
        close_btn.connect("clicked", lambda _: self.close())
        header.append(title)
        header.append(close_btn)
        content.append(header)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        self._text_view = Gtk.TextView()
        self._text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._text_view.set_placeholder_text("What's happening on the network?")
        scrolled.set_child(self._text_view)
        content.append(scrolled)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self._counter = Gtk.Label(label=f"0/{Config.MAX_NOTE_LENGTH}")
        self._counter.set_halign(Gtk.Align.START)
        self._counter.set_hexpand(True)
        actions.append(self._counter)

        self._post_btn = Gtk.Button(label="Post")
        self._post_btn.add_css_class("suggested-action")
        self._post_btn.set_sensitive(False)
        self._post_btn.connect("clicked", self._on_post)
        actions.append(self._post_btn)

        content.append(actions)

        self.set_content(content)

        buffer = self._text_view.get_buffer()
        buffer.connect("changed", self._on_buffer_changed)

    def _on_buffer_changed(self, buffer):
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        length = end.get_offset() - start.get_offset()
        over = length > Config.MAX_NOTE_LENGTH
        self._counter.set_label(f"{length}/{Config.MAX_NOTE_LENGTH}")
        if over:
            self._counter.set_css_classes(["count-over"])
        else:
            self._counter.set_css_classes([])
        self._post_btn.set_sensitive(not over and length > 0)

    def _on_post(self, _btn):
        buffer = self._text_view.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
        if text.strip():
            self.emit("submit", text.strip())
            self.close()
