import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject
from echo.models.profile import Profile


class EditProfileDialog(Adw.Window):
    __gsignals__ = {
        "save": (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self, parent, profile: Profile = None):
        super().__init__(transient_for=parent, modal=True)
        self.set_title("Edit Profile")
        self.set_default_size(560, 640)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content.set_margin_start(16)
        content.set_margin_end(16)
        content.set_margin_top(16)
        content.set_margin_bottom(16)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        title = Gtk.Label(label="Edit Profile")
        title.set_hexpand(True)
        title.set_css_classes(["settings-title"])
        close_btn = Gtk.Button(label="✕")
        close_btn.connect("clicked", lambda _: self.close())
        header.append(title)
        header.append(close_btn)
        content.append(header)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        form.set_margin_top(8)

        fields = [
            ("name", "Name", "Short name", profile.name if profile else ""),
            ("display_name", "Display Name", "Display name", profile.display_name if profile else ""),
            ("about", "About", "Bio / description", profile.about if profile else ""),
            ("picture", "Picture URL", "https://example.com/avatar.png", profile.picture if profile else ""),
            ("banner", "Banner URL", "https://example.com/banner.png", profile.banner if profile else ""),
            ("nip05", "NIP-05", "user@example.com", profile.nip05 if profile else ""),
            ("lud16", "Lightning Address", "user@getalby.com", profile.lud16 if profile else ""),
            ("website", "Website", "https://example.com", profile.website if profile else ""),
        ]

        self._entries = {}

        for key, label_text, placeholder, value in fields:
            row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

            lbl = Gtk.Label(label=label_text)
            lbl.set_halign(Gtk.Align.START)
            lbl.set_css_classes(["field-label"])
            row.append(lbl)

            entry = Gtk.Entry()
            entry.set_placeholder_text(placeholder)
            entry.set_text(value)
            entry.set_hexpand(True)
            self._entries[key] = entry
            row.append(entry)

            if key == "about":
                text_view = Gtk.TextView()
                text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
                text_view.set_placeholder_text(placeholder)
                text_view.set_size_request(-1, 80)
                buffer = text_view.get_buffer()
                if value:
                    buffer.set_text(value)
                self._entries[key] = text_view
                row.remove(entry)
                row.append(text_view)

            form.append(row)

        scrolled.set_child(form)
        content.append(scrolled)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        actions.set_margin_top(8)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda _: self.close())
        actions.append(cancel_btn)

        save_btn = Gtk.Button(label="Save")
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self._on_save)
        actions.append(save_btn)

        content.append(actions)

        self.set_content(content)

    def _on_save(self, _btn):
        metadata = {}
        for key, entry in self._entries.items():
            if isinstance(entry, Gtk.TextView):
                buffer = entry.get_buffer()
                val = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False).strip()
            else:
                val = entry.get_text().strip()
            metadata[key] = val
        self.emit("save", metadata)
        self.close()
