from tkinter import StringVar, Label, Frame, Button, LEFT, X
from tkinter.ttk import Entry
from windows.popup import Popup


class InsertLoopPopup(Popup):
    def __init__(self, main_app, macro_editor):
        t = main_app.text_content.get("editor", {})
        super().__init__(t.get("loop_title", "Wrap in Loop"), 280, 150, main_app)

        self.main_app = main_app
        self.macro_editor = macro_editor
        self.t = t

        Label(self, text=t.get("loop_count_label", "Repeat count:"),
              anchor="w").pack(fill=X, padx=10, pady=(10, 2))
        self._count_var = StringVar(value="2")
        Entry(self, textvariable=self._count_var).pack(fill=X, padx=10)

        Label(self, text=t.get("loop_rows_label", "Rows to include:"),
              anchor="w").pack(fill=X, padx=10, pady=(6, 2))
        self._rows_var = StringVar(value="1")
        Entry(self, textvariable=self._rows_var).pack(fill=X, padx=10)

        btn = Frame(self)
        btn.pack(fill=X, padx=10, pady=8)
        g = main_app.text_content.get("global", {})
        Button(btn, text=g.get("confirm_button", "Confirm"), command=self._confirm).pack(side=LEFT, padx=4)
        Button(btn, text=g.get("cancel_button", "Cancel"), command=self.destroy).pack(side=LEFT, padx=4)

    def _confirm(self):
        try:
            count = max(1, int(self._count_var.get()))
        except ValueError:
            count = 2
        try:
            rows = max(1, int(self._rows_var.get()))
        except ValueError:
            rows = 1

        events = self.main_app.macro.macro_events.get("events", [])
        gi = self.macro_editor.get_selected_group_index()
        groups = self.macro_editor._groups

        if gi is None:
            insert_before = len(events)
            insert_after = len(events)
        else:
            group = groups[gi]
            insert_before = group["start"] if group["kind"] == "move_group" else group["index"]
            # Find the end event index after `rows` groups
            end_gi = min(gi + rows - 1, len(groups) - 1)
            end_group = groups[end_gi]
            insert_after = (end_group["end"] if end_group["kind"] == "move_group" else end_group["index"]) + 1

        loop_end = {"type": "loopEnd", "timestamp": 0.0}
        loop_start = {"type": "loopStart", "count": count, "timestamp": 0.0}

        # Insert end first (higher index) so start index stays valid
        events.insert(insert_after, loop_end)
        events.insert(insert_before, loop_start)

        self.macro_editor.refresh(self.main_app.macro.macro_events)
        self.destroy()
