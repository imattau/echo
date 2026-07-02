import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject, GLib
from echo.widgets.avatar import Avatar
from echo.models.profile import Profile
from echo.services.key_manager import KeyManager


def _fmt_count(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1000:
        return f"{n / 1000:.1f}K"
    return str(n)


class ProfileView(Gtk.Box):
    __gsignals__ = {
        "back": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "follow": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "tab-changed": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "edit-profile": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, profile: Profile = None, own_pubkey: str = ""):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._profile = profile
        self._own_pubkey = own_pubkey or ""
        self._tab_content = {}

        banner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        banner.set_size_request(-1, 180)
        banner.add_css_class("profile-banner")
        self.append(banner)

        back_btn = Gtk.Button(label="‹ Back to feed")
        back_btn.set_halign(Gtk.Align.START)
        back_btn.set_margin_start(16)
        back_btn.set_margin_top(16)
        back_btn.add_css_class("flat")
        back_btn.connect("clicked", lambda _: self.emit("back"))
        self.append(back_btn)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        header.set_margin_start(20)
        header.set_margin_end(20)
        header.set_margin_top(-48)

        initials = profile.initials if profile else "?"
        color = profile.avatar_color if profile else "#99BF8C"
        self._avatar = Avatar(size=96, initials=initials, color=color)
        header.append(self._avatar)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self._name = Gtk.Label(label=profile.name if profile else "Name")
        self._name.set_css_classes(["profile-name"])
        self._handle = Gtk.Label(label=f"@{profile.handle}" if profile else "@handle")
        info.append(self._name)
        info.append(self._handle)

        if profile and profile.about:
            about_label = Gtk.Label(label=profile.about)
            about_label.set_wrap(True)
            about_label.set_max_width_chars(60)
            about_label.set_xalign(0)
            about_label.set_margin_top(2)
            about_label.set_css_classes(["profile-about"])
            info.append(about_label)

        stats = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        stats.set_margin_top(4)
        self._stat_labels = {}
        for label_text, key, val in [
            ("Following", "following", profile.following_count if profile else 0),
            ("Followers", "followers", profile.followers_count if profile else 0),
            ("Notes", "notes", profile.notes_count if profile else 0),
        ]:
            stat = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            count_label = Gtk.Label(label=_fmt_count(val))
            count_label.set_css_classes(["stat-count"])
            name_label = Gtk.Label(label=label_text)
            name_label.set_css_classes(["stat-label"])
            stat.append(count_label)
            stat.append(name_label)
            stats.append(stat)
            self._stat_labels[key] = count_label
        info.append(stats)

        header.append(info)

        is_own = profile and self._own_pubkey == profile.pubkey
        self._follow_btn = Gtk.Button(
            label="Edit Profile" if is_own else "Follow"
        )
        if is_own:
            self._follow_btn.remove_css_class("suggested-action")
        else:
            self._follow_btn.add_css_class("suggested-action")
        self._follow_btn.set_halign(Gtk.Align.END)
        self._follow_btn.set_hexpand(True)
        self._follow_btn.connect("clicked", self._on_action_clicked)
        header.append(self._follow_btn)

        self.append(header)

        tabs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self._tab_group = None
        for tab_name in ["Notes", "Replies", "Media", "Zapped"]:
            btn = Gtk.ToggleButton(label=tab_name)
            btn.set_group(self._tab_group)
            self._tab_group = btn
            if tab_name == "Notes":
                btn.set_active(True)
            btn.connect("toggled", self._on_tab_toggled, tab_name)
            tabs.append(btn)
        self.append(tabs)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        self._content_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scrolled.set_child(self._content_area)
        self.append(scrolled)

    def set_profile(self, profile: Profile):
        self._profile = profile
        self._name.set_label(profile.name or profile.handle or "Name")
        self._handle.set_label(f"@{profile.handle}" if profile.handle else "@handle")
        self._avatar._initials = profile.initials or "?"
        self._avatar.queue_draw()

        for key, label in self._stat_labels.items():
            val = 0
            if key == "following":
                val = profile.following_count
            elif key == "followers":
                val = profile.followers_count
            elif key == "notes":
                val = profile.notes_count
            label.set_label(_fmt_count(val))

        is_own = self._own_pubkey == profile.pubkey
        self._follow_btn.set_visible(True)
        if is_own:
            self._follow_btn.set_label("Edit Profile")
            self._follow_btn.remove_css_class("suggested-action")
        else:
            self._follow_btn.set_label("Follow")
            self._follow_btn.add_css_class("suggested-action")

    def add_note_card(self, card):
        self._content_area.append(card)

    def clear_content(self):
        self._content_area.remove_all()

    def _on_action_clicked(self, btn):
        if btn.get_label() == "Edit Profile":
            self.emit("edit-profile")
        else:
            self.emit("follow")
            if btn.get_label() == "Follow":
                btn.set_label("Unfollow")
                btn.remove_css_class("suggested-action")
                btn.add_css_class("destructive-action")
            else:
                btn.set_label("Follow")
                btn.remove_css_class("destructive-action")
                btn.add_css_class("suggested-action")

    def _on_tab_toggled(self, btn, tab_name: str):
        if btn.get_active():
            self.emit("tab-changed", tab_name.lower())
