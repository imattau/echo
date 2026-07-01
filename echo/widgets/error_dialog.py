import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, GObject


class ErrorDialog(Adw.Window):
    __gsignals__ = {
        "retry": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, parent, title="Something went wrong", message="", primary_label="Try Again"):
        super().__init__(transient_for=parent, modal=True)
        self.set_default_size(380, 280)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_halign(Gtk.Align.CENTER)
        content.set_valign(Gtk.Align.CENTER)

        icon = Gtk.Label(label="⚠")
        icon.set_css_classes(["error-icon"])
        content.append(icon)

        title_label = Gtk.Label(label=title)
        title_label.set_css_classes(["dialog-title"])
        content.append(title_label)

        if message:
            msg = Gtk.Label(label=message)
            msg.set_wrap(True)
            msg.set_max_width_chars(40)
            content.append(msg)

        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda _: self.close())
        buttons.append(cancel_btn)

        retry_btn = Gtk.Button(label=primary_label)
        retry_btn.add_css_class("suggested-action")
        retry_btn.connect("clicked", lambda _: [self.emit("retry"), self.close()])
        buttons.append(retry_btn)

        content.append(buttons)
        self.set_content(content)


class ConfirmDialog(Adw.Window):
    __gsignals__ = {
        "confirm": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, parent, title="", message="", destructive_label="Remove", destructive=False):
        super().__init__(transient_for=parent, modal=True)
        self.set_default_size(380, 280)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_start(24)
        content.set_margin_end(24)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_halign(Gtk.Align.CENTER)
        content.set_valign(Gtk.Align.CENTER)

        icon = Gtk.Label(label="⚠")
        content.append(icon)

        title_label = Gtk.Label(label=title)
        title_label.set_css_classes(["dialog-title"])
        content.append(title_label)

        if message:
            msg = Gtk.Label(label=message)
            msg.set_wrap(True)
            msg.set_max_width_chars(40)
            content.append(msg)

        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda _: self.close())
        buttons.append(cancel_btn)

        confirm_btn = Gtk.Button(label=destructive_label)
        if destructive:
            confirm_btn.add_css_class("destructive-action")
        confirm_btn.connect("clicked", lambda _: [self.emit("confirm"), self.close()])
        buttons.append(confirm_btn)

        content.append(buttons)
        self.set_content(content)


class Toast(Gtk.Box):
    def __init__(self, message="", success=True):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add_css_class("toast")

        icon = Gtk.Label(label="✓" if success else "⚠")
        content = Gtk.Label(label=message)
        self.append(icon)
        self.append(content)


class InlineErrorBanner(Gtk.Box):
    __gsignals__ = {
        "retry": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, title="Failed to connect", subtitle=""):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add_css_class("error-banner")

        icon = Gtk.Label(label="⚠")
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title_lbl = Gtk.Label(label=title)
        text_box.append(title_lbl)
        if subtitle:
            sub = Gtk.Label(label=subtitle)
            text_box.append(sub)

        retry_btn = Gtk.Button(label="Retry")
        retry_btn.connect("clicked", lambda _: self.emit("retry"))

        self.append(icon)
        self.append(text_box)
        self.append(retry_btn)


class OfflineBanner(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.add_css_class("offline-banner")
        icon = Gtk.Label(label="⚠")
        text = Gtk.Label(label="You're offline — notes will send once you reconnect")
        self.append(icon)
        self.append(text)
