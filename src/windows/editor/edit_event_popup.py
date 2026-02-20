from tkinter import StringVar, Label, Entry, Frame, Button, TOP, LEFT, X, EW
from windows.popup import Popup


class EditEventPopup(Popup):
    def __init__(self, main_app, macro_editor, group_index):
        t = main_app.text_content.get("editor", {})
        super().__init__(t.get("edit_title", "Edit Action"), 380, 280, main_app)

        self.main_app = main_app
        self.macro_editor = macro_editor
        self.group_index = group_index
        self.t = t

        group = macro_editor._groups[group_index]
        events = main_app.macro.macro_events.get("events", [])

        self._fields = {}
        content_frame = Frame(self)
        content_frame.pack(side=TOP, fill=X, padx=10, pady=10)

        if group["kind"] == "move_group":
            self._build_move_group(content_frame, group, events)
        elif group["kind"] == "single":
            ev = events[group["index"]]
            etype = ev["type"]
            if etype in ("leftClickEvent", "rightClickEvent", "middleClickEvent"):
                self._build_click(content_frame, ev)
            elif etype == "keyboardEvent":
                self._build_keyboard(content_frame, ev)
            elif etype == "scrollEvent":
                self._build_scroll(content_frame, ev)
            else:
                self._build_generic(content_frame, ev)

        # Comment field always shown
        self._add_field(content_frame, t.get("comment", "Comment"), "comment",
                        events[group["start"] if group["kind"] == "move_group" else group["index"]].get("comment", ""))

        btn_frame = Frame(self)
        btn_frame.pack(side=TOP, fill=X, padx=10, pady=(0, 10))
        Button(btn_frame, text=t.get("confirm_button", main_app.text_content.get("global", {}).get("confirm_button", "Confirm")),
               command=self._confirm).pack(side=LEFT, padx=5)
        Button(btn_frame, text=main_app.text_content.get("global", {}).get("cancel_button", "Cancel"),
               command=self.destroy).pack(side=LEFT, padx=5)

    def _add_field(self, parent, label_text, key, initial=""):
        row = Frame(parent)
        row.pack(fill=X, pady=2)
        Label(row, text=label_text + ":", width=12, anchor="w").pack(side=LEFT)
        var = StringVar(value=str(initial))
        entry = Entry(row, textvariable=var)
        entry.pack(side=LEFT, fill=X, expand=True)
        self._fields[key] = var

    def _build_move_group(self, parent, group, events):
        t = self.t
        e_start = events[group["start"]]
        e_end = events[group["end"]]
        self._add_field(parent, t.get("start_x", "Start X"), "start_x", e_start["x"])
        self._add_field(parent, t.get("start_y", "Start Y"), "start_y", e_start["y"])
        self._add_field(parent, t.get("end_x", "End X"), "end_x", e_end["x"])
        self._add_field(parent, t.get("end_y", "End Y"), "end_y", e_end["y"])
        self._add_field(parent, t.get("timestamp", "Delay (s)"), "timestamp", e_start.get("timestamp", 0))
        self._group_data = group

    def _build_click(self, parent, ev):
        t = self.t
        self._add_field(parent, t.get("coord_x", "X"), "x", ev["x"])
        self._add_field(parent, t.get("coord_y", "Y"), "y", ev["y"])
        self._add_field(parent, t.get("timestamp", "Delay (s)"), "timestamp", ev.get("timestamp", 0))

    def _build_keyboard(self, parent, ev):
        t = self.t
        self._add_field(parent, t.get("timestamp", "Delay (s)"), "timestamp", ev.get("timestamp", 0))

    def _build_scroll(self, parent, ev):
        t = self.t
        self._add_field(parent, "dx", "dx", ev.get("dx", 0))
        self._add_field(parent, "dy", "dy", ev.get("dy", 0))
        self._add_field(parent, t.get("timestamp", "Delay (s)"), "timestamp", ev.get("timestamp", 0))

    def _build_generic(self, parent, ev):
        t = self.t
        self._add_field(parent, t.get("timestamp", "Delay (s)"), "timestamp", ev.get("timestamp", 0))

    def _confirm(self):
        events = self.main_app.macro.macro_events.get("events", [])
        group = self.macro_editor._groups[self.group_index]

        try:
            if group["kind"] == "move_group":
                start_i = group["start"]
                end_i = group["end"]
                nx1 = int(float(self._fields["start_x"].get()))
                ny1 = int(float(self._fields["start_y"].get()))
                nx2 = int(float(self._fields["end_x"].get()))
                ny2 = int(float(self._fields["end_y"].get()))
                ts = float(self._fields["timestamp"].get())
                events[start_i]["timestamp"] = ts

                n = end_i - start_i
                for k in range(start_i, end_i + 1):
                    if n == 0:
                        t_val = 0.0
                    else:
                        t_val = (k - start_i) / n
                    events[k]["x"] = round(nx1 + t_val * (nx2 - nx1))
                    events[k]["y"] = round(ny1 + t_val * (ny2 - ny1))

                if "comment" in self._fields:
                    events[start_i]["comment"] = self._fields["comment"].get()

            elif group["kind"] == "single":
                idx = group["index"]
                ev = events[idx]
                etype = ev["type"]

                if "timestamp" in self._fields:
                    ev["timestamp"] = float(self._fields["timestamp"].get())
                if "comment" in self._fields:
                    ev["comment"] = self._fields["comment"].get()

                if etype in ("leftClickEvent", "rightClickEvent", "middleClickEvent"):
                    ev["x"] = int(float(self._fields["x"].get()))
                    ev["y"] = int(float(self._fields["y"].get()))
                elif etype == "scrollEvent":
                    ev["dx"] = int(float(self._fields["dx"].get()))
                    ev["dy"] = int(float(self._fields["dy"].get()))

        except (ValueError, KeyError):
            pass

        self.macro_editor.refresh(self.main_app.macro.macro_events)
        self.destroy()
