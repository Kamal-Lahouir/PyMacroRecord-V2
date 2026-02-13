from tkinter import BOTH, LEFT, W, X, BooleanVar, StringVar
from tkinter.ttk import Button, Checkbutton, Combobox, Entry, Frame, Label, LabelFrame

from windows.popup import Popup


EVENT_TYPES = [
    ("cursorMove", "Cursor Move"),
    ("leftClickEvent", "Left Click"),
    ("rightClickEvent", "Right Click"),
    ("middleClickEvent", "Middle Click"),
    ("scrollEvent", "Scroll"),
    ("keyboardEvent", "Keyboard"),
]


class InsertEventDialog(Popup):
    """Dialog for inserting a new event at a given position."""

    def __init__(self, main_app, insert_index):
        text = main_app.text_content.get("editor", {})
        super().__init__(
            text.get("insert_dialog_title", "Insert New Event"),
            400, 320, main_app,
        )
        self.main_app = main_app
        self.insert_index = insert_index

        # Event type selector
        type_frame = LabelFrame(self, text=text.get("event_type", "Event Type"))
        type_frame.pack(fill=X, padx=10, pady=(10, 4))

        self._type_var = StringVar(value=EVENT_TYPES[0][0])
        self._type_combo = Combobox(
            type_frame,
            textvariable=self._type_var,
            values=[t[1] for t in EVENT_TYPES],
            state="readonly",
            width=25,
        )
        self._type_combo.set(EVENT_TYPES[0][1])
        self._type_combo.pack(padx=8, pady=6)
        self._type_combo.bind("<<ComboboxSelected>>", self._on_type_change)

        # Fields frame
        self._fields_frame = LabelFrame(self, text="Parameters")
        self._fields_frame.pack(fill=BOTH, expand=True, padx=10, pady=4)

        # Create all possible field widgets
        self._x_var = StringVar(value="0")
        self._y_var = StringVar(value="0")
        self._dx_var = StringVar(value="0")
        self._dy_var = StringVar(value="0")
        self._key_var = StringVar(value="a")
        self._pressed_var = BooleanVar(value=True)
        self._delay_var = StringVar(value="0.1")

        self._field_widgets = []

        # Buttons
        btn_frame = Frame(self)
        btn_frame.pack(fill=X, padx=10, pady=(4, 10))

        confirm_text = main_app.text_content.get("global", {}).get("confirm_button", "Confirm")
        cancel_text = main_app.text_content.get("global", {}).get("cancel_button", "Cancel")

        Button(btn_frame, text=confirm_text, command=self._confirm,
               style="Primary.TButton").pack(side=LEFT, padx=4)
        Button(btn_frame, text=cancel_text, command=self.destroy).pack(side=LEFT, padx=4)

        # Show initial fields
        self._show_fields_for_type("cursorMove")
        self.wait_window()

    def _get_selected_type_key(self):
        label = self._type_combo.get()
        for key, lbl in EVENT_TYPES:
            if lbl == label:
                return key
        return EVENT_TYPES[0][0]

    def _on_type_change(self, event=None):
        type_key = self._get_selected_type_key()
        self._show_fields_for_type(type_key)

    def _show_fields_for_type(self, event_type):
        for w in self._field_widgets:
            w.grid_forget()
        self._field_widgets.clear()

        row = 0

        if event_type in ("cursorMove", "leftClickEvent", "rightClickEvent", "middleClickEvent"):
            lx = Label(self._fields_frame, text="X:")
            lx.grid(row=row, column=0, sticky=W, padx=4, pady=2)
            ex = Entry(self._fields_frame, textvariable=self._x_var, width=8)
            ex.grid(row=row, column=1, sticky=W, padx=4, pady=2)
            ly = Label(self._fields_frame, text="Y:")
            ly.grid(row=row, column=2, sticky=W, padx=4, pady=2)
            ey = Entry(self._fields_frame, textvariable=self._y_var, width=8)
            ey.grid(row=row, column=3, sticky=W, padx=4, pady=2)
            self._field_widgets.extend([lx, ex, ly, ey])
            row += 1

        if event_type in ("leftClickEvent", "rightClickEvent", "middleClickEvent"):
            cb = Checkbutton(self._fields_frame, text="Pressed", variable=self._pressed_var)
            cb.grid(row=row, column=0, columnspan=2, sticky=W, padx=4, pady=2)
            self._field_widgets.append(cb)
            row += 1

        if event_type == "scrollEvent":
            ldx = Label(self._fields_frame, text="dx:")
            ldx.grid(row=row, column=0, sticky=W, padx=4, pady=2)
            edx = Entry(self._fields_frame, textvariable=self._dx_var, width=8)
            edx.grid(row=row, column=1, sticky=W, padx=4, pady=2)
            ldy = Label(self._fields_frame, text="dy:")
            ldy.grid(row=row, column=2, sticky=W, padx=4, pady=2)
            edy = Entry(self._fields_frame, textvariable=self._dy_var, width=8)
            edy.grid(row=row, column=3, sticky=W, padx=4, pady=2)
            self._field_widgets.extend([ldx, edx, ldy, edy])
            row += 1

        if event_type == "keyboardEvent":
            lk = Label(self._fields_frame, text="Key:")
            lk.grid(row=row, column=0, sticky=W, padx=4, pady=2)
            ek = Entry(self._fields_frame, textvariable=self._key_var, width=16)
            ek.grid(row=row, column=1, columnspan=3, sticky=W, padx=4, pady=2)
            self._field_widgets.extend([lk, ek])
            row += 1

            cb = Checkbutton(self._fields_frame, text="Pressed", variable=self._pressed_var)
            cb.grid(row=row, column=0, columnspan=2, sticky=W, padx=4, pady=2)
            self._field_widgets.append(cb)
            row += 1

        # Delay is always shown
        ld = Label(self._fields_frame, text="Delay (s):")
        ld.grid(row=row, column=0, sticky=W, padx=4, pady=2)
        ed = Entry(self._fields_frame, textvariable=self._delay_var, width=10)
        ed.grid(row=row, column=1, sticky=W, padx=4, pady=2)
        self._field_widgets.extend([ld, ed])

    def _confirm(self):
        event_type = self._get_selected_type_key()
        event = {"type": event_type}

        try:
            event["timestamp"] = float(self._delay_var.get())
        except ValueError:
            event["timestamp"] = 0.0

        if event_type in ("cursorMove", "leftClickEvent", "rightClickEvent", "middleClickEvent"):
            try:
                event["x"] = int(float(self._x_var.get()))
                event["y"] = int(float(self._y_var.get()))
            except ValueError:
                event["x"] = 0
                event["y"] = 0

        if event_type in ("leftClickEvent", "rightClickEvent", "middleClickEvent"):
            event["pressed"] = self._pressed_var.get()

        if event_type == "scrollEvent":
            try:
                event["dx"] = int(float(self._dx_var.get()))
                event["dy"] = int(float(self._dy_var.get()))
            except ValueError:
                event["dx"] = 0
                event["dy"] = 0

        if event_type == "keyboardEvent":
            event["key"] = self._key_var.get()
            event["pressed"] = self._pressed_var.get()

        self.main_app.macro_editor.insert_event(self.insert_index, event)
        editor = getattr(self.main_app, "event_editor", None)
        if editor:
            editor.refresh()
        self.destroy()
