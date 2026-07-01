import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject


class DMListView(Gtk.Box):
    __gsignals__ = {
        "conversation-selected": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "new-conversation": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        header.set_margin_start(16)
        header.set_margin_end(16)
        header.set_margin_top(16)
        header.set_margin_bottom(12)

        title = Gtk.Label(label="Direct Messages")
        title.set_halign(Gtk.Align.START)
        title.set_hexpand(True)

        compose_btn = Gtk.Button(label="✎")
        compose_btn.set_tooltip_text("New conversation")
        compose_btn.connect("clicked", lambda _: self.emit("new-conversation"))
        header.append(title)
        header.append(compose_btn)
        self.append(header)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        self._list = Gtk.ListBox()
        self._list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._list.connect("row-activated", self._on_row_activated)
        scrolled.set_child(self._list)
        self.append(scrolled)

        self._empty_state = Gtk.Label(label="No conversations yet.\nStart one by clicking the compose button.")
        self._empty_state.set_halign(Gtk.Align.CENTER)
        self._empty_state.set_valign(Gtk.Align.CENTER)
        self._empty_state.set_margin_top(48)
        self._empty_state.set_visible(False)
        self.append(self._empty_state)

    def add_conversation(self, conv_row, pubkey: str = ""):
        conv_row._conv_pubkey = pubkey
        self._list.append(conv_row)
        self._update_state()

    def _on_row_activated(self, listbox, row):
        pubkey = getattr(row, "_conv_pubkey", "")
        self.emit("conversation-selected", pubkey)

    def _update_state(self):
        has_items = self._list.get_first_child() is not None
        self._empty_state.set_visible(not has_items)
        self._list.set_visible(has_items)
