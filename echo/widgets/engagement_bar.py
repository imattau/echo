import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, GObject


class EngagementBar(Gtk.Box):
    __gsignals__ = {
        "reply": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "repost": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "like": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "zap": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, reply_count=0, repost_count=0, like_count=0, zap_amount=0):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        self.reply_btn = self._button(f"↩ {reply_count}" if reply_count else "↩ Reply")
        self.reply_btn.connect("clicked", lambda _: self.emit("reply"))
        self.append(self.reply_btn)

        self.repost_btn = self._button(f"⟲ {repost_count}" if repost_count else "⟲ Repost")
        self.repost_btn.connect("clicked", lambda _: self.emit("repost"))
        self.append(self.repost_btn)

        self.like_btn = self._button(f"♥ {like_count}" if like_count else "♥ Like")
        self.like_btn.connect("clicked", lambda _: self.emit("like"))
        self.append(self.like_btn)

        self.zap_btn = self._zap_button(f"⚡ {zap_amount}" if zap_amount else "⚡ Zap")
        self.zap_btn.connect("clicked", lambda _: self.emit("zap"))
        self.append(self.zap_btn)

    def _button(self, label: str) -> Gtk.Button:
        btn = Gtk.Button(label=label)
        btn.add_css_class("engagement-button")
        return btn

    def _zap_button(self, label: str) -> Gtk.Button:
        btn = Gtk.Button(label=label)
        btn.add_css_class("zap-button")
        return btn
