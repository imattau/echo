import gi

gi.require_version("Gtk", "4.0")
gi.require_version("GLib", "2.0")

from gi.repository import Gtk, GLib, Pango, GObject
from echo.models import Note
from .engagement_bar import EngagementBar
from .avatar import Avatar
from .media_widgets import ImagePlaceholder, VideoOverlay


class NoteCard(Gtk.Box):
    __gsignals__ = {
        "profile-clicked": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "reply": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "repost": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "like": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "zap": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, note: Note):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add_css_class("note-card")
        self._note = note
        self._show_more = False

        self._build_header()
        self._build_content()
        self._build_media()
        self._build_engagement()

    def _build_header(self):
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header.set_margin_start(16)
        header.set_margin_end(16)
        header.set_margin_top(12)

        profile = self._note.profile
        initials = profile.initials if profile else "?"
        color = profile.avatar_color if profile else "#99BF8C"

        avatar = Avatar(size=40, initials=initials, color=color)

        info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        name = Gtk.Label(label=profile.handle if profile else "unknown")
        name.set_halign(Gtk.Align.START)
        dt = GLib.DateTime.new_from_unix_utc(self._note.created_at)
        timestamp = Gtk.Label(label=dt.format("%b %d, %H:%M") or str(self._note.created_at))
        timestamp.set_halign(Gtk.Align.START)
        info.append(name)
        info.append(timestamp)

        header.append(avatar)
        header.append(info)

        click = Gtk.GestureClick()
        click.connect("pressed", lambda *_: self.emit("profile-clicked", self._note.pubkey))
        header.add_controller(click)

        self.append(header)

    def _build_content(self):
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        content_box.set_margin_start(16)
        content_box.set_margin_end(16)
        content_box.set_margin_top(8)
        content_box.set_margin_bottom(4)

        text = self._note.truncated_content if not self._show_more else self._note.content
        label = Gtk.Label(label=text)
        label.set_wrap(True)
        label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        label.set_halign(Gtk.Align.START)
        label.set_xalign(0)
        content_box.append(label)

        if self._note.is_truncated and not self._show_more:
            more_btn = Gtk.Button(label="Show more")
            more_btn.set_halign(Gtk.Align.START)
            more_btn.add_css_class("flat")
            more_btn.connect("clicked", self._on_show_more)
            content_box.append(more_btn)

        self._content_box = content_box
        self.append(content_box)

    def _on_show_more(self, btn):
        self._show_more = True
        self._content_box.set_visible(False)
        self.remove(self._content_box)
        self._build_content()

    def _build_media(self):
        urls = self._note.media_urls
        if not urls:
            return
        for url in urls[:3]:
            if any(url.lower().endswith(ext) for ext in (".mp4", ".webm", ".mov")):
                widget = VideoOverlay()
            else:
                widget = ImagePlaceholder()
            widget.set_margin_start(16)
            widget.set_margin_end(16)
            widget.set_margin_top(4)
            widget.set_margin_bottom(4)
            self.append(widget)

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
        self._engagement_bar = bar
        self.append(bar)
