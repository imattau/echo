import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


class FeedView(Gtk.Box):
    __gsignals__ = {
        "refresh": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, title_text="Home"):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        header.set_margin_start(16)
        header.set_margin_end(16)
        header.set_margin_top(16)
        header.set_margin_bottom(12)

        title = Gtk.Label(label=title_text)
        title.set_halign(Gtk.Align.START)
        title.set_hexpand(True)

        refresh_btn = Gtk.Button(label="↻")
        refresh_btn.connect("clicked", lambda _: self.emit("refresh"))
        header.append(title)
        header.append(refresh_btn)
        self.append(header)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        self._note_list = Gtk.ListBox()
        self._note_list.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.set_child(self._note_list)
        self.append(scrolled)

    def add_note(self, note_card):
        self._note_list.append(note_card)
