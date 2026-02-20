from tkinter import StringVar, Label, Frame, Button, LEFT, X
from tkinter.ttk import Entry
from windows.popup import Popup


class InsertDelayPopup(Popup):
    def __init__(self, main_app, macro_editor):
        t = main_app.text_content.get("editor", {})
        super().__init__(t.get("insert_delay_title", "Insert Delay"), 280, 120, main_app)

        self.main_app    = main_app
        self.macro_editor = macro_editor
        self.t           = t

        Label(self, text=t.get("insert_delay_label", "Delay (seconds):"),
              anchor="w").pack(fill=X, padx=10, pady=(10, 2))

        self._delay_var = StringVar(value="1.0")
        Entry(self, textvariable=self._delay_var).pack(fill=X, padx=10)

        btn_frame = Frame(self)
        btn_frame.pack(fill=X, padx=10, pady=8)
        confirm_text = main_app.text_content.get("global", {}).get("confirm_button", "Confirm")
        cancel_text  = main_app.text_content.get("global", {}).get("cancel_button", "Cancel")
        Button(btn_frame, text=confirm_text, command=self._confirm).pack(side=LEFT, padx=4)
        Button(btn_frame, text=cancel_text,  command=self.destroy).pack(side=LEFT, padx=4)

    def _confirm(self):
        try:
            delay = float(self._delay_var.get())
        except ValueError:
            delay = 1.0

        events = self.main_app.macro.macro_events.get("events", [])
        gi     = self.macro_editor.get_selected_group_index()

        new_event = {"type": "delayEvent", "timestamp": delay}

        if gi is None:
            # Append at end
            events.append(new_event)
        else:
            group = self.macro_editor._groups[gi]
            if group["kind"] == "move_group":
                insert_at = group["end"] + 1
            else:
                insert_at = group["index"] + 1
            events.insert(insert_at, new_event)

        self.macro_editor.refresh(self.main_app.macro.macro_events)
        self.destroy()
