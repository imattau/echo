import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


class RemoteSignerView(Gtk.Box):
    __gsignals__ = {
        "back": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "connect-signer": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
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

        title = Gtk.Label(label="Connect a remote signer")
        title.set_css_classes(["welcome-title"])
        content.append(title)

        self._entry = Gtk.Entry()
        self._entry.set_placeholder_text("bunker://...")
        self._entry.set_width_chars(50)
        content.append(self._entry)

        connect_btn = Gtk.Button(label="Connect")
        connect_btn.add_css_class("suggested-action")
        connect_btn.connect("clicked", self._on_connect)
        content.append(connect_btn)

        self.append(content)

    def _on_connect(self, _btn):
        url = self._entry.get_text().strip()
        if url:
            self.emit("connect-signer", url)
