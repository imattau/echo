import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject


class RelaysView(Gtk.Box):
    __gsignals__ = {
        "add-relay": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        header.set_margin_start(14)
        header.set_margin_end(14)
        header.set_margin_top(24)

        title = Gtk.Label(label="Relays")
        title.set_css_classes(["settings-title"])
        title.set_halign(Gtk.Align.START)
        title.set_hexpand(True)

        add_btn = Gtk.Button(label="Add Relay")
        add_btn.add_css_class("suggested-action")
        add_btn.connect("clicked", lambda _: self.emit("add-relay"))
        header.append(title)
        header.append(add_btn)
        self.append(header)

        desc = Gtk.Label(label="Manage your relay connections")
        desc.set_margin_start(14)
        desc.set_margin_end(14)
        desc.set_margin_top(8)
        self.append(desc)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        self._list = Gtk.ListBox()
        self._list.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.set_child(self._list)
        self.append(scrolled)

    def add_relay_row(self, row):
        self._list.append(row)


class RelaysPage(RelaysView):
    pass
