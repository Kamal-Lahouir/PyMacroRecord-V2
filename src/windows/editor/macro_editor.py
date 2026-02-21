from tkinter import BOTH, END, VERTICAL, HORIZONTAL, RIGHT, BOTTOM, Y, X
from tkinter.ttk import Frame, Treeview, Scrollbar


def build_groups(events):
    """Group consecutive cursorMove events into single entries."""
    groups = []
    i = 0
    while i < len(events):
        if events[i]["type"] == "cursorMove":
            j = i
            while j < len(events) and events[j]["type"] == "cursorMove":
                j += 1
            groups.append({"kind": "move_group", "start": i, "end": j - 1})
            i = j
        else:
            groups.append({"kind": "single", "index": i})
            i += 1
    return groups


def reorder_by_groups(events, groups, new_order):
    """Rebuild events list in the order given by new_order (list of group indices)."""
    new_events = []
    for gi in new_order:
        g = groups[gi]
        if g["kind"] == "move_group":
            new_events.extend(events[g["start"]:g["end"] + 1])
        else:
            new_events.append(events[g["index"]])
    return new_events


def _is_group_disabled(events, group):
    if group["kind"] == "move_group":
        return events[group["start"]].get("disabled", False)
    return events[group["index"]].get("disabled", False)


def _set_group_disabled(events, group, value):
    if group["kind"] == "move_group":
        for i in range(group["start"], group["end"] + 1):
            events[i]["disabled"] = value
    else:
        events[group["index"]]["disabled"] = value


