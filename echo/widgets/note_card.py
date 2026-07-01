import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Pango, GObject
from echo.models import Note
from .engagement_bar import EngagementBar
from .avatar import Avatar


class NoteCard(Gtk.Box):
    __gsignals__ = {
        "reply": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "repost": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "like": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "zap": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, note: Note):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add_css_class("note-card")
        self._note = note

        self._build_header()
        self._build_content()
        self._build_media()
        self._build_engagement()

    def _build_header(self):
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header.set_margin_start(16)
        header.set_margin_end(16)
        header.set_margin_top(12)

        initials = "?"
        color = "#99BF8C"
        if self._note.profile:
            initials = self._note.profile.handle[:2].upper()

        avatar = Avatar(size=40, initials=initials, color=color)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        name = Gtk.Label(label=self._note.profile.handle if self._note.profile else "unknown")
        name.set_halign(Gtk.Align.START)
        timestamp = Gtk.Label(label=str(self._note.created_at))
        timestamp.set_halign(Gtk.Align.START)
        info.append(name)
        info.append(timestamp)

        header.append(avatar)
        header.append(info)
        self.append(header)

    def _build_content(self):
        label = Gtk.Label(label=self._note.content)
        label.set_wrap(True)
        label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        label.set_margin_start(16)
        label.set_margin_end(16)
        label.set_margin_top(8)
        label.set_margin_bottom(8)
        label.set_halign(Gtk.Align.START)
        label.set_xalign(0)
        self.append(label)

    def _build_media(self):
        pass

    def _build_engagement(self):
        bar = EngagementBar(
            reply_count=self._note.reply_count,
            repost_count=self._note.repost_count,
            like_count=self._note.like_count,
            zap_amount=self._note.zap_amount,
        )
        bar.set_margin_start(16)
        bar.set_margin_end(16)
        bar.set_margin_bottom(12)
        bar.connect("reply", lambda _: self.emit("reply"))
        bar.connect("repost", lambda _: self.emit("repost"))
        bar.connect("like", lambda _: self.emit("like"))
        bar.connect("zap", lambda _: self.emit("zap"))
        self.append(bar)
