import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


class WalletPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.set_margin_start(14)
        self.set_margin_end(14)
        self.set_margin_top(24)

        title = Gtk.Label(label="Wallet")
        title.set_css_classes(["settings-title"])
        title.set_halign(Gtk.Align.START)
        self.append(title)

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        wallet_name = Gtk.Label(label="Alby")
        balance = Gtk.Label(label="Balance: 42,300 sats")
        disconnect_btn = Gtk.Button(label="Disconnect")
        disconnect_btn.add_css_class("destructive-action")
        card.append(wallet_name)
        card.append(balance)
        card.append(disconnect_btn)
        self.append(card)

        entry = Gtk.Entry()
        entry.set_placeholder_text("NWC connection string")
        self.append(entry)

        connect_btn = Gtk.Button(label="Connect")
        self.append(connect_btn)
