import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject
from echo.widgets.relay_row import RelayRow
from echo.utils.config import Config


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
        add_btn.connect("clicked", self._on_add_clicked)
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

        for url in Config.DEFAULT_RELAYS:
            self.add_relay_row(RelayRow(url=url, status="disconnected"))

    def add_relay_row(self, row):
        self._list.append(row)

    def _on_add_clicked(self, _btn):
        window = Adw.Window(
            transient_for=self.get_root(),
            modal=True,
            title="Add Relay",
            default_width=400,
            default_height=160,
        )
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_start(16)
        content.set_margin_end(16)
        content.set_margin_top(16)
        content.set_margin_bottom(16)

        label = Gtk.Label(label="Enter relay URL:")
        label.set_halign(Gtk.Align.START)
        content.append(label)

        entry = Gtk.Entry()
        entry.set_placeholder_text("wss://relay.example.com")
        content.append(entry)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda _: window.close())
        actions.append(cancel_btn)

        add_btn = Gtk.Button(label="Add")
        add_btn.add_css_class("suggested-action")
        add_btn.connect("clicked", lambda _: self._add_from_dialog(window, entry))
        actions.append(add_btn)
        content.append(actions)

        entry.connect("activate", lambda: self._add_from_dialog(window, entry))
        window.set_content(content)
        window.present()

    def _add_from_dialog(self, window, entry):
        url = entry.get_text().strip()
        if url:
            self.add_relay_row(RelayRow(url=url, status="connecting"))
            self.emit("add-relay")
        window.close()


class RelaysPage(RelaysView):
    pass
