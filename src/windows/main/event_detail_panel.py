from tkinter import BOTH, LEFT, RIGHT, W, X, BooleanVar, StringVar
from tkinter.ttk import Button, Checkbutton, Entry, Frame, Label, LabelFrame


class EventDetailPanel(Frame):
    """Bottom panel for viewing/editing fields of the selected event."""

    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self._current_index = None

        text = main_app.text_content.get("editor", {})

        self.label_frame = LabelFrame(
            self, text=text.get("detail_panel_title", "Event Details")
        )
        self.label_frame.pack(fill=BOTH, expand=True, padx=4, pady=4)

        # Row 0: Type (read-only)
        self._type_var = StringVar()
        Label(self.label_frame, text="Type:").grid(row=0, column=0, sticky=W, padx=4, pady=2)
        self._type_label = Label(self.label_frame, textvariable=self._type_var)
        self._type_label.grid(row=0, column=1, columnspan=3, sticky=W, padx=4, pady=2)

        # Row 1: X, Y
        self._x_label = Label(self.label_frame, text="X:")
        self._x_var = StringVar()
        self._x_entry = Entry(self.label_frame, textvariable=self._x_var, width=8)

        self._y_label = Label(self.label_frame, text="Y:")
        self._y_var = StringVar()
        self._y_entry = Entry(self.label_frame, textvariable=self._y_var, width=8)

        # Row 1: dx, dy (for scroll events)
        self._dx_label = Label(self.label_frame, text="dx:")
        self._dx_var = StringVar()
        self._dx_entry = Entry(self.label_frame, textvariable=self._dx_var, width=8)

        self._dy_label = Label(self.label_frame, text="dy:")
        self._dy_var = StringVar()
        self._dy_entry = Entry(self.label_frame, textvariable=self._dy_var, width=8)

        # Row 1: key (for keyboard events)
        self._key_label = Label(self.label_frame, text="Key:")
        self._key_var = StringVar()
        self._key_entry = Entry(self.label_frame, textvariable=self._key_var, width=16)

        # Row 2: pressed checkbox
        self._pressed_var = BooleanVar()
        self._pressed_check = Checkbutton(
            self.label_frame, text="Pressed", variable=self._pressed_var
        )

        # Row 2: delay
        self._delay_label = Label(self.label_frame, text="Delay (s):")
        self._delay_var = StringVar()
        self._delay_entry = Entry(self.label_frame, textvariable=self._delay_var, width=10)

        # Apply button
        self._apply_btn = Button(
            self.label_frame,
            text=text.get("apply_changes", "Apply Changes"),
            command=self._apply_changes,
        )

        # Track which widgets are currently shown
        self._shown_widgets = []

    def show_event(self, index, event_data):
        """Populate panel for the given event."""
        self._clear_fields()
        self._current_index = index
        event_type = event_data.get("type", "")
        self._type_var.set(event_type)

        row = 1
        col = 0

        if event_type in ("cursorMove", "leftClickEvent", "rightClickEvent", "middleClickEvent"):
            self._x_label.grid(row=row, column=0, sticky=W, padx=4, pady=2)
            self._x_entry.grid(row=row, column=1, sticky=W, padx=4, pady=2)
            self._x_var.set(str(event_data.get("x", "")))

            self._y_label.grid(row=row, column=2, sticky=W, padx=4, pady=2)
            self._y_entry.grid(row=row, column=3, sticky=W, padx=4, pady=2)
            self._y_var.set(str(event_data.get("y", "")))
            self._shown_widgets.extend([self._x_label, self._x_entry, self._y_label, self._y_entry])
            row += 1

        if event_type in ("leftClickEvent", "rightClickEvent", "middleClickEvent"):
            self._pressed_check.grid(row=row, column=0, columnspan=2, sticky=W, padx=4, pady=2)
            self._pressed_var.set(event_data.get("pressed", False))
            self._shown_widgets.append(self._pressed_check)
            row += 1

        if event_type == "scrollEvent":
            self._dx_label.grid(row=row, column=0, sticky=W, padx=4, pady=2)
            self._dx_entry.grid(row=row, column=1, sticky=W, padx=4, pady=2)
            self._dx_var.set(str(event_data.get("dx", "")))

            self._dy_label.grid(row=row, column=2, sticky=W, padx=4, pady=2)
            self._dy_entry.grid(row=row, column=3, sticky=W, padx=4, pady=2)
            self._dy_var.set(str(event_data.get("dy", "")))
            self._shown_widgets.extend([self._dx_label, self._dx_entry, self._dy_label, self._dy_entry])
            row += 1

        if event_type == "keyboardEvent":
            self._key_label.grid(row=row, column=0, sticky=W, padx=4, pady=2)
            self._key_entry.grid(row=row, column=1, columnspan=3, sticky=W, padx=4, pady=2)
            self._key_var.set(str(event_data.get("key", "")))
            self._shown_widgets.extend([self._key_label, self._key_entry])
            row += 1

            self._pressed_check.grid(row=row, column=0, columnspan=2, sticky=W, padx=4, pady=2)
            self._pressed_var.set(event_data.get("pressed", False))
            self._shown_widgets.append(self._pressed_check)
            row += 1

        # Delay is always shown
        self._delay_label.grid(row=row, column=0, sticky=W, padx=4, pady=2)
        self._delay_entry.grid(row=row, column=1, sticky=W, padx=4, pady=2)
        self._delay_var.set(f"{event_data.get('timestamp', 0):.4f}")
        self._shown_widgets.extend([self._delay_label, self._delay_entry])
        row += 1

        self._apply_btn.grid(row=row, column=0, columnspan=4, pady=(6, 4))
        self._shown_widgets.append(self._apply_btn)

    def _clear_fields(self):
        for w in self._shown_widgets:
            w.grid_forget()
        self._shown_widgets.clear()
        self._current_index = None

    def clear(self):
        self._clear_fields()
        self._type_var.set("")

    def _apply_changes(self):
        if self._current_index is None:
            return
        macro_editor = self.main_app.macro_editor
        event = macro_editor.get_event(self._current_index)
        if event is None:
            return

        event_type = event["type"]
        fields = {}

        try:
            fields["timestamp"] = float(self._delay_var.get())
        except ValueError:
            pass

        if event_type in ("cursorMove", "leftClickEvent", "rightClickEvent", "middleClickEvent"):
            try:
                fields["x"] = int(float(self._x_var.get()))
                fields["y"] = int(float(self._y_var.get()))
            except ValueError:
                pass

        if event_type in ("leftClickEvent", "rightClickEvent", "middleClickEvent", "keyboardEvent"):
            fields["pressed"] = self._pressed_var.get()

        if event_type == "scrollEvent":
            try:
                fields["dx"] = int(float(self._dx_var.get()))
                fields["dy"] = int(float(self._dy_var.get()))
            except ValueError:
                pass

        if event_type == "keyboardEvent":
            fields["key"] = self._key_var.get()

        if fields:
            macro_editor.update_event_fields(self._current_index, fields)
            # Refresh the editor row
            editor = getattr(self.main_app, "event_editor", None)
            if editor:
                editor.refresh_row(self._current_index)
