import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk
from echo.models import Profile


class UserRow(Gtk.Box):
    def __init__(self, profile: Profile):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._profile = profile

        avatar = Gtk.DrawingArea()
        avatar.set_size_request(48, 48)
        avatar.add_css_class("avatar")

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        name = Gtk.Label(label=profile.handle)
        name.set_halign(Gtk.Align.START)
        npub = Gtk.Label(label=profile.npub[:12])
        npub.set_halign(Gtk.Align.START)
        info.append(name)
        info.append(npub)

        self.append(avatar)
        self.append(info)
