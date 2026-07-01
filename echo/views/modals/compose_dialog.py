import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject


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
        post_btn = Gtk.Button(label="Post")
        post_btn.add_css_class("suggested-action")
        post_btn.connect("clicked", self._on_post)
        actions.append(post_btn)
        content.append(actions)

        self.set_content(content)

    def _on_post(self, _btn):
        buffer = self._text_view.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
        if text.strip():
            self.emit("submit", text.strip())
            self.close()
