import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject
from echo.widgets.avatar import Avatar


class ZapDialog(Adw.Window):
    __gsignals__ = {
        "send-zap": (GObject.SignalFlags.RUN_FIRST, None, (int, str)),
    }

    def __init__(self, parent, recipient_name="", recipient_handle=""):
        super().__init__(transient_for=parent, modal=True)
        self.set_title("Send a Zap")
        self.set_default_size(380, 500)
        self._selected_amount = 500
        self._amount_buttons = []

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_margin_top(24)
        content.set_margin_bottom(24)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        title = Gtk.Label(label="Send a Zap")
        title.set_hexpand(True)
        close_btn = Gtk.Button(label="✕")
        close_btn.connect("clicked", lambda _: self.close())
        header.append(title)
        header.append(close_btn)
        content.append(header)

        recipient_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        avatar = Avatar(size=32, initials=recipient_name[:2].upper() if recipient_name else "?")
        recipient_row.append(avatar)
        recipient_label = Gtk.Label(label=recipient_name or "Recipient")
        recipient_row.append(recipient_label)
        content.append(recipient_row)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        grid.set_column_spacing(8)
        grid.set_row_spacing(8)

        amounts = [21, 100, 500, 1000, 5000, 10000]
        self._amount_group = None
        for i, amount in enumerate(amounts):
            btn = Gtk.ToggleButton(label=f"⚡{amount}")
            btn.set_group(self._amount_group)
            self._amount_group = btn
            if amount == 500:
                btn.set_active(True)
            btn.connect("toggled", self._on_amount_toggled, amount)
            grid.attach(btn, i % 3, i // 3, 1, 1)
            self._amount_buttons.append(btn)

        content.append(grid)

        self._custom_entry = Gtk.Entry()
        self._custom_entry.set_placeholder_text("Custom amount (sats)")
        self._custom_entry.connect("activate", self._on_custom_amount)
        content.append(self._custom_entry)

        self._msg_entry = Gtk.Entry()
        self._msg_entry.set_placeholder_text("Add a message (optional)")
        content.append(self._msg_entry)

        self._send_btn = Gtk.Button(label="⚡ Send 500 sats")
        self._send_btn.add_css_class("zap-button")
        self._send_btn.connect("clicked", self._on_send)
        content.append(self._send_btn)

        self.set_content(content)
        self._update_amount_display()

    def _on_amount_toggled(self, btn, amount: int):
        if btn.get_active():
            self._selected_amount = amount
            self._update_amount_display()

    def _on_custom_amount(self, entry):
        try:
            amount = int(entry.get_text())
            if amount > 0:
                for b in self._amount_buttons:
                    b.set_active(False)
                self._selected_amount = amount
                self._update_amount_display()
        except ValueError:
            pass

    def _update_amount_display(self):
        self._send_btn.set_label(f"⚡ Send {self._selected_amount} sats")

    def _on_send(self, _btn):
        message = self._msg_entry.get_text()
        self.emit("send-zap", self._selected_amount, message)
        self.close()
