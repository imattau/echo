import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk
from .widgets.sidebar import Sidebar
from .views.feed.feed_view import FeedView


class EchoWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Echo")
        self.set_default_size(1200, 800)

        split_view = Adw.NavigationSplitView()
        split_view.set_min_sidebar_width(240)
        split_view.set_max_sidebar_width(240)

        self.sidebar = Sidebar()
        self.content = Gtk.Stack()
        self.detail = Gtk.Stack()

        feed_view = FeedView()
        self.content.add_named(feed_view, "feed")
        self.content.set_visible_child_name("feed")

        split_view.set_sidebar(self.sidebar)
        split_view.set_content(self.content)
        split_view.set_detail(self.detail)

        self.set_content(split_view)
