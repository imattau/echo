import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject
from echo.services.key_manager import KeyManager
from echo.widgets.avatar import Avatar


class AccountsPage(Gtk.Box):
    __gsignals__ = {
        "add-account": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.set_margin_start(14)
        self.set_margin_end(14)
        self.set_margin_top(24)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        title = Gtk.Label(label="Accounts")
        title.set_css_classes(["settings-title"])
        title.set_halign(Gtk.Align.START)
        title.set_hexpand(True)

        add_btn = Gtk.Button(label="Add Account")
        add_btn.add_css_class("suggested-action")
        add_btn.connect("clicked", lambda _: self.emit("add-account"))
        header.append(title)
        header.append(add_btn)
        self.append(header)

        self._list = Gtk.ListBox()
        self._list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.append(self._list)

        km = KeyManager.get()
        if km.has_key:
            pubkey = km.pubkey or ""
            npub = km.npub or ""
            initials = pubkey[:2].upper() if pubkey else "?"
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.set_margin_start(12)
            row.set_margin_end(12)
            row.set_margin_top(8)
            row.set_margin_bottom(8)
            avatar = Avatar(size=32, initials=initials)
            row.append(avatar)
            info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            name = Gtk.Label(label=npub[:20] + "…" if len(npub) > 20 else npub)
            name.set_halign(Gtk.Align.START)
            info.append(name)
            row.append(info)
            self._list.append(row)
        else:
            empty = Gtk.Label(label="No accounts set up yet.\nUse the onboarding to create or import a key.")
            empty.set_margin_top(16)
            empty.set_halign(Gtk.Align.CENTER)
            self._list.append(empty)
