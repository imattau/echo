import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject


class BookmarksView(Gtk.Box):
    __gsignals__ = {
        "load": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        header.set_margin_start(16)
        header.set_margin_end(16)
        header.set_margin_top(16)
        header.set_margin_bottom(12)

        self._title = Gtk.Label(label="Bookmarks")
        self._title.set_halign(Gtk.Align.START)
        self._title.set_hexpand(True)

        self._sort_btn = Gtk.Button(label="Newest")
        self._sort_btn.connect("clicked", self._on_sort_toggle)
        header.append(self._title)
        header.append(self._sort_btn)
        self.append(header)

        self._spinner = Gtk.Spinner()
        self._spinner.set_halign(Gtk.Align.CENTER)
        self._spinner.set_valign(Gtk.Align.CENTER)
        self._spinner.set_margin_top(48)
        self._spinner.set_visible(False)
        self.append(self._spinner)

        self._empty_state = Gtk.Label(label="No bookmarks yet.\nBookmark notes from the feed to see them here.")
        self._empty_state.set_halign(Gtk.Align.CENTER)
        self._empty_state.set_valign(Gtk.Align.CENTER)
        self._empty_state.set_margin_top(48)
        self._empty_state.set_visible(True)
        self.append(self._empty_state)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        self._list = Gtk.ListBox()
        self._list.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.set_child(self._list)
        self.append(scrolled)

        self._sort_ascending = False

    def add_bookmark(self, note_card):
        self._list.append(note_card)
        self._update_state()

    def clear(self):
        row = self._list.get_first_child()
        while row:
            next_row = row.get_next_sibling()
            self._list.remove(row)
            row = next_row
        self._update_state()

    def show_loading(self, loading: bool):
        self._spinner.set_visible(loading)
        if loading:
            self._spinner.start()
        else:
            self._spinner.stop()
        self._update_state()

    def _update_state(self):
        has_items = self._list.get_first_child() is not None
        is_loading = self._spinner.get_visible()
        self._list.set_visible(has_items)
        self._empty_state.set_visible(not has_items and not is_loading)

    def _on_sort_toggle(self, _btn):
        self._sort_ascending = not self._sort_ascending
        self._sort_btn.set_label("Oldest" if self._sort_ascending else "Newest")
        self.emit("load")