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

        self._reply_count = reply_count
        self._repost_count = repost_count
        self._like_count = like_count
        self._zap_amount = zap_amount

        self.reply_btn = self._action_button("↩", reply_count, "Reply")
        self.reply_btn.set_tooltip_text("Reply")
        self.reply_btn.connect("clicked", lambda _: self.emit("reply"))
        self.append(self.reply_btn)

        self.repost_btn = self._toggle_button("⟲", repost_count, "Repost")
        self.repost_btn.set_tooltip_text("Repost")
        self.repost_btn.connect("toggled", lambda b: self.emit("repost") if b.get_active() else None)
        self.append(self.repost_btn)

        self.like_btn = self._toggle_button("♥", like_count, "Like")
        self.like_btn.set_tooltip_text("Like")
        self.like_btn.connect("toggled", lambda b: self.emit("like") if b.get_active() else None)
        self.append(self.like_btn)

        self.zap_btn = self._action_button("⚡", zap_amount, "Zap")
        self.zap_btn.set_tooltip_text("Send zap")
        self.zap_btn.connect("clicked", lambda _: self.emit("zap"))
        self.append(self.zap_btn)

    def _make_label(self, icon: str, count: int, fallback: str) -> str:
        return f"{icon} {count}" if count else f"{icon} {fallback}"

    def _action_button(self, icon: str, count: int, fallback: str) -> Gtk.Button:
        btn = Gtk.Button(label=self._make_label(icon, count, fallback))
        btn.add_css_class("engagement-button")
        return btn

    def _toggle_button(self, icon: str, count: int, fallback: str) -> Gtk.ToggleButton:
        btn = Gtk.ToggleButton(label=self._make_label(icon, count, fallback))
        btn.add_css_class("engagement-button")
        return btn

    def update_counts(self, reply_count=None, repost_count=None, like_count=None, zap_amount=None):
        if reply_count is not None:
            self._reply_count = reply_count
            self.reply_btn.set_label(self._make_label("↩", reply_count, "Reply"))
        if repost_count is not None:
            self._repost_count = repost_count
            self.repost_btn.set_label(self._make_label("⟲", repost_count, "Repost"))
        if like_count is not None:
            self._like_count = like_count
            self.like_btn.set_label(self._make_label("♥", like_count, "Like"))
        if zap_amount is not None:
            self._zap_amount = zap_amount
            self.zap_btn.set_label(self._make_label("⚡", zap_amount, "Zap"))
