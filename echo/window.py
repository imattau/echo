import json

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk
from .widgets.sidebar import Sidebar
from .widgets.note_card import NoteCard
from .views.feed.feed_view import FeedView
from .views.feed.thread_view import ThreadView
from .views.feed.note_list import NoteList
from .views.discover.discover_view import DiscoverView
from .views.dms.dm_list import DMListView
from .views.dms.dm_conversation import DMConversationView
from .views.bookmarks.bookmarks_view import BookmarksView
from .views.contacts.contacts_view import ContactsView
from .views.relays.relays_view import RelaysView
from .views.profile.profile_view import ProfileView
from .views.modals.compose_dialog import ComposeDialog
from .views.modals.zap_dialog import ZapDialog
from .views.modals.account_switcher import AccountSwitcherPopover
from .views.settings.settings_window import SettingsWindow
from .views.onboarding.import_key_view import ImportKeyView
from echo.services.key_manager import KeyManager
from echo.services.relay_manager import RelayManager
from echo.services.profile_service import ProfileService
from echo.services.nostr_client import NostrClient
from echo.utils.config import Config, Settings
from echo.widgets.error_dialog import ErrorDialog, ConfirmDialog


class EchoWindow(Adw.ApplicationWindow):
    def __init__(self, key_manager=None, relay_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Echo")
        self.set_default_size(1200, 800)

        self._key_manager = key_manager or KeyManager.get()
        self._relay_manager = relay_manager or RelayManager()
        self._profile_service = ProfileService()

        self.sidebar = Sidebar(key_manager=self._key_manager)
        self.sidebar.set_size_request(240, -1)

        self.content = Gtk.Stack()
        self.content.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)

        self._pages = {}
        for name, page_cls in [
            ("feed", FeedView),
            ("following", FeedView),
            ("discover", DiscoverView),
            ("dms", DMListView),
            ("dm-conversation", DMConversationView),
            ("bookmarks", BookmarksView),
            ("contacts", ContactsView),
            ("relays", RelaysView),
            ("thread", ThreadView),
        ]:
            if page_cls is FeedView:
                page = FeedView(title_text="Following" if name == "following" else "Home")
            else:
                page = page_cls()
            self._pages[name] = page
            self.content.add_named(page, name)

        settings = Settings.get()
        initial_page = "following" if settings.get_bool("open-to-following-feed") else "feed"
        self.content.set_visible_child_name(initial_page)

        self._state_file = Config.STATE_DIR / "window_state.json"
        self._restore_window_state(settings)

        self.connect("close-request", self._on_close_request)

        self.sidebar.connect("nav-changed", self._on_nav_changed)
        self.sidebar.connect("new-note", self._on_new_note)
        self.sidebar.connect("account-switch", self._on_account_switch)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_start_child(self.sidebar)
        paned.set_end_child(self.content)
        paned.set_shrink_start_child(False)
        paned.set_shrink_end_child(False)
        paned.set_position(240)

        self.set_content(paned)

        feed = self._pages.get("feed")
        if isinstance(feed, FeedView):
            feed.connect("refresh", self._on_feed_refresh)
        thread = self._pages.get("thread")
        if isinstance(thread, ThreadView):
            thread.connect("back", lambda _: self.content.set_visible_child_name("feed"))

        dms_list = self._pages.get("dms")
        if isinstance(dms_list, DMListView):
            dms_list.connect("conversation-selected", self._on_dm_conversation_selected)
            dms_list.connect("new-conversation", self._on_dm_new_conversation)
        dm_conv = self._pages.get("dm-conversation")
        if isinstance(dm_conv, DMConversationView):
            dm_conv.connect("send-message", self._on_dm_send_message)
            dm_conv.connect("back", lambda _: self.content.set_visible_child_name("dms"))

        discover = self._pages.get("discover")
        if isinstance(discover, DiscoverView):
            discover.connect("search", self._on_discover_search)
            discover.connect("trending-tag", self._on_discover_trending_tag)

        bookmarks = self._pages.get("bookmarks")
        if isinstance(bookmarks, BookmarksView):
            bookmarks.connect("load", self._on_bookmarks_load)

        contacts = self._pages.get("contacts")
        if isinstance(contacts, ContactsView):
            contacts.connect("load", self._on_contacts_load)
            contacts.connect("add-contact", self._on_contacts_add)
            contacts.connect("follow", self._on_contacts_follow)
            contacts.connect("unfollow", self._on_contacts_unfollow)
            contacts.connect("mute", self._on_contacts_mute)
            contacts.connect("unmute", self._on_contacts_unmute)
            contacts.connect("block", self._on_contacts_block)
            contacts.connect("unblock", self._on_contacts_unblock)

        self._connect_default_relays()

    def _connect_default_relays(self):
        if self._key_manager.has_key:
            for url in Config.DEFAULT_RELAYS:
                self._relay_manager.add_relay(url)

    def _restore_window_state(self, settings):
        if settings.get_bool("restore-last-window-state"):
            try:
                if self._state_file.exists():
                    data = json.loads(self._state_file.read_text())
                    w = data.get("width", 1200)
                    h = data.get("height", 800)
                    self.set_default_size(w, h)
            except Exception:
                pass

    def _on_close_request(self, *args):
        settings = Settings.get()
        if settings.get_bool("restore-last-window-state"):
            try:
                w, h = self.get_default_size()
                Config.STATE_DIR.mkdir(parents=True, exist_ok=True)
                self._state_file.write_text(json.dumps({"width": w, "height": h}))
            except Exception:
                pass
        return False

    def _on_nav_changed(self, _sidebar, page_name: str):
        self.sidebar.set_active(page_name)
        if page_name == "settings":
            window = SettingsWindow(self)
            window.present()
        elif page_name in self._pages:
            self.content.set_visible_child_name(page_name)

    def _on_new_note(self, _sidebar):
        dialog = ComposeDialog(self)
        dialog.connect("submit", self._on_compose_submit)
        dialog.present()

    def _on_compose_submit(self, dialog, text: str):
        settings = Settings.get()
        if settings.get_bool("confirm-before-posting"):
            confirm = ConfirmDialog(
                self,
                title="Post this note?",
                message=text[:100] + ("…" if len(text) > 100 else ""),
                destructive_label="Post",
                destructive=False,
            )
            confirm.connect("confirm", lambda _: self._do_publish(text))
            confirm.present()
        else:
            self._do_publish(text)

    def _do_publish(self, text: str):
        if not self._key_manager.has_key:
            ErrorDialog(self, title="No identity", message="Set up your key first.").present()
            return
        from echo.services.event_signer import EventSigner
        from echo.services.nostr_client import NostrClient
        try:
            keys = self._key_manager.keys
            signer = EventSigner(keys)
            event = signer.sign_text_note(text)
            client = NostrClient()
            client.publish_event(event)
        except Exception:
            ErrorDialog(self, title="Failed to post", message="Could not publish your note. Check your relay connection.").present()

    def _on_account_switch(self, _sidebar):
        popover = AccountSwitcherPopover()
        popover.set_parent(self.sidebar)
        popover.connect("add-account", self._on_add_account)
        popover.popup()

    def _on_add_account(self, _popover):
        import_view = ImportKeyView()
        window = Adw.Window(transient_for=self, modal=True)
        window.set_title("Import Existing Key")
        window.set_default_size(560, 400)
        window.set_content(import_view)
        import_view.connect("import-key", self._on_import_key_from_switcher)
        import_view.connect("back", lambda v: window.close())
        window.present()

    def _on_import_key_from_switcher(self, _view, key: str):
        if self._key_manager.import_key(key):
            self._key_manager.save_to_keyring()

    def _on_feed_refresh(self, feed):
        feed.show_loading(True)
        if self._key_manager.has_key:
            from nostr_sdk import Filter, Kind, PublicKey
            client = NostrClient()
            f = Filter().kinds([Kind(1)]).limit(20)
            client.subscribe(f, self._on_event_received)

    def _on_discover_search(self, _page, query: str):
        if not self._key_manager.has_key:
            return
        from nostr_sdk import Filter, Kind
        client = NostrClient()
        f = Filter().kinds([Kind(1)]).search(query).limit(50)
        client.subscribe(f, self._on_discover_result)

    def _on_discover_trending_tag(self, _page, tag: str):
        if not self._key_manager.has_key:
            return
        from nostr_sdk import Filter, Kind
        client = NostrClient()
        f = Filter().kinds([Kind(1)]).hashtag(tag.lstrip("#")).limit(50)
        client.subscribe(f, self._on_discover_result)

    def _on_discover_result(self, event):
        from echo.models.note import Note
        from echo.models.profile import Profile

        pubkey = event.pubkey().to_hex()
        profile = Profile(pubkey=pubkey)

        note = Note(
            id=event.id().to_hex(),
            pubkey=pubkey,
            content=event.content(),
            kind=event.kind().as_u16(),
            created_at=event.created_at().as_u64(),
            profile=profile,
        )

        card = NoteCard(note)
        card.connect("reply", self._on_note_reply)
        card.connect("profile-clicked", self._on_note_profile_clicked)
        card.connect("zap", self._on_note_zap)

        discover = self._pages.get("discover")
        if isinstance(discover, DiscoverView):
            discover.add_result(card)

    def _on_bookmarks_load(self, _page):
        if not self._key_manager.has_key:
            return
        bookmarks = self._pages.get("bookmarks")
        if isinstance(bookmarks, BookmarksView):
            bookmarks.show_loading(True)
            bookmarks.clear()
        from nostr_sdk import Filter, Kind, PublicKey
        client = NostrClient()
        pk = self._key_manager.pubkey
        if pk:
            pubkey = PublicKey.parse(pk)
            f = Filter().kinds([Kind(34)]).authors([pubkey]).limit(10)
            client.subscribe(f, self._on_bookmarks_list_received)

    def _on_bookmarks_list_received(self, event):
        from nostr_sdk import EventId, Filter
        ids = []
        for tag in event.tags().to_vec():
            t = tag.as_vec()
            if len(t) >= 2 and t[0] == "e":
                try:
                    ids.append(EventId.parse(t[1]))
                except Exception:
                    pass
        if ids:
            f = Filter().ids(ids).limit(50)
            client = NostrClient()
            client.subscribe(f, self._on_bookmark_event_received)
        else:
            bookmarks = self._pages.get("bookmarks")
            if isinstance(bookmarks, BookmarksView):
                bookmarks.show_loading(False)

    def _on_bookmark_event_received(self, event):
        from echo.models.note import Note
        from echo.models.profile import Profile

        pubkey = event.pubkey().to_hex()
        profile = Profile(pubkey=pubkey)

        note = Note(
            id=event.id().to_hex(),
            pubkey=pubkey,
            content=event.content(),
            kind=event.kind().as_u16(),
            created_at=event.created_at().as_u64(),
            profile=profile,
        )

        card = NoteCard(note)
        card.connect("reply", self._on_note_reply)
        card.connect("profile-clicked", self._on_note_profile_clicked)
        card.connect("zap", self._on_note_zap)

        bookmarks = self._pages.get("bookmarks")
        if isinstance(bookmarks, BookmarksView):
            bookmarks.add_bookmark(card)
            bookmarks.show_loading(False)

    def _on_event_received(self, event):
        from echo.models.note import Note
        from echo.models.profile import Profile

        pubkey = event.pubkey().to_hex()
        profile = Profile(pubkey=pubkey)

        note = Note(
            id=event.id().to_hex(),
            pubkey=pubkey,
            content=event.content(),
            kind=event.kind().as_u16(),
            created_at=event.created_at().as_u64(),
            profile=profile,
        )

        card = NoteCard(note)
        card.connect("reply", self._on_note_reply)
        card.connect("profile-clicked", self._on_note_profile_clicked)
        card.connect("zap", self._on_note_zap)

        feed = self._pages.get("feed")
        if isinstance(feed, FeedView):
            feed.add_note(card)
            feed.show_loading(False)

    def _on_note_reply(self, card):
        thread = self._pages.get("thread")
        if isinstance(thread, ThreadView):
            if hasattr(card, "_note"):
                thread.set_root_note(card._note)
            self.content.set_visible_child_name("thread")

    def _on_note_profile_clicked(self, card, pubkey: str):
        existing = self._pages.get("profile")
        if existing is not None:
            self.content.remove(existing)
            del self._pages["profile"]
        own_pk = self._key_manager.pubkey or ""
        cached = self._profile_service.get_cached(pubkey)
        view = ProfileView(profile=cached, own_pubkey=own_pk)
        view.connect("back", lambda _v: self.content.set_visible_child_name("feed"))
        view.connect("follow", lambda _v: self._on_profile_follow(view, pubkey))
        view.connect("tab-changed", lambda _v, tab: self._on_profile_tab_changed(view, tab))
        self._pages["profile"] = view
        self.content.add_named(view, "profile")
        self.content.set_visible_child_name("profile")
        if not cached or True:
            self._profile_service.fetch_profile(pubkey, lambda p: view.set_profile(p))

    def _on_profile_follow(self, view, pubkey: str):
        pass

    def _on_profile_tab_changed(self, view, tab: str):
        view.clear_content()
        if tab == "notes":
            pass
        elif tab == "replies":
            pass
        elif tab == "media":
            pass
        elif tab == "zapped":
            pass

    def _on_note_zap(self, card):
        profile = card._note.profile if hasattr(card, "_note") else None
        name = profile.name or profile.handle if profile else ""
        dialog = ZapDialog(self, recipient_name=name)
        dialog.present()

    def _on_dm_conversation_selected(self, _list, pubkey: str):
        conv = self._pages.get("dm-conversation")
        if not isinstance(conv, DMConversationView):
            return
        conv.clear_messages()
        profile = self._profile_service.get_cached(pubkey)
        name = profile.handle if profile else ""
        conv.set_contact(name=name, pubkey=pubkey)
        self.content.set_visible_child_name("dm-conversation")

    def _on_dm_new_conversation(self, _list):
        window = Adw.Window(transient_for=self, modal=True)
        window.set_title("New Conversation")
        window.set_default_size(400, 200)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_start(16)
        content.set_margin_end(16)
        content.set_margin_top(16)
        content.set_margin_bottom(16)

        label = Gtk.Label(label="Enter the recipient's npub or hex public key")
        label.set_wrap(True)
        content.append(label)

        entry = Gtk.Entry()
        entry.set_placeholder_text("npub1... or hex key")
        entry.set_width_chars(50)
        content.append(entry)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda _: window.close())
        actions.append(cancel_btn)

        start_btn = Gtk.Button(label="Start conversation")
        start_btn.add_css_class("suggested-action")
        start_btn.connect("clicked", lambda _: self._on_dm_start(window, entry))
        actions.append(start_btn)
        content.append(actions)

        entry.connect("activate", lambda: self._on_dm_start(window, entry))
        window.set_content(content)
        window.present()

    def _on_dm_start(self, window, entry):
        raw = entry.get_text().strip()
        if not raw:
            return
        from nostr_sdk import PublicKey
        try:
            pk = PublicKey.parse(raw)
            pubkey = pk.to_hex()
        except Exception:
            return
        window.close()
        conv = self._pages.get("dm-conversation")
        if isinstance(conv, DMConversationView):
            conv.clear_messages()
            conv.set_contact(name="", pubkey=pubkey)
            self.content.set_visible_child_name("dm-conversation")

    def _on_dm_send_message(self, conv, text: str):
        if not self._key_manager.has_key:
            return
        pubkey = conv._contact_pubkey if hasattr(conv, "_contact_pubkey") else ""
        if not pubkey:
            return
        from nostr_sdk import PublicKey
        from echo.services.nostr_client import NostrClient
        try:
            receiver = PublicKey.parse(pubkey)
            client = NostrClient()
            client.send_private_msg(receiver, text)
        except Exception:
            pass

    def _on_contacts_load(self, _view):
        if not self._key_manager.has_key:
            return
        contacts = self._pages.get("contacts")
        if isinstance(contacts, ContactsView):
            contacts.clear()
            contacts.show_loading(True)
        from nostr_sdk import Filter, Kind, PublicKey
        client = NostrClient()
        pk = self._key_manager.pubkey
        if pk:
            pubkey = PublicKey.parse(pk)
            f = Filter().kinds([Kind(3)]).authors([pubkey]).limit(1)
            client.subscribe(f, self._on_contact_list_received)
            mute_f = Filter().kinds([Kind(10000)]).authors([pubkey]).limit(1)
            client.subscribe(mute_f, self._on_mute_list_received)

    def _on_contact_list_received(self, event):
        contact_pubkeys = []
        for tag in event.tags().to_vec():
            t = tag.as_vec()
            if len(t) >= 2 and t[0] == "p":
                contact_pubkeys.append(t[1])
        contacts = self._pages.get("contacts")
        if isinstance(contacts, ContactsView):
            contacts.set_following(set(contact_pubkeys))
        for pk in contact_pubkeys:
            self._profile_service.fetch_profile(pk, self._on_contact_profile_received)

    def _on_contact_profile_received(self, profile):
        contacts = self._pages.get("contacts")
        if isinstance(contacts, ContactsView):
            contacts.add_profile(profile)
            contacts.show_loading(False)

    def _on_mute_list_received(self, event):
        muted = set()
        for tag in event.tags().to_vec():
            t = tag.as_vec()
            if len(t) >= 2 and t[0] == "p":
                muted.add(t[1])
        contacts = self._pages.get("contacts")
        if isinstance(contacts, ContactsView):
            contacts.set_muted(muted)

    def _on_contacts_add(self, _view):
        window = Adw.Window(transient_for=self, modal=True)
        window.set_title("Add Contact")
        window.set_default_size(400, 200)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_start(16)
        content.set_margin_end(16)
        content.set_margin_top(16)
        content.set_margin_bottom(16)

        label = Gtk.Label(label="Enter the npub or hex public key of the contact to add")
        label.set_wrap(True)
        content.append(label)

        entry = Gtk.Entry()
        entry.set_placeholder_text("npub1... or hex key")
        entry.set_width_chars(50)
        content.append(entry)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda _: window.close())
        actions.append(cancel_btn)

        add_btn = Gtk.Button(label="Add Contact")
        add_btn.add_css_class("suggested-action")
        add_btn.connect("clicked", lambda _: self._on_contacts_add_submit(window, entry))
        actions.append(add_btn)
        content.append(actions)

        entry.connect("activate", lambda: self._on_contacts_add_submit(window, entry))
        window.set_content(content)
        window.present()

    def _on_contacts_add_submit(self, window, entry):
        raw = entry.get_text().strip()
        if not raw:
            return
        from nostr_sdk import PublicKey
        try:
            pk = PublicKey.parse(raw)
            pubkey = pk.to_hex()
        except Exception:
            return
        window.close()
        contact_pubkeys = set()
        contacts_view = self._pages.get("contacts")
        if isinstance(contacts_view, ContactsView):
            contact_pubkeys = set(contacts_view._following)
        contact_pubkeys.add(pubkey)
        self._publish_contact_list(contact_pubkeys)
        self._profile_service.fetch_profile(pubkey, self._on_contact_profile_received)

    def _on_contacts_follow(self, _view, pubkey: str):
        contacts_view = self._pages.get("contacts")
        if not isinstance(contacts_view, ContactsView):
            return
        following = set(contacts_view._following)
        following.add(pubkey)
        self._publish_contact_list(following)

    def _on_contacts_unfollow(self, _view, pubkey: str):
        contacts_view = self._pages.get("contacts")
        if not isinstance(contacts_view, ContactsView):
            return
        following = set(contacts_view._following)
        following.discard(pubkey)
        self._publish_contact_list(following)

    def _publish_contact_list(self, pubkeys: set[str]):
        if not self._key_manager.has_key:
            return
        from echo.services.event_signer import EventSigner
        from echo.services.nostr_client import NostrClient
        contacts_with_relays = [(pk, "", "") for pk in pubkeys]
        try:
            keys = self._key_manager.keys
            signer = EventSigner(keys)
            event = signer.sign_contact_list(contacts_with_relays)
            client = NostrClient()
            client.publish_event(event)
        except Exception:
            pass

    def _on_contacts_mute(self, _view, pubkey: str):
        contacts_view = self._pages.get("contacts")
        if not isinstance(contacts_view, ContactsView):
            return
        muted = set(contacts_view._muted)
        muted.add(pubkey)
        contacts_view.set_muted(muted)
        self._publish_mute_list(muted)

    def _on_contacts_unmute(self, _view, pubkey: str):
        contacts_view = self._pages.get("contacts")
        if not isinstance(contacts_view, ContactsView):
            return
        muted = set(contacts_view._muted)
        muted.discard(pubkey)
        contacts_view.set_muted(muted)
        self._publish_mute_list(muted)

    def _publish_mute_list(self, muted: set[str]):
        if not self._key_manager.has_key:
            return
        from nostr_sdk import Kind, Tag, EventBuilder
        from echo.services.nostr_client import NostrClient
        try:
            keys = self._key_manager.keys
            tags = [Tag.parse(["p", pk]) for pk in muted]
            builder = EventBuilder(Kind(10000), "").tags(tags)
            event = builder.sign_with_keys(keys)
            client = NostrClient()
            client.publish_event(event)
        except Exception:
            pass

    def _on_contacts_block(self, _view, pubkey: str):
        contacts_view = self._pages.get("contacts")
        if not isinstance(contacts_view, ContactsView):
            return
        blocked = set(contacts_view._blocked)
        blocked.add(pubkey)
        contacts_view.set_blocked(blocked)

    def _on_contacts_unblock(self, _view, pubkey: str):
        contacts_view = self._pages.get("contacts")
        if not isinstance(contacts_view, ContactsView):
            return
        blocked = set(contacts_view._blocked)
        blocked.discard(pubkey)
        contacts_view.set_blocked(blocked)
