from sys import platform
from tkinter import BOTH, BOTTOM, END, LEFT, Menu, RIGHT, VERTICAL, X, Y
from tkinter.ttk import Entry, Frame, Scrollbar, Style, Treeview

from windows.main.event_detail_panel import EventDetailPanel


EVENT_TYPE_LABELS = {
    "cursorMove": "Cursor Move",
    "leftClickEvent": "Left Click",
    "rightClickEvent": "Right Click",
    "middleClickEvent": "Middle Click",
    "scrollEvent": "Scroll",
    "keyboardEvent": "Keyboard",
}

# Tag name -> event types that use it
EVENT_TYPE_TAGS = {
    "mouse_move": ("cursorMove",),
    "mouse_click": ("leftClickEvent", "rightClickEvent", "middleClickEvent"),
    "scroll": ("scrollEvent",),
    "keyboard": ("keyboardEvent",),
}


class EventEditor(Frame):
    """Treeview-based macro event editor with inline editing and detail panel."""

    def __init__(self, main_app):
        super().__init__(main_app)
        self.main_app = main_app
        self.macro = main_app.macro
        self._inline_entry = None
        self._drag_data = {"item": None, "start_y": 0}

        text = main_app.text_content.get("editor", {})

        # Treeview frame
        tree_frame = Frame(self)
        tree_frame.pack(fill=BOTH, expand=True)

        columns = ("index", "type", "params", "delay")
        self.tree = Treeview(
            tree_frame, columns=columns, show="headings", selectmode="extended"
        )
        self.tree.heading("index", text=text.get("column_index", "#"))
        self.tree.heading("type", text=text.get("column_type", "Type"))
        self.tree.heading("params", text=text.get("column_params", "Parameters"))
        self.tree.heading("delay", text=text.get("column_delay", "Delay (s)"))

        self.tree.column("index", width=50, minwidth=40, stretch=False)
        self.tree.column("type", width=120, minwidth=80, stretch=False)
        self.tree.column("params", width=250, minwidth=120)
        self.tree.column("delay", width=90, minwidth=60, stretch=False)

        scrollbar = Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Row coloring by event type
        self.tree.tag_configure("mouse_move", background="#e8f0fe")
        self.tree.tag_configure("mouse_click", background="#fce8e6")
        self.tree.tag_configure("scroll", background="#fef7e0")
        self.tree.tag_configure("keyboard", background="#e6f4ea")

        # Detail panel at bottom
        self.detail_panel = EventDetailPanel(self, main_app)
        self.detail_panel.pack(side=BOTTOM, fill=X)

        # Context menu
        self._context_menu = Menu(self.tree, tearoff=0)
        editor_text = text
        self._context_menu.add_command(
            label=editor_text.get("insert_event", "Insert Event"),
            command=self.insert_event_at_selection,
        )
        self._context_menu.add_command(
            label=editor_text.get("delete_event", "Delete"),
            command=self.delete_selected,
        )
        self._context_menu.add_separator()
        self._context_menu.add_command(
            label=editor_text.get("copy", "Copy"),
            command=self.copy_selected,
        )
        self._context_menu.add_command(
            label=editor_text.get("paste", "Paste"),
            command=self.paste_at_selection,
        )
        self._context_menu.add_separator()
        self._context_menu.add_command(
            label=editor_text.get("move_up", "Move Up"),
            command=self.move_selected_up,
        )
        self._context_menu.add_command(
            label=editor_text.get("move_down", "Move Down"),
            command=self.move_selected_down,
        )

        # Bindings
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Delete>", lambda e: self.delete_selected())
        self.tree.bind("<Control-c>", lambda e: self.copy_selected())
        self.tree.bind("<Control-v>", lambda e: self.paste_at_selection())
        self.tree.bind("<Control-i>", lambda e: self.insert_event_at_selection())

        # Right-click context menu
        if platform == "darwin":
            self.tree.bind("<Button-2>", self._show_context_menu)
        else:
            self.tree.bind("<Button-3>", self._show_context_menu)

        # Drag-and-drop
        self.tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.tree.bind("<B1-Motion>", self._on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self._on_drag_end)

    # ── Refresh / Display ────────────────────────────────────────────

    def refresh(self):
        """Reload all events from macro_events into the treeview."""
        self._cancel_inline_edit()
        self.detail_panel.clear()
        self.tree.delete(*self.tree.get_children())
        events = self.macro.macro_events.get("events", [])
        for i, event in enumerate(events):
            self._insert_tree_row(i, event)

    def refresh_row(self, index):
        """Update a single row in the treeview."""
        events = self.macro.macro_events.get("events", [])
        if index < 0 or index >= len(events):
            return
        iid = str(index)
        event = events[index]
        values = self._event_to_values(index, event)
        tag = self._get_event_tag(event.get("type", ""))
        if self.tree.exists(iid):
            self.tree.item(iid, values=values, tags=(tag,) if tag else ())
        else:
            self.refresh()

    def _insert_tree_row(self, index, event):
        values = self._event_to_values(index, event)
        tag = self._get_event_tag(event.get("type", ""))
        self.tree.insert("", END, iid=str(index), values=values, tags=(tag,) if tag else ())

    @staticmethod
    def _get_event_tag(event_type):
        for tag, types in EVENT_TYPE_TAGS.items():
            if event_type in types:
                return tag
        return None

    def _event_to_values(self, index, event):
        etype = event.get("type", "")
        label = EVENT_TYPE_LABELS.get(etype, etype)
        params = self._format_params(event)
        delay = f"{event.get('timestamp', 0):.3f}"
        return (index + 1, label, params, delay)

    @staticmethod
    def _format_params(event):
        t = event.get("type", "")
        if t == "cursorMove":
            return f"({event.get('x', '?')}, {event.get('y', '?')})"
        elif t in ("leftClickEvent", "rightClickEvent", "middleClickEvent"):
            action = "Press" if event.get("pressed") else "Release"
            return f"({event.get('x', '?')}, {event.get('y', '?')}) {action}"
        elif t == "scrollEvent":
            return f"dx={event.get('dx', 0)}, dy={event.get('dy', 0)}"
        elif t == "keyboardEvent":
            action = "Press" if event.get("pressed") else "Release"
            key = event.get("key", "?")
            # Clean up key display
            if key and key.startswith("Key."):
                key = key[4:].capitalize()
            return f"{key} {action}"
        return ""

    # ── Selection ────────────────────────────────────────────────────

    def _on_select(self, event=None):
        selected = self.tree.selection()
        if selected:
            index = int(selected[0])
            evt = self.main_app.macro_editor.get_event(index)
            if evt:
                self.detail_panel.show_event(index, evt)
        else:
            self.detail_panel.clear()

    def get_selected_indices(self):
        return [int(s) for s in self.tree.selection()]

    # ── Inline Editing ───────────────────────────────────────────────

    def _on_double_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        column = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        if not item:
            return

        col_index = int(column.replace("#", "")) - 1
        # Only allow editing delay column (index 3)
        if col_index != 3:
            return

        bbox = self.tree.bbox(item, column)
        if not bbox:
            return

        self._cancel_inline_edit()

        x, y, w, h = bbox
        entry = Entry(self.tree)
        entry.place(x=x, y=y, width=w, height=h)

        current_value = self.tree.set(item, column)
        entry.insert(0, current_value)
        entry.select_range(0, END)
        entry.focus_set()

        self._inline_entry = entry
        self._inline_item = item
        self._inline_col = col_index

        entry.bind("<Return>", lambda e: self._commit_inline_edit())
        entry.bind("<Escape>", lambda e: self._cancel_inline_edit())
        entry.bind("<FocusOut>", lambda e: self._commit_inline_edit())

    def _commit_inline_edit(self):
        if self._inline_entry is None:
            return
        new_value = self._inline_entry.get()
        item = self._inline_item
        col = self._inline_col
        self._inline_entry.destroy()
        self._inline_entry = None

        index = int(item)
        if col == 3:  # delay
            try:
                delay = float(new_value)
                self.main_app.macro_editor.update_event(index, "timestamp", delay)
                self.refresh_row(index)
            except ValueError:
                pass

    def _cancel_inline_edit(self):
        if self._inline_entry is not None:
            self._inline_entry.destroy()
            self._inline_entry = None

    # ── Editor Actions ───────────────────────────────────────────────

    def insert_event_at_selection(self):
        from windows.main.insert_event_dialog import InsertEventDialog

        selected = self.get_selected_indices()
        insert_at = selected[-1] + 1 if selected else len(self.main_app.macro_editor.events)
        InsertEventDialog(self.main_app, insert_at)

    def delete_selected(self):
        indices = self.get_selected_indices()
        if indices:
            self.main_app.macro_editor.delete_events(indices)
            self.refresh()

    def move_selected_up(self):
        indices = self.get_selected_indices()
        if not indices or min(indices) == 0:
            return
        # Move each selected event up by 1
        for idx in sorted(indices):
            self.main_app.macro_editor.move_event(idx, idx - 1)
        self.refresh()
        # Re-select moved items
        new_selection = [str(i - 1) for i in sorted(indices)]
        for iid in new_selection:
            if self.tree.exists(iid):
                self.tree.selection_add(iid)

    def move_selected_down(self):
        indices = self.get_selected_indices()
        num_events = len(self.main_app.macro_editor.events)
        if not indices or max(indices) >= num_events - 1:
            return
        for idx in sorted(indices, reverse=True):
            self.main_app.macro_editor.move_event(idx, idx + 1)
        self.refresh()
        new_selection = [str(i + 1) for i in sorted(indices)]
        for iid in new_selection:
            if self.tree.exists(iid):
                self.tree.selection_add(iid)

    def copy_selected(self):
        indices = self.get_selected_indices()
        if indices:
            self.main_app.macro_editor.copy_events(indices)

    def paste_at_selection(self):
        if not self.main_app.macro_editor.has_clipboard():
            return
        selected = self.get_selected_indices()
        insert_at = selected[-1] + 1 if selected else len(self.main_app.macro_editor.events)
        count = self.main_app.macro_editor.paste_events(insert_at)
        self.refresh()
        # Select pasted items
        for i in range(insert_at, insert_at + count):
            iid = str(i)
            if self.tree.exists(iid):
                self.tree.selection_add(iid)

    # ── Drag and Drop ────────────────────────────────────────────────

    def _on_drag_start(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self._drag_data["item"] = item
            self._drag_data["start_y"] = event.y

    def _on_drag_motion(self, event):
        if self._drag_data["item"] is None:
            return
        # Only start visual drag if moved enough
        if abs(event.y - self._drag_data["start_y"]) < 8:
            return
        target = self.tree.identify_row(event.y)
        if target and target != self._drag_data["item"]:
            self.tree.selection_set(self._drag_data["item"])

    def _on_drag_end(self, event):
        source = self._drag_data["item"]
        self._drag_data["item"] = None
        if source is None:
            return
        # Only process drag if moved enough
        if abs(event.y - self._drag_data["start_y"]) < 8:
            return
        target = self.tree.identify_row(event.y)
        if target and source != target:
            from_idx = int(source)
            to_idx = int(target)
            self.main_app.macro_editor.move_event(from_idx, to_idx)
            self.refresh()
            # Select the moved item
            new_iid = str(to_idx)
            if self.tree.exists(new_iid):
                self.tree.selection_set(new_iid)

    # ── Context Menu ──────────────────────────────────────────────────

    def _show_context_menu(self, event):
        """Show right-click context menu."""
        # Select row under cursor if not already selected
        item = self.tree.identify_row(event.y)
        if item and item not in self.tree.selection():
            self.tree.selection_set(item)
        try:
            self._context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._context_menu.grab_release()

    # ── State Management ─────────────────────────────────────────────

    def update_state(self, state):
        """Enable/disable editor based on app state."""
        if state in ("recording", "playing"):
            self.tree.configure(selectmode="none")
            self._cancel_inline_edit()
            self.detail_panel.clear()
        else:
            self.tree.configure(selectmode="extended")
