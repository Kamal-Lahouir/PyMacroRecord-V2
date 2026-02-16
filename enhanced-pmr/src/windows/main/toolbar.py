from os import path
from tkinter import DISABLED, LEFT, NORMAL, PhotoImage, VERTICAL, StringVar
from tkinter.ttk import Button, Combobox, Frame, Label, Separator

from utils.get_file import resource_path


class Toolbar(Frame):
    """Top toolbar with transport controls and editor action buttons."""

    def __init__(self, main_app):
        super().__init__(main_app, style="Toolbar.TFrame")
        self.main_app = main_app
        text = main_app.text_content

        # Load button images
        self.play_img = PhotoImage(
            file=resource_path(path.join("assets", "button", "play.png"))
        )
        self.record_img = PhotoImage(
            file=resource_path(path.join("assets", "button", "record.png"))
        )
        self.stop_img = PhotoImage(
            file=resource_path(path.join("assets", "button", "stop.png"))
        )

        # Transport controls
        self.record_btn = Button(
            self, image=self.record_img, command=main_app.macro.start_record,
            style="Toolbar.TButton",
        )
        self.record_btn.pack(side=LEFT, padx=(10, 3), pady=6)

        self.play_btn = Button(
            self, image=self.play_img, state=DISABLED,
            style="Toolbar.TButton",
        )
        self.play_btn.pack(side=LEFT, padx=3, pady=6)

        # Separator between transport and editor actions
        sep = Separator(self, orient=VERTICAL)
        sep.pack(side=LEFT, fill="y", padx=10, pady=6)

        # Editor action buttons
        editor_text = text.get("editor", {})

        self.insert_btn = Button(
            self,
            text=editor_text.get("insert_event", "Insert"),
            command=self._on_insert,
            state=DISABLED,
            style="ToolbarText.TButton",
        )
        self.insert_btn.pack(side=LEFT, padx=3, pady=6)

        self.delete_btn = Button(
            self,
            text=editor_text.get("delete_event", "Delete"),
            command=self._on_delete,
            state=DISABLED,
            style="ToolbarText.TButton",
        )
        self.delete_btn.pack(side=LEFT, padx=3, pady=6)

        sep2 = Separator(self, orient=VERTICAL)
        sep2.pack(side=LEFT, fill="y", padx=6, pady=6)

        self.move_up_btn = Button(
            self,
            text=editor_text.get("move_up", "Move Up"),
            command=self._on_move_up,
            state=DISABLED,
            style="ToolbarText.TButton",
        )
        self.move_up_btn.pack(side=LEFT, padx=3, pady=6)

        self.move_down_btn = Button(
            self,
            text=editor_text.get("move_down", "Move Down"),
            command=self._on_move_down,
            state=DISABLED,
            style="ToolbarText.TButton",
        )
        self.move_down_btn.pack(side=LEFT, padx=3, pady=6)

        sep3 = Separator(self, orient=VERTICAL)
        sep3.pack(side=LEFT, fill="y", padx=6, pady=6)

        self.copy_btn = Button(
            self,
            text=editor_text.get("copy", "Copy"),
            command=self._on_copy,
            state=DISABLED,
            style="ToolbarText.TButton",
        )
        self.copy_btn.pack(side=LEFT, padx=3, pady=6)

        self.paste_btn = Button(
            self,
            text=editor_text.get("paste", "Paste"),
            command=self._on_paste,
            state=DISABLED,
            style="ToolbarText.TButton",
        )
        self.paste_btn.pack(side=LEFT, padx=3, pady=6)

        sep4 = Separator(self, orient=VERTICAL)
        sep4.pack(side=LEFT, fill="y", padx=6, pady=6)

        self.simplify_btn = Button(
            self,
            text=editor_text.get("simplify_path", "Simplify Path..."),
            command=self._on_simplify,
            state=DISABLED,
            style="ToolbarText.TButton",
        )
        self.simplify_btn.pack(side=LEFT, padx=3, pady=6)

        # Label navigation
        sep5 = Separator(self, orient=VERTICAL)
        sep5.pack(side=LEFT, fill="y", padx=6, pady=6)

        label_lbl = Label(self, text=editor_text.get("jump_to_label", "Jump to:"), style="Toolbar.TLabel")
        label_lbl.pack(side=LEFT, padx=(3, 2), pady=6)

        self._label_nav_var = StringVar()
        self.label_nav_combo = Combobox(
            self,
            textvariable=self._label_nav_var,
            width=15,
            state="readonly",
        )
        self.label_nav_combo.pack(side=LEFT, padx=2, pady=6)
        self.label_nav_combo.bind("<<ComboboxSelected>>", self._on_label_selected)
        self.label_nav_combo.configure(state=DISABLED)

    def _on_insert(self):
        editor = getattr(self.main_app, "event_editor", None)
        if editor:
            editor.insert_event_at_selection()

    def _on_delete(self):
        editor = getattr(self.main_app, "event_editor", None)
        if editor:
            editor.delete_selected()

    def _on_move_up(self):
        editor = getattr(self.main_app, "event_editor", None)
        if editor:
            editor.move_selected_up()

    def _on_move_down(self):
        editor = getattr(self.main_app, "event_editor", None)
        if editor:
            editor.move_selected_down()

    def _on_copy(self):
        editor = getattr(self.main_app, "event_editor", None)
        if editor:
            editor.copy_selected()

    def _on_paste(self):
        editor = getattr(self.main_app, "event_editor", None)
        if editor:
            editor.paste_at_selection()

    def _on_simplify(self):
        editor = getattr(self.main_app, "event_editor", None)
        if editor:
            editor._on_simplify_path()

    def _on_label_selected(self, event=None):
        """Jump to the selected label in the editor."""
        label = self._label_nav_var.get()
        if not label:
            return
        editor = getattr(self.main_app, "event_editor", None)
        if not editor:
            return
        index = self.main_app.macro_editor.get_event_by_label(label)
        if index is not None:
            # Select and scroll to the event
            iid = editor._index_to_iid.get(index)
            if iid:
                editor.tree.selection_set(iid)
                editor.tree.see(iid)
                editor.tree.focus(iid)

    def refresh_label_list(self):
        """Update the label navigation dropdown with current labels."""
        labels = self.main_app.macro_editor.get_all_labels()
        self.label_nav_combo["values"] = labels
        if labels:
            self.label_nav_combo.configure(state="readonly")
        else:
            self.label_nav_combo.configure(state=DISABLED)
            self._label_nav_var.set("")

    def update_state(self, state):
        """Update button states based on app state.
        state: 'idle', 'recording', 'playing', 'has_recording'
        """
        if state == "idle":
            self.record_btn.configure(
                image=self.record_img,
                command=self.main_app.macro.start_record,
                state=NORMAL,
            )
            self.play_btn.configure(state=DISABLED, image=self.play_img)
            self._set_editor_buttons(DISABLED)

        elif state == "recording":
            self.record_btn.configure(
                image=self.stop_img,
                command=self.main_app.macro.stop_record,
            )
            self.play_btn.configure(state=DISABLED)
            self._set_editor_buttons(DISABLED)

        elif state == "playing":
            self.play_btn.configure(
                image=self.stop_img,
                command=lambda: self.main_app.macro.stop_playback(True),
            )
            self.record_btn.configure(state=DISABLED)
            self._set_editor_buttons(DISABLED)

        elif state == "has_recording":
            self.record_btn.configure(
                image=self.record_img,
                command=self.main_app.macro.start_record,
                state=NORMAL,
            )
            self.play_btn.configure(
                state=NORMAL,
                image=self.play_img,
                command=self.main_app.macro.start_playback,
            )
            self._set_editor_buttons(NORMAL)

    def _set_editor_buttons(self, state):
        for btn in (
            self.insert_btn,
            self.delete_btn,
            self.move_up_btn,
            self.move_down_btn,
            self.copy_btn,
            self.paste_btn,
            self.simplify_btn,
        ):
            btn.configure(state=state)
        if state == NORMAL:
            self.refresh_label_list()
        else:
            self.label_nav_combo.configure(state=DISABLED)
