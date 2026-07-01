import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


class AccountsPage(Gtk.Box):
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
        header.append(title)
        header.append(add_btn)
        self.append(header)

        self._list = Gtk.ListBox()
        self._list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.append(self._list)
