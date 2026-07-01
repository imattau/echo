import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


class ProfileView(Gtk.Box):
    __gsignals__ = {
        "follow": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "tab-changed": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        banner = Gtk.DrawingArea()
        banner.set_size_request(-1, 180)
        banner.add_css_class("profile-banner")
        self.append(banner)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        header.set_margin_start(20)
        header.set_margin_end(20)
        header.set_margin_top(-48)

        avatar = Gtk.DrawingArea()
        avatar.set_size_request(96, 96)
        avatar.add_css_class("profile-avatar")
        header.append(avatar)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self._name = Gtk.Label(label="Name")
        self._name.set_css_classes(["profile-name"])
        self._handle = Gtk.Label(label="@handle")
        info.append(self._name)
        info.append(self._handle)

        stats = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        stats.set_margin_top(4)
        for label_text, count in [("Following", "284"), ("Followers", "12.4K"), ("Notes", "1,204")]:
            stat = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            count_label = Gtk.Label(label=count)
            count_label.set_css_classes(["stat-count"])
            name_label = Gtk.Label(label=label_text)
            name_label.set_css_classes(["stat-label"])
            stat.append(count_label)
            stat.append(name_label)
            stats.append(stat)
        info.append(stats)

        header.append(info)

        self._follow_btn = Gtk.Button(label="Follow")
        self._follow_btn.add_css_class("suggested-action")
        self._follow_btn.set_halign(Gtk.Align.END)
        self._follow_btn.set_hexpand(True)
        self._follow_btn.connect("clicked", lambda _: self.emit("follow"))
        header.append(self._follow_btn)

        self.append(header)

        tabs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self._tab_group = None
        for tab_name in ["Notes", "Replies", "Media", "Zapped"]:
            btn = Gtk.ToggleButton(label=tab_name)
            btn.set_group(self._tab_group)
            self._tab_group = btn
            btn.connect("toggled", self._on_tab_toggled, tab_name)
            tabs.append(btn)
        self.append(tabs)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        self._notes = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        scrolled.set_child(self._notes)
        self.append(scrolled)

    def _on_tab_toggled(self, btn, tab_name: str):
        if btn.get_active():
            self.emit("tab-changed", tab_name.lower())
