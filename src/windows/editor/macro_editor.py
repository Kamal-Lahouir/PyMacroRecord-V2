from tkinter import BOTH, END, VERTICAL, HORIZONTAL, RIGHT, BOTTOM, Y, X
from tkinter.ttk import Frame, Treeview, Scrollbar


def _build_groups(events):
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


class MacroEditor(Frame):
    def __init__(self, parent, text_content):
        super().__init__(parent)
        self.text_content = text_content
        self.main_app = parent
        self._groups = []

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

        vsb = Scrollbar(self, orient=VERTICAL, command=self.tree.yview)
        hsb = Scrollbar(self, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=RIGHT, fill=Y)
        hsb.pack(side=BOTTOM, fill=X)
        self.tree.pack(expand=True, fill=BOTH)

        self.tree.bind("<Double-1>", self._on_double_click)

    def refresh(self, macro_events):
        self.tree.delete(*self.tree.get_children())
        self._groups = []

        events = macro_events.get("events", []) if macro_events else []
        self._groups = _build_groups(events)

        t = self.text_content.get("editor", {})

        action_map = {
            "cursorMove": t.get("action_cursor_move", "Mouse Move"),
            "leftClickEvent": t.get("action_left_click", "Left Click"),
            "rightClickEvent": t.get("action_right_click", "Right Click"),
            "middleClickEvent": t.get("action_middle_click", "Middle Click"),
            "scrollEvent": t.get("action_scroll", "Scroll"),
            "keyboardEvent": t.get("action_key_press", "Key Press"),
        }
        steps_label = t.get("steps", "steps")

        for gi, group in enumerate(self._groups):
            row_id = gi + 1
            if group["kind"] == "move_group":
                start_i = group["start"]
                end_i = group["end"]
                e_start = events[start_i]
                e_end = events[end_i]
                n = end_i - start_i + 1
                action = action_map["cursorMove"]
                value = f"({e_start['x']},{e_start['y']}) \u2192 ({e_end['x']},{e_end['y']})  [{n} {steps_label}]"
                comment = e_start.get("comment", "")
            else:
                idx = group["index"]
                ev = events[idx]
                etype = ev["type"]
                comment = ev.get("comment", "")
                if etype in ("leftClickEvent", "rightClickEvent", "middleClickEvent"):
                    pressed_str = "\u2193" if ev.get("pressed") else "\u2191"
                    action = f"{action_map.get(etype, etype)} {pressed_str}"
                    value = f"({ev['x']},{ev['y']})"
                elif etype == "scrollEvent":
                    action = action_map.get(etype, etype)
                    value = f"dx={ev['dx']}, dy={ev['dy']}"
                elif etype == "keyboardEvent":
                    pressed_str = t.get("action_key_press", "Key Press") if ev.get("pressed") else t.get("action_key_release", "Key Release")
                    action = pressed_str
                    value = str(ev.get("key", ""))
                else:
                    action = etype
                    value = ""

            self.tree.insert("", END, iid=str(gi), values=(row_id, action, value, comment))

        # Update status bar
        n_actions = len(self._groups)
        status_label = t.get("status_actions", "actions")
        try:
            self.main_app.status_text.configure(text=f"{n_actions} {status_label}")
        except Exception:
            pass

    def get_selected_group_index(self):
        sel = self.tree.selection()
        if sel:
            return int(sel[0])
        return None

    def _on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        gi = int(item)
        if gi >= len(self._groups):
            return
        from windows.editor.edit_event_popup import EditEventPopup
        EditEventPopup(self.main_app, self, gi)
