import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


class HashtagPill(Gtk.Button):
    __gsignals__ = {
        "selected": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self, hashtag: str, count: str = ""):
        self._hashtag = hashtag
        label_text = f"#{hashtag}"
        if count:
            label_text += f" ({count})"

        super().__init__(label=label_text)
        self.add_css_class("trending-pill")
        self.connect("clicked", lambda _: self.emit("selected", f"#{hashtag}"))
