import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


class WelcomeView(Gtk.Box):
    __gsignals__ = {
        "create-identity": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "import-key": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "remote-signer": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)

        emblem = Gtk.Label(label="⚡")
        emblem.set_css_classes(["app-emblem"])
        self.append(emblem)

        title = Gtk.Label(label="Welcome to Echo")
        title.set_css_classes(["welcome-title"])
        self.append(title)

        desc = Gtk.Label(label="A native Nostr client for GNOME")
        self.append(desc)

        actions = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        actions.set_margin_top(24)

        create_btn = Gtk.Button(label="Create a new identity")
        create_btn.add_css_class("suggested-action")
        create_btn.connect("clicked", lambda _: self.emit("create-identity"))
        actions.append(create_btn)

        import_btn = Gtk.Button(label="Import an existing key")
        import_btn.connect("clicked", lambda _: self.emit("import-key"))
        actions.append(import_btn)

        signer_btn = Gtk.Button(label="Connect a remote signer")
        signer_btn.connect("clicked", lambda _: self.emit("remote-signer"))
        actions.append(signer_btn)

        self.append(actions)
