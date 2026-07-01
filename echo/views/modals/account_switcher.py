import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


class AccountSwitcherPopover(Gtk.Popover):
    def __init__(self):
        super().__init__()

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content.set_margin_start(8)
        content.set_margin_end(8)
        content.set_margin_top(8)
        content.set_margin_bottom(8)

        accounts = [
            ("Matt", True),
            ("Echo Test", False),
            ("Side Project", False),
        ]

        for name, active in accounts:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            label = Gtk.Label(label=name)
            row.append(label)
            if active:
                check = Gtk.Label(label="✓")
                row.append(check)
            content.append(row)

        sep = Gtk.Separator()
        content.append(sep)

        add_btn = Gtk.Button(label="Add an account")
        add_btn.set_halign(Gtk.Align.START)
        content.append(add_btn)

        self.set_child(content)
