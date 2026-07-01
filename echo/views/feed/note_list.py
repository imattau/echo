import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk


class NoteList(Gtk.ListBox):
    def __init__(self):
        super().__init__()
        self.set_selection_mode(Gtk.SelectionMode.NONE)

    def add_note(self, note_card):
        self.append(note_card)

    def clear(self):
        row = self.get_first_child()
        while row:
            next_row = row.get_next_sibling()
            self.remove(row)
            row = next_row
