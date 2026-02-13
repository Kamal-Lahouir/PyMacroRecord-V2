from os import path
from tkinter import DISABLED, LEFT, NORMAL, PhotoImage, VERTICAL
from tkinter.ttk import Button, Frame, Separator

from utils.get_file import resource_path


class Toolbar(Frame):
    """Top toolbar with transport controls and editor action buttons."""

    def __init__(self, main_app):
        super().__init__(main_app)
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
            self, image=self.record_img, command=main_app.macro.start_record
        )
        self.record_btn.pack(side=LEFT, padx=(8, 2), pady=4)

        self.play_btn = Button(self, image=self.play_img, state=DISABLED)
        self.play_btn.pack(side=LEFT, padx=2, pady=4)

        # Separator between transport and editor actions
        sep = Separator(self, orient=VERTICAL)
        sep.pack(side=LEFT, fill="y", padx=8, pady=4)

        # Editor action buttons
        editor_text = text.get("editor", {})

        self.insert_btn = Button(
            self,
            text=editor_text.get("insert_event", "Insert"),
            command=self._on_insert,
            state=DISABLED,
        )
        self.insert_btn.pack(side=LEFT, padx=2, pady=4)

        self.delete_btn = Button(
            self,
            text=editor_text.get("delete_event", "Delete"),
            command=self._on_delete,
            state=DISABLED,
        )
        self.delete_btn.pack(side=LEFT, padx=2, pady=4)

        sep2 = Separator(self, orient=VERTICAL)
        sep2.pack(side=LEFT, fill="y", padx=4, pady=4)

        self.move_up_btn = Button(
            self,
            text=editor_text.get("move_up", "Move Up"),
            command=self._on_move_up,
            state=DISABLED,
        )
        self.move_up_btn.pack(side=LEFT, padx=2, pady=4)

        self.move_down_btn = Button(
            self,
            text=editor_text.get("move_down", "Move Down"),
            command=self._on_move_down,
            state=DISABLED,
        )
        self.move_down_btn.pack(side=LEFT, padx=2, pady=4)

        sep3 = Separator(self, orient=VERTICAL)
        sep3.pack(side=LEFT, fill="y", padx=4, pady=4)

        self.copy_btn = Button(
            self,
            text=editor_text.get("copy", "Copy"),
            command=self._on_copy,
            state=DISABLED,
        )
        self.copy_btn.pack(side=LEFT, padx=2, pady=4)

        self.paste_btn = Button(
            self,
            text=editor_text.get("paste", "Paste"),
            command=self._on_paste,
            state=DISABLED,
        )
        self.paste_btn.pack(side=LEFT, padx=2, pady=4)

        sep4 = Separator(self, orient=VERTICAL)
        sep4.pack(side=LEFT, fill="y", padx=4, pady=4)

        self.simplify_btn = Button(
            self,
            text=editor_text.get("simplify_path", "Simplify Path..."),
            command=self._on_simplify,
            state=DISABLED,
        )
        self.simplify_btn.pack(side=LEFT, padx=2, pady=4)

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
