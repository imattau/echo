import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject
from echo.widgets.note_card import NoteCard


class ThreadView(Gtk.Box):
    __gsignals__ = {
        "back": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._root_note = None

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        header.set_margin_start(16)
        header.set_margin_end(16)
        header.set_margin_top(16)
        header.set_margin_bottom(12)

        back_btn = Gtk.Button(label="‹ Back")
        back_btn.set_halign(Gtk.Align.START)
        back_btn.connect("clicked", lambda _: self.emit("back"))
        header.append(back_btn)

        self._breadcrumb = Gtk.Label(label="Home > Thread")
        self._breadcrumb.set_hexpand(True)
        self._breadcrumb.set_margin_start(12)
        header.append(self._breadcrumb)
        self.append(header)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        self._content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self._content.set_margin_start(16)
        self._content.set_margin_end(16)
        scrolled.set_child(self._content)
        self.append(scrolled)

        composer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        composer_box.set_margin_start(16)
        composer_box.set_margin_end(16)
        composer_box.set_margin_top(8)
        composer_box.set_margin_bottom(8)

        self._reply_entry = Gtk.Entry()
        self._reply_entry.set_hexpand(True)
        self._reply_entry.set_placeholder_text("Write a reply...")
        self._reply_entry.connect("activate", self._on_send_reply)
        composer_box.append(self._reply_entry)

        send_btn = Gtk.Button(label="Reply")
        send_btn.add_css_class("suggested-action")
        send_btn.connect("clicked", self._on_send_reply)
        composer_box.append(send_btn)

        self.append(composer_box)

    def set_root_note(self, note):
        self._root_note = note
        self._content.remove_all()
        card = NoteCard(note)
        self._content.append(card)
        profile = note.profile
        handle = profile.handle if profile else note.pubkey[:8]
        self._breadcrumb.set_label(f"Home > Thread by {handle}")

    def add_reply(self, note_card):
        self._content.append(note_card)

    def _on_send_reply(self, _widget):
        text = self._reply_entry.get_text().strip()
        if text:
            self._reply_entry.set_text("")
