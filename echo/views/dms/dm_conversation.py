import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GLib, GObject
from echo.widgets.avatar import Avatar
from echo.models.dm import DirectMessage


class DMConversationView(Gtk.Box):
    __gsignals__ = {
        "send-message": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "back": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._contact_pubkey = ""
        self._contact_name_str = ""

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header.set_margin_start(16)
        header.set_margin_end(16)
        header.set_margin_top(16)
        header.set_margin_bottom(12)

        back_btn = Gtk.Button(label="‹ Back")
        back_btn.set_halign(Gtk.Align.START)
        back_btn.connect("clicked", lambda _: self.emit("back"))
        header.append(back_btn)

        self._avatar = Avatar(size=32, initials="?")
        header.append(self._avatar)

        self._contact_name = Gtk.Label(label="Contact")
        header.append(self._contact_name)
        self.append(header)

        self._scrolled = Gtk.ScrolledWindow()
        self._scrolled.set_vexpand(True)

        self._messages = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self._messages.set_margin_start(16)
        self._messages.set_margin_end(16)
        self._messages.set_margin_top(8)
        self._scrolled.set_child(self._messages)
        self.append(self._scrolled)

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
        send_btn.add_css_class("suggested-action")
        send_btn.connect("clicked", self._on_send)
        composer.append(self._entry)
        composer.append(send_btn)
        self.append(composer)

    def set_contact(self, name: str, pubkey: str = ""):
        self._contact_pubkey = pubkey
        self._contact_name_str = name or pubkey[:12]
        self._contact_name.set_label(self._contact_name_str)
        initials = name[:2].upper() if name else (pubkey[:2].upper() if pubkey else "?")
        self._avatar._initials = initials[:2].upper() or "?"
        self._avatar.queue_draw()

    def add_message(self, dm: DirectMessage):
        is_sent = dm.is_sent
        text = dm.content
        dt = GLib.DateTime.new_from_unix_utc(dm.created_at)
        time_str = dt.format("%H:%M") or ""

        bubble = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        bubble.set_max_width_chars(50)
        bubble.set_wrap(True)

        label = Gtk.Label(label=text)
        label.set_wrap(True)
        label.set_max_width_chars(50)
        label.set_xalign(0)
        bubble.append(label)

        time_label = Gtk.Label(label=time_str)
        time_label.set_halign(Gtk.Align.END)
        bubble.append(time_label)

        if is_sent:
            bubble.add_css_class("dm-bubble-sent")
            bubble.set_halign(Gtk.Align.END)
        else:
            bubble.add_css_class("dm-bubble-received")
            bubble.set_halign(Gtk.Align.START)

        self._messages.append(bubble)

        GLib.idle_add(self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        adj = self._scrolled.get_vadjustment()
        if adj:
            adj.set_value(adj.get_upper() - adj.get_page_size())

    def clear_messages(self):
        self._messages.remove_all()

    def _on_send(self, _widget):
        text = self._entry.get_text().strip()
        if text:
            self.emit("send-message", text)
            self._entry.set_text("")
