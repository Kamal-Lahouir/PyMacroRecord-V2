from tkinter import StringVar, Label, Frame, Button, LEFT, X, messagebox
from tkinter.ttk import Combobox, Entry
from windows.popup import Popup


_TYPE_KEYS = [
    ("all_types",           None),
    ("action_cursor_move",  "cursorMove"),
    ("action_left_click",   "leftClickEvent"),
    ("action_right_click",  "rightClickEvent"),
    ("action_middle_click", "middleClickEvent"),
    ("action_scroll",       "scrollEvent"),
    ("action_key_press",    "keyboardEvent"),
    ("action_delay",        "delayEvent"),
]


class SearchReplacePopup(Popup):
    def __init__(self, main_app, macro_editor):
        t = main_app.text_content.get("editor", {})
        super().__init__(t.get("find_replace_title", "Find & Replace"), 400, 320, main_app)

        self.main_app    = main_app
        self.macro_editor = macro_editor
        self.t           = t

        pad = {"fill": X, "padx": 10, "pady": 3}

        # ── Action type filter ──────────────────────────────────────────────
        self._add_label(t.get("fr_action_type", "Action type"))
        self._type_labels = [t.get(k, v or "All types") for k, v in _TYPE_KEYS]
        self._type_var = StringVar(value=self._type_labels[0])
        cb = Combobox(self, textvariable=self._type_var,
                      values=self._type_labels, state="readonly")
        cb.pack(**pad)

        # ── Value contains ──────────────────────────────────────────────────
        self._add_label(t.get("fr_value_contains", "Value contains"))
        self._find_value_var = StringVar()
        Entry(self, textvariable=self._find_value_var).pack(**pad)

        # ── Replace comment ─────────────────────────────────────────────────
        self._add_label(t.get("fr_replace_comment", "Set comment"))
        self._repl_comment_var = StringVar()
        Entry(self, textvariable=self._repl_comment_var).pack(**pad)

        # ── Replace delay ───────────────────────────────────────────────────
        self._add_label(t.get("fr_replace_delay", "Set delay (s)") +
                        "  (leave blank = no change)")
        self._repl_delay_var = StringVar()
        Entry(self, textvariable=self._repl_delay_var).pack(**pad)

        # ── Replace key (keyboard only) ─────────────────────────────────────
        self._add_label(t.get("fr_replace_key_from", "Replace key") +
                        " → " + t.get("fr_replace_key_to", "With key") +
                        "  (leave blank = no change)")
        key_row = Frame(self)
        key_row.pack(**pad)
        self._key_from_var = StringVar()
        self._key_to_var   = StringVar()
        Entry(key_row, textvariable=self._key_from_var, width=14).pack(side=LEFT, padx=(0, 4))
        Label(key_row, text="→").pack(side=LEFT)
        Entry(key_row, textvariable=self._key_to_var, width=14).pack(side=LEFT, padx=(4, 0))

        # ── Buttons ─────────────────────────────────────────────────────────
        btn_frame = Frame(self)
        btn_frame.pack(fill=X, padx=10, pady=(6, 10))
        Button(btn_frame, text=t.get("confirm_button",
               main_app.text_content.get("global", {}).get("confirm_button", "Replace All")),
               command=self._replace_all).pack(side=LEFT, padx=4)
        Button(btn_frame, text=main_app.text_content.get("global", {}).get("cancel_button", "Cancel"),
               command=self.destroy).pack(side=LEFT, padx=4)

    def _add_label(self, text):
        Label(self, text=text, anchor="w").pack(fill=X, padx=10)

    def _replace_all(self):
        t      = self.t
        events = self.main_app.macro.macro_events.get("events", [])
        groups = self.macro_editor._groups

        # Resolve selected type filter
        selected_label = self._type_var.get()
        type_filter = None
        for label, etype in zip(self._type_labels,
                                [v for _, v in _TYPE_KEYS]):
            if label == selected_label:
                type_filter = etype
                break

        find_val       = self._find_value_var.get().strip()
        repl_comment   = self._repl_comment_var.get()
        repl_delay_str = self._repl_delay_var.get().strip()
        key_from       = self._key_from_var.get().strip()
        key_to         = self._key_to_var.get().strip()

        repl_delay = None
        if repl_delay_str:
            try:
                repl_delay = float(repl_delay_str)
            except ValueError:
                messagebox.showerror(
                    t.get("find_replace_title", "Find & Replace"),
                    "Delay must be a number.")
                return

        replaced = 0

        for gi, group in enumerate(groups):
            # Collect events for this group
            if group["kind"] == "move_group":
                ev_indices = list(range(group["start"], group["end"] + 1))
            else:
                ev_indices = [group["index"]]

            # Check type filter — use representative event
            rep = events[ev_indices[0]]
            if type_filter is not None and rep["type"] != type_filter:
                continue

            # Check value contains filter (against display value of first event)
            if find_val:
                display = self._display_value(rep)
                if find_val.lower() not in display.lower():
                    continue

            # Apply replacements
            matched = False
            for idx in ev_indices:
                ev = events[idx]

                if repl_delay is not None:
                    ev["timestamp"] = repl_delay
                    matched = True

                if repl_comment:
                    ev["comment"] = repl_comment
                    matched = True

                if key_from and key_to and ev.get("type") == "keyboardEvent":
                    if ev.get("key") == key_from:
                        ev["key"] = key_to
                        matched = True

            if matched:
                replaced += 1

        self.macro_editor.refresh(self.main_app.macro.macro_events)
        repl_label    = t.get("fr_replaced", "Replaced")
        matches_label = t.get("fr_matches",  "matches")
        messagebox.showinfo(t.get("find_replace_title", "Find & Replace"),
                            f"{repl_label}: {replaced} {matches_label}")
        self.destroy()

    @staticmethod
    def _display_value(ev):
        etype = ev.get("type", "")
        if etype == "cursorMove":
            return f"({ev.get('x',0)},{ev.get('y',0)})"
        if etype in ("leftClickEvent", "rightClickEvent", "middleClickEvent"):
            return f"({ev.get('x',0)},{ev.get('y',0)})"
        if etype == "scrollEvent":
            return f"dx={ev.get('dx',0)}, dy={ev.get('dy',0)}"
        if etype == "keyboardEvent":
            return str(ev.get("key", ""))
        return ""
