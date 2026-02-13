from sys import platform
from tkinter import BOTH, BOTTOM, END, LEFT, Menu, RIGHT, TOP, VERTICAL, X, Y, BooleanVar, StringVar
from tkinter.ttk import Button, Checkbutton, Entry, Frame, Label, Scrollbar, Treeview

from windows.main.event_detail_panel import EventDetailPanel
from windows.theme import COLORS, FONTS


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

# Filter key -> which tags it matches
_FILTER_TAG_MAP = {
    "moves": ("mouse_move",),
    "clicks": ("mouse_click",),
    "scroll": ("scroll",),
    "keyboard": ("keyboard",),
    "paths": ("mouse_path_group",),
}


class EventEditor(Frame):
    """Treeview-based macro event editor with grouped mouse path display."""

    def __init__(self, main_app):
        super().__init__(main_app)
        self.main_app = main_app
        self.macro = main_app.macro
        self._inline_entry = None
        self._drag_data = {"item": None, "start_y": 0}

        # Mapping dictionaries for grouped display
        self._group_items = {}       # group_iid -> {"start": int, "end": int, "count": int}
        self._index_to_iid = {}      # event_index -> treeview iid
        self._iid_to_index = {}      # treeview iid -> event_index

        # All top-level iids in display order (for filter detach/reattach)
        self._all_top_iids = []
        # Currently detached (hidden) iids
        self._detached_iids = set()

        text = main_app.text_content.get("editor", {})

        # ── Filter bar ────────────────────────────────────────────────
        self._filter_bar = Frame(self, style="FilterBar.TFrame")
        self._filter_bar.pack(side=TOP, fill=X)

        # Guard: trace callbacks fire during construction, skip until ready
        self._filter_ready = False

        # Search entry
        self._search_var = StringVar()
        self._search_var.trace_add("write", self._on_filter_change)
        self._search_entry = Entry(
            self._filter_bar, textvariable=self._search_var, width=20,
        )
        self._search_entry.pack(side=LEFT, padx=(6, 4), pady=4)
        # Placeholder text
        self._search_placeholder = text.get(
            "search_placeholder", "Search events... (Ctrl+F)"
        )
        self._search_entry.insert(0, self._search_placeholder)
        self._search_entry.configure(foreground=COLORS["text_disabled"])
        self._search_has_focus = False
        self._search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self._search_entry.bind("<FocusOut>", self._on_search_focus_out)

        # Type filter checkboxes — all checked by default
        self._filter_vars = {}
        for key, label_key, default_label in (
            ("moves", "filter_moves", "Moves"),
            ("clicks", "filter_clicks", "Clicks"),
            ("scroll", "filter_scroll", "Scroll"),
            ("keyboard", "filter_keyboard", "Keyboard"),
            ("paths", "filter_paths", "Paths"),
        ):
            var = BooleanVar(value=True)
            var.trace_add("write", self._on_filter_change)
            self._filter_vars[key] = var
            Checkbutton(
                self._filter_bar,
                text=text.get(label_key, default_label),
                variable=var,
                style="Filter.TCheckbutton",
            ).pack(side=LEFT, padx=2, pady=4)

        # Clear button
        self._clear_btn = Button(
            self._filter_bar,
            text=text.get("clear_filter", "Clear"),
            command=self._clear_filters,
            style="ToolbarText.TButton",
        )
        self._clear_btn.pack(side=LEFT, padx=(4, 2), pady=4)

        # Filter status label (right-aligned)
        self._filter_status_var = StringVar()
        self._filter_status = Label(
            self._filter_bar,
            textvariable=self._filter_status_var,
            style="FilterBar.TLabel",
        )
        self._filter_status.pack(side=RIGHT, padx=(0, 6), pady=4)

        self._filter_ready = True  # Filter bar fully constructed

        # ── Treeview ──────────────────────────────────────────────────
        tree_frame = Frame(self)
        tree_frame.pack(fill=BOTH, expand=True)

        columns = ("index", "type", "params", "delay")
        self.tree = Treeview(
            tree_frame, columns=columns, show="tree headings", selectmode="extended"
        )
        # Column #0 for expand/collapse arrows
        self.tree.column("#0", width=30, minwidth=20, stretch=False)
        self.tree.heading("#0", text="")

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
        self.tree.tag_configure("mouse_move", background=COLORS["tag_mouse_move"])
        self.tree.tag_configure("mouse_click", background=COLORS["tag_mouse_click"])
        self.tree.tag_configure("scroll", background=COLORS["tag_scroll"])
        self.tree.tag_configure("keyboard", background=COLORS["tag_keyboard"])
        self.tree.tag_configure("mouse_path_group", background=COLORS["tag_mouse_path_group"])

        # Detail panel at bottom
        self.detail_panel = EventDetailPanel(self, main_app)
        self.detail_panel.pack(side=BOTTOM, fill=X)

        # Context menu (tk.Menu — styled via constructor args)
        self._context_menu = Menu(
            self.tree, tearoff=0,
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            activebackground=COLORS["accent"],
            activeforeground=COLORS["text_inverse"],
            font=FONTS["default"],
            relief="flat",
            borderwidth=1,
        )
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
        self._context_menu.add_separator()
        self._simplify_menu_index = 8  # index of simplify item in context menu
        self._context_menu.add_command(
            label=editor_text.get("simplify_path", "Simplify Path..."),
            command=self._on_simplify_path,
        )

        # Bindings
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Delete>", lambda e: self.delete_selected())
        self.tree.bind("<Control-c>", lambda e: self.copy_selected())
        self.tree.bind("<Control-v>", lambda e: self.paste_at_selection())
        self.tree.bind("<Control-i>", lambda e: self.insert_event_at_selection())
        self.tree.bind("<Control-f>", lambda e: self._focus_search())

        # Also bind Ctrl+F at the frame level
        self.bind("<Control-f>", lambda e: self._focus_search())

        # Right-click context menu
        if platform == "darwin":
            self.tree.bind("<Button-2>", self._show_context_menu)
        else:
            self.tree.bind("<Button-3>", self._show_context_menu)

        # Drag-and-drop
        self.tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.tree.bind("<B1-Motion>", self._on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self._on_drag_end)

        # Lazy expand/collapse for groups
        self.tree.bind("<<TreeviewOpen>>", self._on_group_expand)
        self.tree.bind("<<TreeviewClose>>", self._on_group_collapse)

    # ── Search bar helpers ────────────────────────────────────────────

    def _focus_search(self):
        self._search_entry.focus_set()

    def _on_search_focus_in(self, event=None):
        if not self._search_has_focus:
            self._search_has_focus = True
            if self._search_var.get() == self._search_placeholder:
                self._search_entry.delete(0, END)
                self._search_entry.configure(foreground=COLORS["text_primary"])

    def _on_search_focus_out(self, event=None):
        self._search_has_focus = False
        if not self._search_var.get():
            self._search_entry.configure(foreground=COLORS["text_disabled"])
            self._search_entry.insert(0, self._search_placeholder)

    def _get_search_text(self):
        """Return search text, or empty string if placeholder is showing."""
        val = self._search_var.get()
        if val == self._search_placeholder:
            return ""
        return val.strip().lower()

    def _clear_filters(self):
        """Reset search text and check all filter boxes."""
        # Reset search
        self._search_has_focus = False
        self._search_var.set("")
        self._search_entry.configure(foreground=COLORS["text_disabled"])
        self._search_entry.insert(0, self._search_placeholder)
        # Check all filters
        for var in self._filter_vars.values():
            var.set(True)

    # ── Filter logic ──────────────────────────────────────────────────

    def _on_filter_change(self, *_args):
        """Called when search text or filter checkboxes change."""
        if not self._filter_ready:
            return
        self._apply_filter()

    def _apply_filter(self):
        """Show/hide top-level treeview items based on current filters."""
        search = self._get_search_text()
        # Build set of allowed tags from checked filters
        allowed_tags = set()
        for key, var in self._filter_vars.items():
            if var.get():
                allowed_tags.update(_FILTER_TAG_MAP[key])

        # Reattach all previously detached items first
        # We need to reattach in original order
        if self._detached_iids:
            for iid in self._all_top_iids:
                if iid in self._detached_iids:
                    # Find the correct position: after the previous visible sibling
                    idx = self._all_top_iids.index(iid)
                    if idx == 0:
                        self.tree.reattach(iid, "", 0)
                    else:
                        # Find the previous iid that is currently attached
                        prev = ""
                        for j in range(idx - 1, -1, -1):
                            if self._all_top_iids[j] not in self._detached_iids:
                                prev = self._all_top_iids[j]
                                break
                        if prev:
                            self.tree.move(iid, "", self.tree.index(prev) + 1)
                        else:
                            self.tree.reattach(iid, "", 0)
            self._detached_iids.clear()

        total = len(self._all_top_iids)
        shown = total

        # Now detach items that don't match
        for iid in self._all_top_iids:
            if not self._item_matches_filter(iid, search, allowed_tags):
                self.tree.detach(iid)
                self._detached_iids.add(iid)
                shown -= 1

        # Update status label
        if shown < total:
            tmpl = self.main_app.text_content.get("editor", {}).get(
                "showing_filtered", "Showing {shown} of {total} events"
            )
            self._filter_status_var.set(
                tmpl.format(shown=shown, total=total)
            )
        else:
            self._filter_status_var.set("")

    def _item_matches_filter(self, iid, search, allowed_tags):
        """Check if a top-level item passes current filters."""
        tags = set(self.tree.item(iid, "tags"))

        # Type filter: check if the item's tag is in allowed set
        if tags:
            if not tags.intersection(allowed_tags):
                return False
        # Items with no tag (shouldn't normally happen) always pass type filter

        # Text search
        if search:
            values = self.tree.item(iid, "values")
            text = " ".join(str(v).lower() for v in values)
            if search not in text:
                return False

        return True

    # ── Refresh / Display ────────────────────────────────────────────

    def refresh(self):
        """Reload all events from macro_events into the treeview with grouping."""
        self._cancel_inline_edit()
        self.detail_panel.clear()
        self.tree.delete(*self.tree.get_children())
        self._group_items.clear()
        self._index_to_iid.clear()
        self._iid_to_index.clear()
        self._all_top_iids.clear()
        self._detached_iids.clear()

        events = self.macro.macro_events.get("events", [])
        display_items = self.main_app.macro_editor.get_cursor_move_groups()

        group_counter = 0
        for item in display_items:
            if item["kind"] == "single":
                idx = item["index"]
                iid = f"evt_{idx}"
                event = events[idx]
                values = self._event_to_values(idx, event)
                tag = self._get_event_tag(event.get("type", ""))
                self.tree.insert(
                    "", END, iid=iid, values=values,
                    tags=(tag,) if tag else ()
                )
                self._index_to_iid[idx] = iid
                self._iid_to_index[iid] = idx
                self._all_top_iids.append(iid)

            elif item["kind"] == "group":
                group_iid = f"grp_{group_counter}"
                group_counter += 1

                # Format group summary row (index = start point, 1-based)
                summary = (
                    item["start"] + 1,
                    "Mouse Path",
                    f"({item['start_x']},{item['start_y']}) \u2192 "
                    f"({item['end_x']},{item['end_y']}) "
                    f"[{item['count']} moves]",
                    f"{item['total_time']:.3f}",
                )
                self.tree.insert(
                    "", END, iid=group_iid, values=summary,
                    tags=("mouse_path_group",), open=False,
                )
                self._group_items[group_iid] = {
                    "start": item["start"],
                    "end": item["end"],
                    "count": item["count"],
                }
                self._all_top_iids.append(group_iid)

                # Insert a dummy child so the expand arrow appears
                dummy_iid = f"dummy_{group_iid}"
                self.tree.insert(group_iid, END, iid=dummy_iid, values=("", "", "Loading...", ""))

        # Apply current filter to the newly loaded data
        self._apply_filter()

    def _on_group_expand(self, event=None):
        """Lazy-load children when a group is expanded."""
        selected = self.tree.focus()
        if not selected or selected not in self._group_items:
            return

        group_info = self._group_items[selected]
        dummy_iid = f"dummy_{selected}"

        # Check if dummy still exists (first expand)
        if self.tree.exists(dummy_iid):
            self.tree.delete(dummy_iid)

            events = self.macro.macro_events.get("events", [])
            for idx in range(group_info["start"], group_info["end"] + 1):
                child_iid = f"evt_{idx}"
                event = events[idx]
                values = self._event_to_values(idx, event)
                tag = self._get_event_tag(event.get("type", ""))
                self.tree.insert(
                    selected, END, iid=child_iid, values=values,
                    tags=(tag,) if tag else ()
                )
                self._index_to_iid[idx] = child_iid
                self._iid_to_index[child_iid] = idx

    def _on_group_collapse(self, event=None):
        """Remove children when a group is collapsed to save memory."""
        selected = self.tree.focus()
        if not selected or selected not in self._group_items:
            return

        group_info = self._group_items[selected]

        # Remove children from mappings and tree
        for child_iid in list(self.tree.get_children(selected)):
            if child_iid in self._iid_to_index:
                idx = self._iid_to_index.pop(child_iid)
                self._index_to_iid.pop(idx, None)
            self.tree.delete(child_iid)

        # Re-insert dummy
        dummy_iid = f"dummy_{selected}"
        self.tree.insert(selected, END, iid=dummy_iid, values=("", "", "Loading...", ""))

    def refresh_row(self, index):
        """Update a single row in the treeview."""
        events = self.macro.macro_events.get("events", [])
        if index < 0 or index >= len(events):
            return
        iid = self._index_to_iid.get(index)
        if iid is None:
            # Row not currently visible (group collapsed), skip
            return
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
        iid = f"evt_{index}"
        self.tree.insert("", END, iid=iid, values=values, tags=(tag,) if tag else ())
        self._index_to_iid[index] = iid
        self._iid_to_index[iid] = index

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
        if not selected:
            self.detail_panel.clear()
            return

        iid = selected[0]
        if iid in self._group_items:
            # Group selected — show path summary
            group_info = self._group_items[iid]
            stats = self.main_app.macro_editor.get_path_stats(
                group_info["start"], group_info["end"]
            )
            self.detail_panel.show_group(group_info, stats)
            # Update status bar with path info
            self.main_app.status_text.configure(
                text=f"Mouse Path: {stats['total_moves']} moves, "
                     f"distance: {stats['total_distance']:.0f}px, "
                     f"duration: {stats['total_time']:.3f}s"
            )
        elif iid in self._iid_to_index:
            index = self._iid_to_index[iid]
            evt = self.main_app.macro_editor.get_event(index)
            if evt:
                self.detail_panel.show_event(index, evt)
        else:
            self.detail_panel.clear()

    def get_selected_indices(self):
        """Resolve selected items to event indices, expanding groups."""
        indices = []
        for iid in self.tree.selection():
            if iid in self._group_items:
                g = self._group_items[iid]
                indices.extend(range(g["start"], g["end"] + 1))
            elif iid in self._iid_to_index:
                indices.append(self._iid_to_index[iid])
        return sorted(set(indices))

    # ── Inline Editing ───────────────────────────────────────────────

    def _on_double_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        column = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        if not item:
            return

        # Don't allow inline editing on group headers or dummy rows
        if item.startswith("grp_") or item.startswith("dummy_"):
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

        if item not in self._iid_to_index:
            return
        index = self._iid_to_index[item]
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
        for i in sorted(indices):
            new_iid = self._index_to_iid.get(i - 1)
            if new_iid and self.tree.exists(new_iid):
                self.tree.selection_add(new_iid)

    def move_selected_down(self):
        indices = self.get_selected_indices()
        num_events = len(self.main_app.macro_editor.events)
        if not indices or max(indices) >= num_events - 1:
            return
        for idx in sorted(indices, reverse=True):
            self.main_app.macro_editor.move_event(idx, idx + 1)
        self.refresh()
        for i in sorted(indices):
            new_iid = self._index_to_iid.get(i + 1)
            if new_iid and self.tree.exists(new_iid):
                self.tree.selection_add(new_iid)

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
            iid = self._index_to_iid.get(i)
            if iid and self.tree.exists(iid):
                self.tree.selection_add(iid)

    # ── Simplify Path ─────────────────────────────────────────────────

    def _on_simplify_path(self):
        """Open simplify dialog for the selected group."""
        selected = self.tree.selection()
        if not selected:
            return
        iid = selected[0]
        if iid not in self._group_items:
            return
        group_info = self._group_items[iid]
        from windows.main.simplify_path_dialog import SimplifyPathDialog
        SimplifyPathDialog(self.main_app, group_info["start"], group_info["end"])

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
        if not target or source == target:
            return
        # Don't support dragging group rows or onto group rows
        if (source.startswith("grp_") or source.startswith("dummy_") or
                target.startswith("grp_") or target.startswith("dummy_")):
            return
        if source not in self._iid_to_index or target not in self._iid_to_index:
            return
        from_idx = self._iid_to_index[source]
        to_idx = self._iid_to_index[target]
        self.main_app.macro_editor.move_event(from_idx, to_idx)
        self.refresh()
        # Select the moved item
        new_iid = self._index_to_iid.get(to_idx)
        if new_iid and self.tree.exists(new_iid):
            self.tree.selection_set(new_iid)

    # ── Context Menu ──────────────────────────────────────────────────

    def _show_context_menu(self, event):
        """Show right-click context menu."""
        # Select row under cursor if not already selected
        item = self.tree.identify_row(event.y)
        if item and item not in self.tree.selection():
            self.tree.selection_set(item)

        # Enable/disable "Simplify Path" based on whether a group is selected
        has_group = any(
            iid in self._group_items for iid in self.tree.selection()
        )
        try:
            if has_group:
                self._context_menu.entryconfigure(
                    self._simplify_menu_index, state="normal"
                )
            else:
                self._context_menu.entryconfigure(
                    self._simplify_menu_index, state="disabled"
                )
        except Exception:
            pass

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
