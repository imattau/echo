import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


class BackupKeyView(Gtk.Box):
    __gsignals__ = {
        "back": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "continue": (GObject.SignalFlags.RUN_FIRST, None, ()),
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

        title = Gtk.Label(label="Back up your key")
        title.set_css_classes(["welcome-title"])
        content.append(title)

        warning = Gtk.Label(label="This is the only copy of your private key. If you lose it, you lose access to your identity forever.")
        warning.set_wrap(True)
        warning.set_max_width_chars(50)
        content.append(warning)

        confirm_btn = Gtk.Button(label="Continue to Echo")
        confirm_btn.add_css_class("suggested-action")
        confirm_btn.connect("clicked", lambda _: self.emit("continue"))
        content.append(confirm_btn)

        self.append(content)
