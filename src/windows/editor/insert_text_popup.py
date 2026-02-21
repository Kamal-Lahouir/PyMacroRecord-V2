from tkinter import StringVar, Label, Frame, Button, LEFT, X
from tkinter.ttk import Entry
from windows.popup import Popup


class InsertTextPopup(Popup):
    def __init__(self, main_app, macro_editor):
        t = main_app.text_content.get("editor", {})
        super().__init__(t.get("type_text_title", "Insert Text"), 320, 130, main_app)

        self.main_app = main_app
        self.macro_editor = macro_editor
        self.t = t

        Label(self, text=t.get("type_text_label", "Text to type:"),
              anchor="w").pack(fill=X, padx=10, pady=(10, 2))
        self._text_var = StringVar()
        Entry(self, textvariable=self._text_var).pack(fill=X, padx=10)

        Label(self, text=t.get("timestamp", "Delay (s):"),
              anchor="w").pack(fill=X, padx=10, pady=(6, 2))
        self._delay_var = StringVar(value="0.0")
        Entry(self, textvariable=self._delay_var).pack(fill=X, padx=10)

        btn = Frame(self)
        btn.pack(fill=X, padx=10, pady=8)
        g = main_app.text_content.get("global", {})
        Button(btn, text=g.get("confirm_button", "Confirm"), command=self._confirm).pack(side=LEFT, padx=4)
        Button(btn, text=g.get("cancel_button", "Cancel"), command=self.destroy).pack(side=LEFT, padx=4)

    def _confirm(self):
        text = self._text_var.get()
        if not text:
            self.destroy()
            return
        try:
            delay = float(self._delay_var.get())
        except ValueError:
            delay = 0.0
        events = self.main_app.macro.macro_events.get("events", [])
        gi = self.macro_editor.get_selected_group_index()
        new_event = {"type": "typeTextEvent", "text": text, "timestamp": delay}
        if gi is None:
            events.append(new_event)
        else:
            group = self.macro_editor._groups[gi]
            insert_at = group["end"] + 1 if group["kind"] == "move_group" else group["index"] + 1
            events.insert(insert_at, new_event)
        self.macro_editor.refresh(self.main_app.macro.macro_events)
        self.destroy()
