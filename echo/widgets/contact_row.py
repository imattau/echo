import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject
from echo.models import Profile
from echo.utils.helpers import truncate_npub
from .avatar import Avatar


class ContactRow(Gtk.Box):
    __gsignals__ = {
        "follow": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "unfollow": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "menu": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self, profile: Profile, is_following: bool = True, is_muted: bool = False, follows_you: bool = False):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._profile = profile
        self._is_following = is_following
        self._is_muted = is_muted
        self._following = is_following

        self.add_css_class("contact-row")
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_top(14)
        self.set_margin_bottom(14)

        avatar = Avatar(size=44, initials=profile.initials, color=profile.avatar_color)
        self.append(avatar)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        info.set_hexpand(True)

        name_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        name_row.set_halign(Gtk.Align.START)

        name = Gtk.Label(label=profile.handle)
        name.add_css_class("contact-name")
        name.set_halign(Gtk.Align.START)
        name_row.append(name)

        handle = Gtk.Label(label=f"@{profile.name}" if profile.name else truncate_npub(profile.npub, 16))
        handle.add_css_class("contact-handle")
        handle.set_halign(Gtk.Align.START)
        name_row.append(handle)

        if follows_you:
            badge = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            badge.add_css_class("contact-badge")
            badge.add_css_class("contact-badge-follows")
            badge_label = Gtk.Label(label="Follows you")
            badge_label.add_css_class("contact-badge-label")
            badge.append(badge_label)
            name_row.append(badge)

        if is_muted:
            badge = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            badge.add_css_class("contact-badge")
            badge.add_css_class("contact-badge-muted")
            badge_label = Gtk.Label(label="Muted")
            badge_label.add_css_class("contact-badge-label")
            badge.append(badge_label)
            name_row.append(badge)

        info.append(name_row)

        if profile.about:
            bio = Gtk.Label(label=profile.about)
            bio.add_css_class("contact-bio")
            bio.set_halign(Gtk.Align.START)
            bio.set_ellipsize(True)
            info.append(bio)

        self.append(info)

        action_btn = Gtk.Button()
        if self._following:
            action_btn.set_label("Following")
            action_btn.add_css_class("contact-action-btn")
            action_btn.add_css_class("contact-action-btn-following")
        else:
            action_btn.set_label("Follow")
            action_btn.add_css_class("contact-action-btn")
            action_btn.add_css_class("primary-button")

        def _on_action_clicked(_btn):
            if self._following:
                self.emit("unfollow", profile.pubkey)
            else:
                self.emit("follow", profile.pubkey)

        action_btn.connect("clicked", _on_action_clicked)
        self.append(action_btn)

        menu_btn = Gtk.Button(label="⋯")
        menu_btn.add_css_class("contact-menu-btn")
        menu_btn.connect("clicked", lambda _b: self.emit("menu", profile.pubkey))
        self.append(menu_btn)

    def set_following(self, following: bool):
        self._following = following
        action_btn = self.get_last_child()
        if action_btn and isinstance(action_btn, Gtk.Button):
            pass

    @property
    def profile(self) -> Profile:
        return self._profile

    @property
    def pubkey(self) -> str:
        return self._profile.pubkey

    @property
    def is_following(self) -> bool:
        return self._following
