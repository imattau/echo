import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


class ImportKeyView(Gtk.Box):
    __gsignals__ = {
        "back": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "import-key": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        back_btn = Gtk.Button(label="‹ Back")
        back_btn.set_halign(Gtk.Align.START)
        back_btn.set_margin_start(20)
        back_btn.set_margin_top(20)
        back_btn.connect("clicked", lambda _: self.emit("back"))
        self.append(back_btn)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_halign(Gtk.Align.CENTER)
        content.set_valign(Gtk.Align.CENTER)
        content.set_margin_start(40)
        content.set_margin_end(40)

        title = Gtk.Label(label="Import an existing key")
        title.set_css_classes(["welcome-title"])
        content.append(title)

        self._entry = Gtk.Entry()
        self._entry.set_placeholder_text("nsec or hex key")
        self._entry.set_width_chars(50)
        content.append(self._entry)

        continue_btn = Gtk.Button(label="Continue to Echo")
        continue_btn.add_css_class("suggested-action")
        continue_btn.connect("clicked", self._on_import)
        content.append(continue_btn)

        self.append(content)

    def _on_import(self, _btn):
        key = self._entry.get_text().strip()
        if key:
            self.emit("import-key", key)
