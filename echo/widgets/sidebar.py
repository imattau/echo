import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject
from .avatar import Avatar


class Sidebar(Gtk.Box):
    __gsignals__ = {
        "nav-changed": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "new-note": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "account-switch": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add_css_class("sidebar")

        self._nav_buttons = {}
        self._build_header()
        self._build_new_note_button()
        self._build_nav()
        self._build_account_switcher()

    def _build_header(self):
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.set_margin_start(12)
        header.set_margin_top(16)
        header.set_margin_bottom(16)

        logo = Avatar(size=20, initials="E", color="#3584E4")
        title = Gtk.Label(label="Echo")
        title.add_css_class("app-title")

        header.append(logo)
        header.append(title)
        self.append(header)

    def _build_new_note_button(self):
        btn = Gtk.Button(label="＋  New Note")
        btn.add_css_class("new-note-button")
        btn.set_margin_start(12)
        btn.set_margin_end(12)
        btn.set_margin_bottom(16)
        btn.connect("clicked", lambda _: self.emit("new-note"))
        self.append(btn)

    def _build_nav(self):
        nav_list = Gtk.ListBox()
        nav_list.set_selection_mode(Gtk.SelectionMode.NONE)

        items = [
            ("feed", "Home"),
            ("following", "Following"),
            ("discover", "Discover"),
            ("dms", "Direct Messages"),
            ("bookmarks", "Bookmarks"),
            ("relays", "Relays"),
        ]

        for name, label in items:
            row = self._nav_item(name, label)
            nav_list.append(row)

        self.append(nav_list)

    def _nav_item(self, name: str, label: str):
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(8)
        box.set_margin_bottom(8)

        icon_names = {
            "feed": "go-home-symbolic",
            "following": "people-symbolic",
            "discover": "edit-find-symbolic",
            "dms": "mail-symbolic",
            "bookmarks": "emblem-favorite-symbolic",
            "relays": "network-server-symbolic",
        }
        icon_name = icon_names.get(name, "view-list-symbolic")
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(16)

        text = Gtk.Label(label=label)
        text.set_halign(Gtk.Align.START)

        box.append(icon)
        box.append(text)

        gesture = Gtk.GestureClick()
        gesture.connect("pressed", lambda _g, _n, _x, _y, n=name: self.emit("nav-changed", n))
        box.add_controller(gesture)

        self._nav_buttons[name] = box
        return box

    def _build_account_switcher(self):
        spacer = Gtk.Label()
        spacer.set_vexpand(True)
        self.append(spacer)

        account_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        account_box.set_margin_start(12)
        account_box.set_margin_end(12)
        account_box.set_margin_top(8)
        account_box.set_margin_bottom(8)

        avatar = Avatar(size=32, initials="M", color="#99BF8C")

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        name = Gtk.Label(label="Matt")
        name.set_halign(Gtk.Align.START)
        npub = Gtk.Label(label="npub1matt…4kx2")
        npub.set_halign(Gtk.Align.START)
        info.append(name)
        info.append(npub)

        dropdown = Gtk.Label(label="⌄")

        account_box.append(avatar)
        account_box.append(info)
        account_box.append(dropdown)

        gesture = Gtk.GestureClick()
        gesture.connect("pressed", lambda *_: self.emit("account-switch"))
        account_box.add_controller(gesture)

        self.append(account_box)
