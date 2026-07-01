import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject
from echo.widgets.avatar import Avatar


class DMConversationView(Gtk.Box):
    __gsignals__ = {
        "send-message": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header.set_margin_start(16)
        header.set_margin_end(16)
        header.set_margin_top(16)
        header.set_margin_bottom(12)

        avatar = Avatar(size=32, initials="?")
        header.append(avatar)

        self._contact_name = Gtk.Label(label="Contact")
        header.append(self._contact_name)
        self.append(header)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        self._messages = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self._messages.set_margin_start(16)
        self._messages.set_margin_end(16)
        scrolled.set_child(self._messages)
        self.append(scrolled)

        composer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        composer.set_margin_start(16)
        composer.set_margin_end(16)
        composer.set_margin_top(8)
        composer.set_margin_bottom(8)

        self._entry = Gtk.Entry()
        self._entry.set_hexpand(True)
        self._entry.set_placeholder_text("Write a message...")
        self._entry.connect("activate", self._on_send)
        send_btn = Gtk.Button(label="Send")
        send_btn.connect("clicked", self._on_send)
        composer.append(self._entry)
        composer.append(send_btn)
        self.append(composer)

    def _on_send(self, _widget):
        text = self._entry.get_text().strip()
        if text:
            self.emit("send-message", text)
            self._entry.set_text("")
