import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject
from echo.services.key_manager import KeyManager


class AccountSwitcherPopover(Gtk.Popover):
    __gsignals__ = {
        "account-selected": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "add-account": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__()

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content.set_margin_start(8)
        content.set_margin_end(8)
        content.set_margin_top(8)
        content.set_margin_bottom(8)

        key_manager = KeyManager.get()
        pubkey = key_manager.npub or key_manager.pubkey or ""
        short_id = pubkey[:16] if pubkey else "No identity"
        has_key = key_manager.has_key

        current = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        current.set_margin_bottom(4)
        label = Gtk.Label(label=short_id)
        label.set_hexpand(True)
        label.set_halign(Gtk.Align.START)
        current.append(label)
        if has_key:
            check = Gtk.Label(label="✓")
            current.append(check)
        content.append(current)

        sep = Gtk.Separator()
        content.append(sep)

        add_btn = Gtk.Button(label="Add an account")
        add_btn.set_halign(Gtk.Align.START)
        add_btn.set_margin_top(4)
        add_btn.connect("clicked", lambda _: [self.emit("add-account"), self.popdown()])
        content.append(add_btn)

        self.set_child(content)
