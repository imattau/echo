import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject
from echo.widgets.hashtag_pill import HashtagPill


class DiscoverView(Gtk.Box):
    __gsignals__ = {
        "search": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "trending-tag": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)

        self._search_entry = Gtk.SearchEntry()
        self._search_entry.set_property("placeholder-text", "Search notes, people, or nostr addresses")
        self._search_entry.set_margin_start(16)
        self._search_entry.set_margin_end(16)
        self._search_entry.set_margin_top(16)
        self._search_entry.connect("activate", self._on_search)
        self.append(self._search_entry)

        trending = Gtk.FlowBox()
        trending.set_max_children_per_line(6)
        trending.set_selection_mode(Gtk.SelectionMode.NONE)
        trending.set_margin_start(16)
        trending.set_margin_end(16)

        for tag in ["nostr", "lightning", "music", "bitcoin", "design"]:
            pill = HashtagPill(hashtag=tag)
            pill.connect("selected", self._on_trending_selected)
            trending.append(pill)

        self._trending_header = trending
        self.append(trending)

        self._spinner = Gtk.Spinner()
        self._spinner.set_halign(Gtk.Align.CENTER)
        self._spinner.set_valign(Gtk.Align.CENTER)
        self._spinner.set_margin_top(48)
        self._spinner.set_visible(False)
        self.append(self._spinner)

        self._empty_state = Gtk.Label(label="Use the search bar or click a trending tag to find content.")
        self._empty_state.set_halign(Gtk.Align.CENTER)
        self._empty_state.set_valign(Gtk.Align.CENTER)
        self._empty_state.set_margin_top(48)
        self._empty_state.set_visible(True)
        self.append(self._empty_state)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        self._grid = Gtk.Grid()
        scrolled.set_child(self._grid)
        self.append(scrolled)

    def add_result(self, note_card):
        self._grid.append(note_card)
        self._update_state()

    def clear_results(self):
        row = self._grid.get_first_child()
        while row:
            next_row = row.get_next_sibling()
            self._grid.remove(row)
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
        has_results = self._grid.get_first_child() is not None
        is_loading = self._spinner.get_visible()
        self._grid.set_visible(has_results)
        self._empty_state.set_visible(not has_results and not is_loading)

    def _on_search(self, *args):
        query = self._search_entry.get_text()
        if query.strip():
            self.clear_results()
            self.emit("search", query.strip())

    def _on_trending_selected(self, pill, tag: str):
        self.clear_results()
        self._search_entry.set_text(tag)
        self.emit("trending-tag", tag)
