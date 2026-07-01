import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


class DiscoverView(Gtk.Box):
    __gsignals__ = {
        "search": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "trending-tag": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)

        self._search_entry = Gtk.SearchEntry()
        self._search_entry.set_placeholder_text("Search notes, people, or nostr addresses")
        self._search_entry.set_margin_start(16)
        self._search_entry.set_margin_end(16)
        self._search_entry.set_margin_top(16)
        self._search_entry.connect("search-changed", self._on_search)
        self._search_entry.connect("activate", self._on_search)
        self.append(self._search_entry)

        trending = Gtk.FlowBox()
        trending.set_max_children_per_line(6)
        trending.set_selection_mode(Gtk.SelectionMode.NONE)
        trending.set_margin_start(16)
        trending.set_margin_end(16)

        for tag in ["#nostr", "#lightning", "#music", "#bitcoin", "#design"]:
            pill = Gtk.Button(label=tag)
            pill.add_css_class("trending-pill")
            pill.connect("clicked", self._on_trending_click, tag)
            trending.append(pill)

        self.append(trending)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        self._grid = Gtk.Grid()
        scrolled.set_child(self._grid)
        self.append(scrolled)

    def _on_search(self, *args):
        query = self._search_entry.get_text()
        if query.strip():
            self.emit("search", query.strip())

    def _on_trending_click(self, btn, tag: str):
        self.emit("trending-tag", tag)