class MacroEditor(Frame):
    def __init__(self, parent, text_content, main_app=None):
        super().__init__(parent)
        self.text_content = text_content
        self.main_app = main_app if main_app is not None else parent
        self._groups = []
        self._drag_item = None

        t = text_content.get("editor", {})

        columns = ("id", "action", "value", "comment")
        self.tree = Treeview(self, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text=t.get("col_id", "ID"))
        self.tree.heading("action", text=t.get("col_action", "Action"))
        self.tree.heading("value", text=t.get("col_value", "Value"))
        self.tree.heading("comment", text=t.get("col_comment", "Comment"))

        self.tree.column("id", width=50, minwidth=40, stretch=False)
        self.tree.column("action", width=160, minwidth=100)
        self.tree.column("value", width=300, minwidth=150)
        self.tree.column("comment", width=180, minwidth=80)

        self.tree.tag_configure("disabled", foreground="#999999")
        self.tree.tag_configure("playing", background="#c8e6c9")
        self._event_to_group = {}
        self._playing_iid = None

        vsb = Scrollbar(self, orient=VERTICAL, command=self.tree.yview)
        hsb = Scrollbar(self, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=RIGHT, fill=Y)
        hsb.pack(side=BOTTOM, fill=X)
        self.tree.pack(expand=True, fill=BOTH)

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.tree.bind("<B1-Motion>", self._on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self._on_drag_release)

    # ------------------------------------------------------------------ refresh

    def refresh(self, macro_events):
        self.tree.delete(*self.tree.get_children())
        self._groups = []

        events = macro_events.get("events", []) if macro_events else []
        self._groups = build_groups(events)
        self._playing_iid = None

        # Build reverse map: event_index → group_index
        self._event_to_group = {}
        for gi, group in enumerate(self._groups):
            if group["kind"] == "move_group":
                for i in range(group["start"], group["end"] + 1):
                    self._event_to_group[i] = gi
            else:
                self._event_to_group[group["index"]] = gi

        t = self.text_content.get("editor", {})

        action_map = {
            "cursorMove":      t.get("action_cursor_move",  "Mouse Move"),
            "leftClickEvent":  t.get("action_left_click",   "Left Click"),
            "rightClickEvent": t.get("action_right_click",  "Right Click"),
            "middleClickEvent":t.get("action_middle_click", "Middle Click"),
            "scrollEvent":     t.get("action_scroll",       "Scroll"),
            "keyboardEvent":   t.get("action_key_press",    "Key Press"),
            "delayEvent":      t.get("action_delay",        "Delay"),
        }
        steps_label   = t.get("steps",        "steps")
        disabled_tag  = t.get("disabled_tag", "[off]")
        key_press_lbl = t.get("action_key_press",   "Key Press")
        key_rel_lbl   = t.get("action_key_release", "Key Release")

        for gi, group in enumerate(self._groups):
            row_id = gi + 1
            is_disabled = _is_group_disabled(events, group)

            if group["kind"] == "move_group":
                e_start = events[group["start"]]
                e_end   = events[group["end"]]
                n       = group["end"] - group["start"] + 1
                action  = action_map["cursorMove"]
                value   = (f"({e_start['x']},{e_start['y']}) \u2192 "
                           f"({e_end['x']},{e_end['y']})  [{n} {steps_label}]")
                comment = e_start.get("comment", "")
            else:
                idx  = group["index"]
                ev   = events[idx]
                etype = ev["type"]
                comment = ev.get("comment", "")

                if etype in ("leftClickEvent", "rightClickEvent", "middleClickEvent"):
                    arrow  = "\u2193" if ev.get("pressed") else "\u2191"
                    action = f"{action_map.get(etype, etype)} {arrow}"
                    value  = f"({ev['x']},{ev['y']})"
                elif etype == "scrollEvent":
                    action = action_map.get(etype, etype)
                    value  = f"dx={ev['dx']}, dy={ev['dy']}"
                elif etype == "keyboardEvent":
                    action = key_press_lbl if ev.get("pressed") else key_rel_lbl
                    value  = str(ev.get("key", ""))
                elif etype == "delayEvent":
                    action = action_map["delayEvent"]
                    value  = f"{ev.get('timestamp', 0):.3f} s"
                else:
                    action = etype
                    value  = ""

            if is_disabled:
                action = f"{action}  {disabled_tag}"

            tags = ("disabled",) if is_disabled else ()
            self.tree.insert("", END, iid=str(gi),
                             values=(row_id, action, value, comment), tags=tags)

        # status bar
        n_actions    = len(self._groups)
        status_label = t.get("status_actions", "actions")
        try:
            self.main_app.status_text.configure(text=f"{n_actions} {status_label}")
        except Exception:
            pass

    # ------------------------------------------------------------------ queries

    def get_selected_group_index(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    # ------------------------------------------------------------------ playback highlight

    def highlight_event(self, event_index):
        """Called from playback thread via main_app.after() — highlights the active row."""
        gi = self._event_to_group.get(event_index)
        if gi is None:
            return
        iid = str(gi)
        if iid == self._playing_iid:
            return  # already highlighted
        # Remove highlight from previous row
        if self._playing_iid is not None:
            try:
                prev_tags = list(self.tree.item(self._playing_iid, "tags"))
                if "playing" in prev_tags:
                    prev_tags.remove("playing")
                    self.tree.item(self._playing_iid, tags=prev_tags)
            except Exception:
                pass
        # Apply highlight to new row
        current_tags = list(self.tree.item(iid, "tags"))
        if "playing" not in current_tags:
            current_tags.append("playing")
        self.tree.item(iid, tags=current_tags)
        self._playing_iid = iid
        self.tree.see(iid)
        self.tree.selection_set(iid)

    def clear_highlight(self):
        """Remove the playing highlight (called when playback finishes naturally)."""
        if self._playing_iid is not None:
            try:
                prev_tags = list(self.tree.item(self._playing_iid, "tags"))
                if "playing" in prev_tags:
                    prev_tags.remove("playing")
                    self.tree.item(self._playing_iid, tags=prev_tags)
            except Exception:
                pass
            self._playing_iid = None

    # ------------------------------------------------------------------ reorder

    def move_up(self, gi=None):
        if gi is None:
            gi = self.get_selected_group_index()
        if gi is None or gi == 0:
            return
        self._reorder(gi, gi - 1)
        # re-select moved row
        self.tree.selection_set(str(gi - 1))
        self.tree.see(str(gi - 1))

    def move_down(self, gi=None):
        if gi is None:
            gi = self.get_selected_group_index()
        if gi is None or gi >= len(self._groups) - 1:
            return
        self._reorder(gi, gi + 1)
        self.tree.selection_set(str(gi + 1))
        self.tree.see(str(gi + 1))

    def _reorder(self, from_gi, to_gi):
        events = self.main_app.macro.macro_events.get("events", [])
        new_order = list(range(len(self._groups)))
        new_order.pop(from_gi)
        new_order.insert(to_gi, from_gi)
        new_events = reorder_by_groups(events, self._groups, new_order)
        events.clear()
        events.extend(new_events)
        self.refresh(self.main_app.macro.macro_events)

    # ------------------------------------------------------------------ enable/disable

    def toggle_enabled(self, gi=None):
        if gi is None:
            gi = self.get_selected_group_index()
        if gi is None:
            return
        events = self.main_app.macro.macro_events.get("events", [])
        group  = self._groups[gi]
        current = _is_group_disabled(events, group)
        _set_group_disabled(events, group, not current)
        self.refresh(self.main_app.macro.macro_events)
        self.tree.selection_set(str(gi))

    # ------------------------------------------------------------------ drag-and-drop

    def _on_drag_start(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self._drag_item = item

    def _on_drag_motion(self, event):
        if not self._drag_item:
            return
        target = self.tree.identify_row(event.y)
        if target and target != self._drag_item:
            target_index = self.tree.index(target)
            self.tree.move(self._drag_item, "", target_index)

    def _on_drag_release(self, event):
        if not self._drag_item:
            return
        from_gi  = int(self._drag_item)
        children = self.tree.get_children()
        to_gi    = list(children).index(self._drag_item)
        self._drag_item = None
        if from_gi != to_gi:
            # children already in new visual order — rebuild events accordingly
            events    = self.main_app.macro.macro_events.get("events", [])
            new_order = [int(iid) for iid in children]
            new_events = reorder_by_groups(events, self._groups, new_order)
            events.clear()
            events.extend(new_events)
        self.refresh(self.main_app.macro.macro_events)
        if 0 <= to_gi < len(self._groups):
            self.tree.selection_set(str(to_gi))

    # ------------------------------------------------------------------ edit popup

    def _on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        gi = int(item)
        if gi >= len(self._groups):
            return
        from windows.editor.edit_event_popup import EditEventPopup
        EditEventPopup(self.main_app, self, gi)
