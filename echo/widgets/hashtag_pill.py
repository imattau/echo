import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


class HashtagPill(Gtk.Box):
    def __init__(self, hashtag: str, count: str = ""):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        label_text = f"#{hashtag}"
        if count:
            label_text += f" ({count})"

        label = Gtk.Label(label=label_text)
        self.append(label)
