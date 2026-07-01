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

        desc = Gtk.Label(label="Paste your nsec (starts with nsec1) or hex private key below")
        desc.set_wrap(True)
        desc.set_max_width_chars(50)
        content.append(desc)

        self._entry = Gtk.Entry()
        self._entry.set_placeholder_text("nsec1... or hex key")
        self._entry.set_width_chars(50)
        self._entry.connect("changed", self._on_entry_changed)
        content.append(self._entry)

        self._error_label = Gtk.Label(label="")
        self._error_label.add_css_class("error-text")
        self._error_label.set_halign(Gtk.Align.START)
        self._error_label.set_visible(False)
        content.append(self._error_label)

        self._continue_btn = Gtk.Button(label="Continue to Echo")
        self._continue_btn.add_css_class("suggested-action")
        self._continue_btn.set_sensitive(False)
        self._continue_btn.connect("clicked", self._on_import)
        content.append(self._continue_btn)

        self.append(content)

    def _on_entry_changed(self, entry):
        key = entry.get_text().strip()
        if not key:
            self._error_label.set_visible(False)
            self._continue_btn.set_sensitive(False)
            return
        valid = key.startswith("nsec1") or (len(key) == 64 and all(c in "0123456789abcdef" for c in key.lower()))
        if not valid:
            self._error_label.set_label("Invalid format. Enter an nsec1... or a 64-character hex key.")
            self._error_label.set_visible(True)
            self._continue_btn.set_sensitive(False)
        else:
            self._error_label.set_visible(False)
            self._continue_btn.set_sensitive(True)

    def _on_import(self, _btn):
        key = self._entry.get_text().strip()
        if key:
            self.emit("import-key", key)
