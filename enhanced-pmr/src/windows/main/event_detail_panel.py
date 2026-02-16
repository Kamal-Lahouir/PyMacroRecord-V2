from tkinter import BOTH, END, LEFT, RIGHT, W, X, Y, BooleanVar, StringVar, Text
from tkinter.ttk import Button, Checkbutton, Entry, Frame, Label, LabelFrame, Scrollbar


class EventDetailPanel(Frame):
    """Bottom panel for viewing/editing fields of the selected event."""

    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self._current_index = None
        self._current_group = None

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

        # Enabled checkbox (for all events)
        self._enabled_var = BooleanVar(value=True)
        self._enabled_check = Checkbutton(
            self.label_frame, text="Enabled", variable=self._enabled_var
        )

        # Label field (for all events)
        self._label_label = Label(self.label_frame, text="Label:")
        self._label_var = StringVar()
        self._label_entry = Entry(self.label_frame, textvariable=self._label_var, width=20)

        # Comment field (multi-line text widget)
        self._comment_label = Label(self.label_frame, text="Comment:")
        self._comment_frame = Frame(self.label_frame)
        self._comment_text = Text(self._comment_frame, width=40, height=3, wrap="word")
        self._comment_scrollbar = Scrollbar(self._comment_frame, command=self._comment_text.yview)
        self._comment_text.configure(yscrollcommand=self._comment_scrollbar.set)

        # Control flow fields
        self._target_label_label = Label(self.label_frame, text="Target Label:")
        self._target_label_var = StringVar()
        self._target_label_entry = Entry(self.label_frame, textvariable=self._target_label_var, width=20)

        self._timeout_label_label = Label(self.label_frame, text="Timeout Label:")
        self._timeout_label_var = StringVar()
        self._timeout_label_entry = Entry(self.label_frame, textvariable=self._timeout_label_var, width=20)

        self._repeat_count_label = Label(self.label_frame, text="Repeat Count:")
        self._repeat_count_var = StringVar()
        self._repeat_count_entry = Entry(self.label_frame, textvariable=self._repeat_count_var, width=10)

        self._wait_delay_label = Label(self.label_frame, text="Wait Duration (s):")
        self._wait_delay_var = StringVar()
        self._wait_delay_entry = Entry(self.label_frame, textvariable=self._wait_delay_var, width=10)

        # Row 2: delay
        self._delay_label = Label(self.label_frame, text="Delay (s):")
        self._delay_var = StringVar()
        self._delay_entry = Entry(self.label_frame, textvariable=self._delay_var, width=10)

        # Apply button
        self._apply_btn = Button(
            self.label_frame,
            text=text.get("apply_changes", "Apply Changes"),
            command=self._apply_changes,
            style="Primary.TButton",
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

        # Control flow events
        if event_type == "goto":
            self._target_label_label.grid(row=row, column=0, sticky=W, padx=4, pady=2)
            self._target_label_entry.grid(row=row, column=1, columnspan=3, sticky=W, padx=4, pady=2)
            self._target_label_var.set(event_data.get("target_label", ""))
            self._shown_widgets.extend([self._target_label_label, self._target_label_entry])
            row += 1

            self._timeout_label_label.grid(row=row, column=0, sticky=W, padx=4, pady=2)
            self._timeout_label_entry.grid(row=row, column=1, columnspan=3, sticky=W, padx=4, pady=2)
            self._timeout_label_var.set(event_data.get("timeout_label", ""))
            self._shown_widgets.extend([self._timeout_label_label, self._timeout_label_entry])
            row += 1

        elif event_type == "repeat":
            self._target_label_label.grid(row=row, column=0, sticky=W, padx=4, pady=2)
            self._target_label_entry.grid(row=row, column=1, columnspan=3, sticky=W, padx=4, pady=2)
            self._target_label_var.set(event_data.get("target_label", ""))
            self._shown_widgets.extend([self._target_label_label, self._target_label_entry])
            row += 1

            self._repeat_count_label.grid(row=row, column=0, sticky=W, padx=4, pady=2)
            self._repeat_count_entry.grid(row=row, column=1, sticky=W, padx=4, pady=2)
            self._repeat_count_var.set(str(event_data.get("count", 1)))
            self._shown_widgets.extend([self._repeat_count_label, self._repeat_count_entry])
            row += 1

        elif event_type == "wait":
            self._wait_delay_label.grid(row=row, column=0, sticky=W, padx=4, pady=2)
            self._wait_delay_entry.grid(row=row, column=1, sticky=W, padx=4, pady=2)
            self._wait_delay_var.set(f"{event_data.get('delay', 0):.4f}")
            self._shown_widgets.extend([self._wait_delay_label, self._wait_delay_entry])
            row += 1

        # Label is always shown
        self._label_label.grid(row=row, column=0, sticky=W, padx=4, pady=2)
        self._label_entry.grid(row=row, column=1, columnspan=3, sticky=W, padx=4, pady=2)
        self._label_var.set(event_data.get("label", ""))
        self._shown_widgets.extend([self._label_label, self._label_entry])
        row += 1

        # Comment is always shown (multi-line)
        self._comment_label.grid(row=row, column=0, sticky=W+"n", padx=4, pady=2)
        self._comment_frame.grid(row=row, column=1, columnspan=3, sticky=W, padx=4, pady=2)
        self._comment_text.pack(side=LEFT, fill=BOTH, expand=True)
        self._comment_scrollbar.pack(side=RIGHT, fill=Y)
        # Clear and set comment
        self._comment_text.delete("1.0", END)
        self._comment_text.insert("1.0", event_data.get("comment", ""))
        self._shown_widgets.extend([self._comment_label, self._comment_frame])
        row += 1

        # Delay is always shown
        self._delay_label.grid(row=row, column=0, sticky=W, padx=4, pady=2)
        self._delay_entry.grid(row=row, column=1, sticky=W, padx=4, pady=2)
        self._delay_var.set(f"{event_data.get('timestamp', 0):.4f}")
        self._shown_widgets.extend([self._delay_label, self._delay_entry])
        row += 1

        # Enabled checkbox is always shown
        self._enabled_check.grid(row=row, column=0, columnspan=2, sticky=W, padx=4, pady=2)
        self._enabled_var.set(event_data.get("enabled", True))
        self._shown_widgets.append(self._enabled_check)
        row += 1

        self._apply_btn.grid(row=row, column=0, columnspan=4, pady=(6, 4))
        self._shown_widgets.append(self._apply_btn)

    def show_group(self, group_info, stats):
        """Show summary for a mouse path group with editable total delay."""
        self._clear_fields()
        self._current_group = group_info

        text = self.main_app.text_content.get("editor", {})
        self._type_var.set(text.get("mouse_path", "Mouse Path"))

        row = 1
        # Start coordinates
        start_lbl = Label(self.label_frame, text=text.get("group_start", "Start") + ":")
        start_lbl.grid(row=row, column=0, sticky=W, padx=4, pady=2)
        start_val = Label(
            self.label_frame,
            text=f"({stats['start_x']}, {stats['start_y']})",
        )
        start_val.grid(row=row, column=1, columnspan=3, sticky=W, padx=4, pady=2)
        self._shown_widgets.extend([start_lbl, start_val])
        row += 1

        # End coordinates
        end_lbl = Label(self.label_frame, text=text.get("group_end", "End") + ":")
        end_lbl.grid(row=row, column=0, sticky=W, padx=4, pady=2)
        end_val = Label(
            self.label_frame,
            text=f"({stats['end_x']}, {stats['end_y']})",
        )
        end_val.grid(row=row, column=1, columnspan=3, sticky=W, padx=4, pady=2)
        self._shown_widgets.extend([end_lbl, end_val])
        row += 1

        # Moves and distance
        moves_lbl = Label(self.label_frame, text=text.get("group_moves", "Moves") + ":")
        moves_lbl.grid(row=row, column=0, sticky=W, padx=4, pady=2)
        moves_val = Label(self.label_frame, text=str(stats["total_moves"]))
        moves_val.grid(row=row, column=1, sticky=W, padx=4, pady=2)

        dist_lbl = Label(self.label_frame, text=text.get("group_distance", "Distance") + ":")
        dist_lbl.grid(row=row, column=2, sticky=W, padx=4, pady=2)
        dist_val = Label(self.label_frame, text=f"{stats['total_distance']:.0f}px")
        dist_val.grid(row=row, column=3, sticky=W, padx=4, pady=2)
        self._shown_widgets.extend([moves_lbl, moves_val, dist_lbl, dist_val])
        row += 1

        # Duration — editable
        dur_lbl = Label(self.label_frame, text=text.get("group_duration", "Duration") + " (s):")
        dur_lbl.grid(row=row, column=0, sticky=W, padx=4, pady=2)
        self._delay_var.set(f"{stats['total_time']:.4f}")
        self._delay_entry.grid(row=row, column=1, sticky=W, padx=4, pady=2)
        self._shown_widgets.extend([dur_lbl, self._delay_entry])
        row += 1

        # Apply button
        self._apply_btn.grid(row=row, column=0, columnspan=4, pady=(6, 4))
        self._shown_widgets.append(self._apply_btn)

    def _clear_fields(self):
        for w in self._shown_widgets:
            w.grid_forget()
        self._shown_widgets.clear()
        self._current_index = None
        self._current_group = None

    def clear(self):
        self._clear_fields()
        self._type_var.set("")
        self._comment_text.delete("1.0", END)

    def _apply_changes(self):
        macro_editor = self.main_app.macro_editor
        editor = getattr(self.main_app, "event_editor", None)

        # ── Group delay rescale ──────────────────────────────────────
        if self._current_group is not None:
            try:
                new_total = float(self._delay_var.get())
            except ValueError:
                return
            macro_editor.rescale_group_time(
                self._current_group["start"],
                self._current_group["end"],
                new_total,
            )
            if editor:
                editor.refresh()
            return

        # ── Single event edit ────────────────────────────────────────
        if self._current_index is None:
            return
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

        # Handle control flow events
        if event_type == "goto":
            fields["target_label"] = self._target_label_var.get().strip()
            timeout = self._timeout_label_var.get().strip()
            if timeout:
                fields["timeout_label"] = timeout
            elif "timeout_label" in event:
                fields["timeout_label"] = None  # Remove if cleared

        elif event_type == "repeat":
            fields["target_label"] = self._target_label_var.get().strip()
            try:
                fields["count"] = max(1, int(self._repeat_count_var.get()))
            except ValueError:
                pass

        elif event_type == "wait":
            try:
                fields["delay"] = max(0, float(self._wait_delay_var.get()))
            except ValueError:
                pass

        # Handle label separately with validation
        label_value = self._label_var.get()
        success, error = macro_editor.update_event_label(self._current_index, label_value)
        if not success and error:
            from tkinter import messagebox
            messagebox.showerror("Invalid Label", error)
            return  # Don't apply other changes if label is invalid

        # Handle comment
        comment_value = self._comment_text.get("1.0", END).strip()
        macro_editor.update_event_comment(self._current_index, comment_value)

        # Handle enabled state
        fields["enabled"] = self._enabled_var.get()

        if fields:
            macro_editor.update_event_fields(self._current_index, fields)
            if editor:
                editor.refresh_row(self._current_index)
