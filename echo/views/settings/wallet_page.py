import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject
from echo.utils.config import Config


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

        self._error_label = Gtk.Label(label="")
        self._error_label.add_css_class("error-text")
        self._error_label.set_halign(Gtk.Align.START)
        self._error_label.set_visible(False)
        connection_section.append(self._error_label)

        connect_btn = Gtk.Button(label="Connect")
        connect_btn.add_css_class("suggested-action")
        connect_btn.connect("clicked", self._on_connect)
        connection_section.append(connect_btn)

        self._connect_btn = connect_btn
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

        self._disconnect_btn = Gtk.Button(label="Disconnect")
        self._disconnect_btn.add_css_class("destructive-action")
        self._disconnect_btn.connect("clicked", self._on_disconnect)
        self._status_section.append(self._disconnect_btn)

        self._status_section.set_visible(False)
        self.append(self._status_section)

        saved_uri = self._load_uri()
        if saved_uri:
            self._nwc_entry.set_text(saved_uri)

    def set_wallet_status(self, connected=False, name="", balance=""):
        self._status_section.set_visible(connected)
        self._error_label.set_visible(False)
        self._connect_btn.set_sensitive(True)
        if connected:
            self._wallet_name.set_label(name or "Connected wallet")
            self._balance.set_label(balance or "")

    def show_error(self, message: str):
        self._error_label.set_label(message)
        self._error_label.set_visible(True)
        self._connect_btn.set_sensitive(True)

    def set_connecting(self, connecting: bool):
        self._connect_btn.set_sensitive(not connecting)

    def _load_uri(self) -> str:
        try:
            path = Config.STATE_DIR / "nwc_uri"
            if path.exists():
                return path.read_text().strip()
        except Exception:
            pass
        return ""

    def _save_uri(self, uri: str):
        try:
            Config.STATE_DIR.mkdir(parents=True, exist_ok=True)
            (Config.STATE_DIR / "nwc_uri").write_text(uri)
        except Exception:
            pass

    def _clear_saved_uri(self):
        try:
            path = Config.STATE_DIR / "nwc_uri"
            if path.exists():
                path.unlink()
        except Exception:
            pass

    def _on_connect(self, _btn):
        url = self._nwc_entry.get_text().strip()
        if not url:
            return
        self._error_label.set_visible(False)
        self._connect_btn.set_sensitive(False)
        self.emit("connect-wallet", url)

    def _on_disconnect(self, _btn):
        self.emit("disconnect-wallet")
