import copy


class MacroEditor:
    """Pure data-layer for editing macro events.
    Operates on the same dict reference as Macro.macro_events."""

    def __init__(self, macro):
        self.macro = macro
        self._clipboard = []

    @property
    def events(self):
        return self.macro.macro_events.get("events", [])

    def has_events(self):
        return len(self.events) > 0

    def get_event(self, index):
        if 0 <= index < len(self.events):
            return self.events[index]
        return None

    def insert_event(self, index, event_dict):
        self.events.insert(index, event_dict)
        self._mark_unsaved()

    def delete_events(self, indices):
        for i in sorted(indices, reverse=True):
            if 0 <= i < len(self.events):
                self.events.pop(i)
        self._mark_unsaved()

    def move_event(self, from_index, to_index):
        if from_index == to_index:
            return
        if not (0 <= from_index < len(self.events)):
            return
        to_index = max(0, min(to_index, len(self.events) - 1))
        event = self.events.pop(from_index)
        self.events.insert(to_index, event)
        self._mark_unsaved()

    def update_event(self, index, field, value):
        if 0 <= index < len(self.events):
            self.events[index][field] = value
            self._mark_unsaved()

    def update_event_fields(self, index, fields_dict):
        if 0 <= index < len(self.events):
            self.events[index].update(fields_dict)
            self._mark_unsaved()

    def copy_events(self, indices):
        self._clipboard = [copy.deepcopy(self.events[i])
                           for i in sorted(indices)
                           if 0 <= i < len(self.events)]

    def paste_events(self, insert_index):
        if not self._clipboard:
            return 0
        copies = copy.deepcopy(self._clipboard)
        for i, event in enumerate(copies):
            self.events.insert(insert_index + i, event)
        self._mark_unsaved()
        return len(copies)

    def has_clipboard(self):
        return len(self._clipboard) > 0

    def _mark_unsaved(self):
        self.macro.main_app.macro_saved = False
