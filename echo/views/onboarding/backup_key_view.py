import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


class BackupKeyView(Gtk.Box):
    __gsignals__ = {
        "back": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "continue": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, nsec="", npub=""):
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

        nsec_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        nsec_box.set_margin_top(8)
        nsec_box.set_margin_bottom(8)

        nsec_label = Gtk.Label(label="Your private key (nsec)")
        nsec_label.set_halign(Gtk.Align.START)
        nsec_box.append(nsec_label)

        self._nsec_entry = Gtk.Entry()
        self._nsec_entry.set_text(nsec)
        self._nsec_entry.set_width_chars(60)
        self._nsec_entry.set_visibility(False)
        self._nsec_entry.set_editable(False)
        nsec_box.append(self._nsec_entry)

        reveal_btn = Gtk.Button(label="Reveal")
        reveal_btn.set_halign(Gtk.Align.START)
        reveal_btn.connect("clicked", self._on_reveal)
        nsec_box.append(reveal_btn)

        copy_btn = Gtk.Button(label="Copy to clipboard")
        copy_btn.set_halign(Gtk.Align.START)
        copy_btn.connect("clicked", self._on_copy)
        nsec_box.append(copy_btn)

        content.append(nsec_box)

        confirm_btn = Gtk.Button(label="I've backed up my key — Continue to Echo")
        confirm_btn.add_css_class("suggested-action")
        confirm_btn.connect("clicked", lambda _: self.emit("continue"))
        content.append(confirm_btn)

        self.append(content)

    def _on_reveal(self, btn):
        visible = self._nsec_entry.get_visibility()
        self._nsec_entry.set_visibility(not visible)
        btn.set_label("Hide" if not visible else "Reveal")

    def _on_copy(self, btn):
        clipboard = self.get_clipboard()
        clipboard.set_text(self._nsec_entry.get_text())
