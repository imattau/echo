import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject
from echo.models import Profile
from .avatar import Avatar


class UserRow(Gtk.Box):
    __gsignals__ = {
        "clicked": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self, profile: Profile):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._profile = profile

        avatar = Avatar(size=48, initials=profile.handle[:2].upper(), color="#99BF8C")

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        name = Gtk.Label(label=profile.handle)
        name.set_halign(Gtk.Align.START)
        npub_label = Gtk.Label(label=profile.npub[:12])
        npub_label.set_halign(Gtk.Align.START)
        info.append(name)
        info.append(npub_label)

        self.append(avatar)
        self.append(info)

        gesture = Gtk.GestureClick()
        gesture.connect("pressed", lambda *_: self.emit("clicked", profile.pubkey))
        self.add_controller(gesture)
