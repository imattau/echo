import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject
from echo.services.key_manager import KeyManager


class WalletPage(Gtk.Box):
    __gsignals__ = {
        "connect-wallet": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "disconnect-wallet": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.set_margin_start(14)
        self.set_margin_end(14)
        self.set_margin_top(24)

        title = Gtk.Label(label="Wallet")
        title.set_css_classes(["settings-title"])
        title.set_halign(Gtk.Align.START)
        self.append(title)

        desc = Gtk.Label(label="Connect a Nostr Wallet Connect (NWC) lightning wallet to send zaps.")
        desc.set_wrap(True)
        desc.set_max_width_chars(60)
        self.append(desc)

        connection_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        connection_section.set_margin_top(8)

        self._nwc_entry = Gtk.Entry()
        self._nwc_entry.set_placeholder_text("nostr+walletconnect://...")
        connection_section.append(self._nwc_entry)

        connect_btn = Gtk.Button(label="Connect")
        connect_btn.add_css_class("suggested-action")
        connect_btn.connect("clicked", self._on_connect)
        connection_section.append(connect_btn)
        self.append(connection_section)

        self._status_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self._status_section.set_margin_top(16)

        status_title = Gtk.Label(label="Connected Wallet")
        status_title.set_css_classes(["settings-title"])
        status_title.set_halign(Gtk.Align.START)
        self._status_section.append(status_title)

        self._wallet_name = Gtk.Label(label="Not connected")
        self._wallet_name.set_halign(Gtk.Align.START)
        self._status_section.append(self._wallet_name)

        self._balance = Gtk.Label(label="")
        self._balance.set_halign(Gtk.Align.START)
        self._status_section.append(self._balance)

        disconnect_btn = Gtk.Button(label="Disconnect")
        disconnect_btn.add_css_class("destructive-action")
        disconnect_btn.connect("clicked", self._on_disconnect)
        self._status_section.append(disconnect_btn)

        self._status_section.set_visible(False)
        self.append(self._status_section)

        self.set_wallet_status(connected=False)

    def set_wallet_status(self, connected=False, name="", balance=""):
        self._status_section.set_visible(connected)
        if connected:
            self._wallet_name.set_label(name or "Connected wallet")
            self._balance.set_label(balance or "")

    def _on_connect(self, _btn):
        url = self._nwc_entry.get_text().strip()
        if not url:
            return
        self.emit("connect-wallet", url)

    def _on_disconnect(self, _btn):
        self.emit("disconnect-wallet")
