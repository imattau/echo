from dataclasses import dataclass

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject
from echo.widgets.media_widgets import MediaThumbnail


@dataclass
class MediaItem:
    url: str
    media_type: str
    note_id: str
    note_content: str
    pubkey: str
    reply_count: int = 0
    repost_count: int = 0
    like_count: int = 0
    zap_count: int = 0
    zap_amount: int = 0
    duration: str = ""


class MediaView(Gtk.Box):
    __gsignals__ = {
        "refresh": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "open-media": (GObject.SignalFlags.RUN_FIRST, None, (object, int)),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)

        self._items: list[MediaItem] = []
        self._active_filter = "all"

        self._build_header()
        self._build_filter_tabs()
        self._build_spinner()
        self._build_empty_state()
        self._build_grid()

    def _build_header(self):
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        header.set_margin_start(28)
        header.set_margin_end(28)
        header.set_margin_top(20)

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title_box.set_hexpand(True)

        self._title = Gtk.Label(label="Media")
        self._title.add_css_class("media-header-title")
        self._title.set_halign(Gtk.Align.START)
        title_box.append(self._title)

        self._count_label = Gtk.Label(label="0 items")
        self._count_label.add_css_class("media-header-count")
        self._count_label.set_halign(Gtk.Align.START)
        title_box.append(self._count_label)

        header.append(title_box)
        self.append(header)

    def _build_filter_tabs(self):
        tabs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        tabs.set_margin_start(28)
        tabs.set_margin_end(28)

        self._filter_buttons = {}
        for name in ("all", "photos", "videos"):
            btn = Gtk.Button(label=name.capitalize())
            btn.add_css_class("filter-pill")
            if name == "all":
                btn.add_css_class("filter-pill-active")
            btn.connect("clicked", self._on_filter_clicked, name)
            tabs.append(btn)
            self._filter_buttons[name] = btn

        self.append(tabs)

    def _build_spinner(self):
        self._spinner = Gtk.Spinner()
        self._spinner.set_halign(Gtk.Align.CENTER)
        self._spinner.set_valign(Gtk.Align.CENTER)
        self._spinner.set_margin_top(48)
        self._spinner.set_visible(False)
        self.append(self._spinner)

    def _build_empty_state(self):
        self._empty_state = Gtk.Label(
            label="No media found. Pull in more notes from your relays to see media content here."
        )
        self._empty_state.set_halign(Gtk.Align.CENTER)
        self._empty_state.set_valign(Gtk.Align.CENTER)
        self._empty_state.set_margin_top(48)
        self._empty_state.add_css_class("media-empty-state")
        self._empty_state.set_visible(False)
        self.append(self._empty_state)

    def _build_grid(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        self._flowbox = Gtk.FlowBox()
        self._flowbox.set_max_children_per_line(4)
        self._flowbox.set_min_children_per_line(1)
        self._flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self._flowbox.set_column_spacing(10)
        self._flowbox.set_row_spacing(10)
        self._flowbox.set_margin_start(28)
        self._flowbox.set_margin_end(28)
        self._flowbox.set_margin_top(4)
        self._flowbox.set_margin_bottom(28)

        scrolled.set_child(self._flowbox)
        self.append(scrolled)

    def add_media_item(self, item: MediaItem):
        if self._active_filter == "photos" and item.media_type != "image":
            return
        if self._active_filter == "videos" and item.media_type != "video":
            return
        self._items.append(item)
        thumb = MediaThumbnail(
            media_index=len(self._items) - 1,
            url=item.url,
            media_type=item.media_type,
            has_multi=False,
            duration=item.duration,
        )
        thumb.connect("clicked", self._on_thumb_clicked)
        self._flowbox.append(thumb)
        self._update_state()

    def clear(self):
        self._items.clear()
        row = self._flowbox.get_first_child()
        while row:
            next_row = row.get_next_sibling()
            self._flowbox.remove(row)
            row = next_row
        self._update_state()

    def show_loading(self, loading: bool):
        self._spinner.set_visible(loading)
        if loading:
            self._spinner.start()
        else:
            self._spinner.stop()
        self._update_state()

    def set_filter(self, filter_name: str):
        self._active_filter = filter_name
        for name, btn in self._filter_buttons.items():
            if name == filter_name:
                btn.add_css_class("filter-pill-active")
            else:
                btn.remove_css_class("filter-pill-active")
        self._apply_filter()

    def _apply_filter(self):
        items = list(self._items)
        self.clear()
        self._items = items
        for item in self._items:
            if self._active_filter == "photos" and item.media_type != "image":
                continue
            if self._active_filter == "videos" and item.media_type != "video":
                continue
            thumb = MediaThumbnail(
                media_index=len([i for i in self._items if i is item]),
                url=item.url,
                media_type=item.media_type,
                has_multi=False,
                duration=item.duration,
            )
            thumb.connect("clicked", self._on_thumb_clicked)
            self._flowbox.append(thumb)
        self._update_state()

    def _on_filter_clicked(self, _btn, filter_name: str):
        self.set_filter(filter_name)

    def _on_thumb_clicked(self, _thumb, index: int):
        self.emit("open-media", self._items, index)

    def _update_state(self):
        count = 0
        child = self._flowbox.get_first_child()
        while child:
            count += 1
            child = child.get_next_sibling()

        self._count_label.set_text(f"{count} items")
        self._empty_state.set_visible(count == 0 and not self._spinner.get_visible())
        self._flowbox.set_visible(count > 0)
