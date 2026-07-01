import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject
from echo.utils.config import Config


class Composer(Gtk.Box):
    __gsignals__ = {
        "submit": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        self._text_view = Gtk.TextView()
        self._text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self._text_view.set_placeholder_text("What's happening on the network?")

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self._text_view)
        scrolled.set_vexpand(True)
        self.append(scrolled)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self._counter = Gtk.Label(label=f"0/{Config.MAX_NOTE_LENGTH}")
        self._counter.set_halign(Gtk.Align.START)
        self._counter.set_hexpand(True)
        actions.append(self._counter)

        post_btn = Gtk.Button(label="Post")
        post_btn.add_css_class("suggested-action")
        post_btn.connect("clicked", self._on_post)
        actions.append(post_btn)
        self.append(actions)

        buffer = self._text_view.get_buffer()
        buffer.connect("changed", self._on_buffer_changed)

    def _on_buffer_changed(self, buffer):
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        length = end.get_offset() - start.get_offset()
        self._counter.set_label(f"{length}/{Config.MAX_NOTE_LENGTH}")

    def _on_post(self, _btn):
        buffer = self._text_view.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
        if text.strip():
            self.emit("submit", text.strip())
            buffer.set_text("", -1)
