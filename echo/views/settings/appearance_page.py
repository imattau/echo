import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw
from echo.utils.config import Settings


class AppearancePage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.set_margin_start(14)
        self.set_margin_end(14)
        self.set_margin_top(24)

        title = Gtk.Label(label="Appearance")
        title.set_css_classes(["settings-title"])
        title.set_halign(Gtk.Align.START)
        self.append(title)

        settings = Settings.get()
        style_manager = Adw.StyleManager.get_default()

        theme_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        theme_group = None
        self._theme_buttons = {}
        for theme in ["Light", "Dark", "System"]:
            btn = Gtk.ToggleButton(label=theme)
            btn.set_group(theme_group)
            theme_group = btn
            theme_key = theme.lower()
            self._theme_buttons[theme_key] = btn
            btn.connect("toggled", self._on_theme_toggled, theme_key, style_manager)
            theme_row.append(btn)

        current_theme = settings.get_string("theme")
        if current_theme in self._theme_buttons:
            self._theme_buttons[current_theme].set_active(True)

        self.append(theme_row)

        for label_text, key in [
            ("Compact mode", "compact-mode"),
            ("Show media previews inline", "show-media-previews"),
        ]:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            label = Gtk.Label(label=label_text)
            label.set_hexpand(True)
            label.set_halign(Gtk.Align.START)
            switch = Gtk.Switch()
            settings.bind(switch, key)
            row.append(label)
            row.append(switch)
            self.append(row)

    def _on_theme_toggled(self, btn, theme_key: str, style_manager):
        if not btn.get_active():
            return
        settings = Settings.get()
        settings.set_string("theme", theme_key)
        settings.sync()
        theme_map = {
            "light": Adw.ColorScheme.FORCE_LIGHT,
            "dark": Adw.ColorScheme.FORCE_DARK,
            "system": Adw.ColorScheme.DEFAULT,
        }
        style_manager.set_color_scheme(theme_map.get(theme_key, Adw.ColorScheme.DEFAULT))
