import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gio", "2.0")

from gi.repository import Gtk, Gio, GObject, GLib
from echo.models import Profile
from echo.widgets.contact_row import ContactRow


class ContactsView(Gtk.Box):
    __gsignals__ = {
        "load": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "add-contact": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "follow": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "unfollow": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "mute": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "unmute": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "block": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "unblock": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    FILTER_ALL = "all"
    FILTER_MUTED = "muted"
    FILTER_BLOCKED = "blocked"

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        self._contacts: list[Profile] = []
        self._muted: set[str] = set()
        self._blocked: set[str] = set()
        self._following: set[str] = set()
        self._follows_you: set[str] = set()
        self._active_filter = self.FILTER_ALL
        self._search_query = ""
        self._needs_render = False
        self._render_source_id = 0

        self._build_nav_panel()
        self._build_content()

    def _build_nav_panel(self):
        nav = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        nav.set_size_request(200, -1)
        nav.add_css_class("contacts-nav-panel")

        header = Gtk.Label(label="CONTACTS")
        header.add_css_class("contacts-nav-header")
        header.set_halign(Gtk.Align.START)
        header.set_margin_start(10)
        header.set_margin_top(20)
        header.set_margin_bottom(6)
        nav.append(header)

        self._nav_list = Gtk.ListBox()
        self._nav_list.set_selection_mode(Gtk.SelectionMode.NONE)

        self._nav_items = {}
        for key, label, count_getter in [
            (self.FILTER_ALL, "All Contacts", lambda: len(self._contacts)),
            (self.FILTER_MUTED, "Muted", lambda: len(self._muted)),
            (self.FILTER_BLOCKED, "Blocked", lambda: len(self._blocked)),
        ]:
            row = self._build_nav_item(key, label, count_getter)
            self._nav_list.append(row)
            self._nav_items[key] = row

        nav.append(self._nav_list)

        spacer = Gtk.Label()
        spacer.set_vexpand(True)
        nav.append(spacer)

        self.append(nav)

        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.append(separator)

    def _build_nav_item(self, key: str, label: str, count_getter) -> Gtk.Box:
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(8)
        box.set_margin_bottom(8)

        label_widget = Gtk.Label(label=label)
        label_widget.set_hexpand(True)
        label_widget.set_halign(Gtk.Align.START)
        label_widget.add_css_class("contacts-nav-item-text")
        box.append(label_widget)

        count_label = Gtk.Label(label="0")
        count_label.add_css_class("contacts-nav-count")
        box.append(count_label)

        gesture = Gtk.GestureClick()
        gesture.connect("pressed", lambda _g, _n, _x, _y, k=key: self._on_nav_selected(k))
        box.add_controller(gesture)

        if key == self.FILTER_ALL:
            box.add_css_class("contacts-nav-active")

        box._count_label = count_label
        box._count_getter = count_getter
        return box

    def _build_content(self):
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content.set_hexpand(True)
        content.set_vexpand(True)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        header.set_margin_start(32)
        header.set_margin_end(32)
        header.set_margin_top(24)
        header.set_margin_bottom(16)

        self._title_label = Gtk.Label(label="All Contacts")
        self._title_label.add_css_class("contacts-title")
        self._title_label.set_halign(Gtk.Align.START)
        self._title_label.set_hexpand(True)
        header.append(self._title_label)

        add_btn = Gtk.Button(label="＋ Add Contact")
        add_btn.add_css_class("primary-button")
        add_btn.connect("clicked", lambda _: self.emit("add-contact"))
        header.append(add_btn)
        content.append(header)

        search = Gtk.SearchEntry()
        search.set_property("placeholder-text", "Search contacts by name or npub")
        search.set_margin_start(32)
        search.set_margin_end(32)
        search.set_margin_bottom(16)
        search.add_css_class("contacts-search")
        search.connect("search-changed", self._on_search_changed)
        self._search_entry = search
        content.append(search)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._list_box = Gtk.ListBox()
        self._list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self._list_box.add_css_class("contacts-list")

        scrolled.set_child(self._list_box)

        self._empty_state = Gtk.Label(label="No contacts found")
        self._empty_state.set_halign(Gtk.Align.CENTER)
        self._empty_state.set_valign(Gtk.Align.CENTER)
        self._empty_state.set_vexpand(True)
        self._empty_state.set_margin_top(48)
        self._empty_state.add_css_class("contacts-empty")

        content.append(scrolled)
        content.append(self._empty_state)

        self._loading = Gtk.Spinner()
        self._loading.set_halign(Gtk.Align.CENTER)
        self._loading.set_valign(Gtk.Align.CENTER)
        self._loading.set_size_request(32, 32)
        self._loading.set_margin_top(48)
        content.append(self._loading)

        self.append(content)

    def _on_nav_selected(self, key: str):
        self._active_filter = key
        for k, row in self._nav_items.items():
            css = row.get_css_classes()
            if k == key:
                if "contacts-nav-active" not in css:
                    row.add_css_class("contacts-nav-active")
            else:
                if "contacts-nav-active" in css:
                    row.remove_css_class("contacts-nav-active")
        label_map = {
            self.FILTER_ALL: "All Contacts",
            self.FILTER_MUTED: "Muted",
            self.FILTER_BLOCKED: "Blocked",
        }
        self._title_label.set_text(label_map.get(key, "Contacts"))
        self._render_contacts()

    def _on_search_changed(self, entry: Gtk.SearchEntry):
        self._search_query = entry.get_text().strip().lower()
        self._render_contacts()

    def _schedule_render(self):
        self._needs_render = True
        if self._render_source_id > 0:
            return
        self._render_source_id = GLib.timeout_add(0, self._do_render)

    def _do_render(self) -> bool:
        self._render_source_id = 0
        if not self._needs_render:
            return False
        self._needs_render = False
        self._render_contacts()
        return False

    def _render_contacts(self):
        while child := self._list_box.get_first_child():
            self._list_box.remove(child)

        filtered = self._get_filtered_contacts()

        for profile in filtered:
            is_following = profile.pubkey in self._following
            is_muted = profile.pubkey in self._muted
            follows_you = profile.pubkey in self._follows_you

            row = ContactRow(
                profile=profile,
                is_following=is_following,
                is_muted=is_muted,
                follows_you=follows_you,
            )
            row.connect("follow", lambda _r, pk: self.emit("follow", pk))
            row.connect("unfollow", lambda _r, pk: self.emit("unfollow", pk))
            row.connect("menu", self._on_contact_menu)
            self._list_box.append(row)

        has_contacts = len(filtered) > 0
        self._list_box.set_visible(has_contacts)
        self._empty_state.set_visible(not has_contacts)
        self._update_nav_counts()

    def _get_filtered_contacts(self) -> list[Profile]:
        profiles = list(self._contacts)

        if self._active_filter == self.FILTER_MUTED:
            profiles = [p for p in profiles if p.pubkey in self._muted]
        elif self._active_filter == self.FILTER_BLOCKED:
            profiles = [p for p in profiles if p.pubkey in self._blocked]

        if self._search_query:
            q = self._search_query
            profiles = [
                p for p in profiles
                if q in p.handle.lower()
                or q in p.name.lower()
                or q in p.npub.lower()
                or q in p.pubkey.lower()
            ]

        return profiles

    def _update_nav_counts(self):
        for key, row in self._nav_items.items():
            if hasattr(row, "_count_getter") and hasattr(row, "_count_label"):
                try:
                    count = row._count_getter()
                    row._count_label.set_text(str(count))
                except Exception:
                    pass

    def _on_contact_menu(self, _row, pubkey: str):
        is_muted = pubkey in self._muted
        is_blocked = pubkey in self._blocked

        popover = Gtk.PopoverMenu()
        menu_model = Gio.Menu()

        if is_muted:
            item = Gio.MenuItem.new("Unmute", "contacts.unmute")
        else:
            item = Gio.MenuItem.new("Mute", "contacts.mute")
        menu_model.append_item(item)

        if is_blocked:
            item = Gio.MenuItem.new("Unblock", "contacts.unblock")
        else:
            item = Gio.MenuItem.new("Block", "contacts.block")
        menu_model.append_item(item)

        popover.set_menu_model(menu_model)
        popover.set_parent(_row)

        action_group = Gio.SimpleActionGroup()
        if is_muted:
            unmute_action = Gio.SimpleAction.new("unmute", None)
            unmute_action.connect("activate", lambda *_: self.emit("unmute", pubkey))
            action_group.add_action(unmute_action)
        else:
            mute_action = Gio.SimpleAction.new("mute", None)
            mute_action.connect("activate", lambda *_: self.emit("mute", pubkey))
            action_group.add_action(mute_action)

        if is_blocked:
            unblock_action = Gio.SimpleAction.new("unblock", None)
            unblock_action.connect("activate", lambda *_: self.emit("unblock", pubkey))
            action_group.add_action(unblock_action)
        else:
            block_action = Gio.SimpleAction.new("block", None)
            block_action.connect("activate", lambda *_: self.emit("block", pubkey))
            action_group.add_action(block_action)

        _row.insert_action_group("contacts", action_group)
        popover.popup()

    def set_contacts(self, profiles: list[Profile]):
        self._contacts = profiles
        self._schedule_render()

    def add_profile(self, profile: Profile):
        for i, p in enumerate(self._contacts):
            if p.pubkey == profile.pubkey:
                self._contacts[i] = profile
                self._schedule_render()
                return
        self._contacts.append(profile)
        self._schedule_render()

    def set_following(self, pubkeys: set[str]):
        self._following = pubkeys

    def set_muted(self, pubkeys: set[str]):
        self._muted = pubkeys
        self._schedule_render()

    def set_blocked(self, pubkeys: set[str]):
        self._blocked = pubkeys
        self._schedule_render()

    def set_follows_you(self, pubkeys: set[str]):
        self._follows_you = pubkeys

    def clear(self):
        self._contacts.clear()
        while child := self._list_box.get_first_child():
            self._list_box.remove(child)

    def show_loading(self, loading: bool):
        self._loading.set_active(loading)
        self._loading.set_visible(loading)
        self._list_box.set_visible(not loading)
        self._empty_state.set_visible(False)
