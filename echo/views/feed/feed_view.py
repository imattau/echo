import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject
from .note_list import NoteList


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
        refresh_btn.set_tooltip_text("Refresh feed")
        refresh_btn.connect("clicked", lambda _: self.emit("refresh"))
        header.append(title)
        header.append(refresh_btn)
        self.append(header)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        self._note_list = NoteList()
        scrolled.set_child(self._note_list)
        self.append(scrolled)

        self._empty_state = Gtk.Label(label="No notes yet.\nConnect relays and refresh to load your feed.")
        self._empty_state.set_halign(Gtk.Align.CENTER)
        self._empty_state.set_valign(Gtk.Align.CENTER)
        self._empty_state.set_margin_top(48)
        self._empty_state.set_visible(False)
        self.append(self._empty_state)

        self._spinner = Gtk.Spinner()
        self._spinner.set_halign(Gtk.Align.CENTER)
        self._spinner.set_valign(Gtk.Align.CENTER)
        self._spinner.set_margin_top(48)
        self._spinner.set_visible(False)
        self.append(self._spinner)

    def add_note(self, note_card):
        self._note_list.add_note(note_card)
        self._update_state()

    def clear(self):
        self._note_list.clear()
        self._update_state()

    def show_loading(self, loading=True):
        self._spinner.set_visible(loading)
        if loading:
            self._spinner.start()
        else:
            self._spinner.stop()
        self._update_state()

    def _update_state(self):
        has_notes = self._note_list.get_first_child() is not None
        self._empty_state.set_visible(not has_notes and not self._spinner.get_visible())
        self._note_list.set_visible(has_notes)
