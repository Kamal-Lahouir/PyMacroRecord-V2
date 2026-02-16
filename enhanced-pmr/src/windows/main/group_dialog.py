from tkinter import BOTH, LEFT, W, X, StringVar, colorchooser
from tkinter.ttk import Button, Entry, Frame, Label, LabelFrame

from windows.popup import Popup


class GroupDialog(Popup):
    """Dialog for creating or editing an event group."""

    def __init__(self, main_app, event_indices=None, group_id=None):
        """
        Args:
            main_app: Main application instance
            event_indices: List of event indices to group (for new groups)
            group_id: Existing group ID (for editing)
        """
        text = main_app.text_content.get("editor", {})
        title = text.get("edit_group", "Edit Group") if group_id else text.get("create_group", "Create Group")
        super().__init__(title, 400, 200, main_app)

        self.main_app = main_app
        self.event_indices = event_indices or []
        self.group_id = group_id
        self.result_group_id = None
        self._selected_color = None

        # Load existing group data if editing
        if group_id and group_id in main_app.macro_editor.groups:
            group = main_app.macro_editor.groups[group_id]
            default_name = group["name"]
            self._selected_color = group.get("color")
        else:
            default_name = "New Group"

        # Name field
        name_frame = LabelFrame(self, text=text.get("group_name", "Group Name"))
        name_frame.pack(fill=X, padx=10, pady=(10, 4))

        self._name_var = StringVar(value=default_name)
        self._name_entry = Entry(name_frame, textvariable=self._name_var, width=30)
        self._name_entry.pack(padx=8, pady=6)
        self._name_entry.focus_set()
        self._name_entry.select_range(0, 'end')

        # Color picker
        color_frame = LabelFrame(self, text=text.get("group_color", "Group Color (optional)"))
        color_frame.pack(fill=X, padx=10, pady=4)

        color_inner = Frame(color_frame)
        color_inner.pack(fill=X, padx=8, pady=6)

        self._color_btn = Button(
            color_inner,
            text=text.get("choose_color", "Choose Color"),
            command=self._choose_color,
        )
        self._color_btn.pack(side=LEFT, padx=4)

        self._color_preview = Label(color_inner, text="    ", width=4)
        self._color_preview.pack(side=LEFT, padx=4)
        if self._selected_color:
            self._color_preview.configure(background=self._selected_color)

        clear_btn = Button(
            color_inner,
            text=text.get("clear_color", "Clear"),
            command=self._clear_color,
        )
        clear_btn.pack(side=LEFT, padx=4)

        # Buttons
        btn_frame = Frame(self)
        btn_frame.pack(fill=X, padx=10, pady=(4, 10))

        confirm_text = main_app.text_content.get("global", {}).get("confirm_button", "Confirm")
        cancel_text = main_app.text_content.get("global", {}).get("cancel_button", "Cancel")

        Button(btn_frame, text=confirm_text, command=self._confirm,
               style="Primary.TButton").pack(side=LEFT, padx=4)
        Button(btn_frame, text=cancel_text, command=self.destroy).pack(side=LEFT, padx=4)

        # Bind Enter key
        self.bind("<Return>", lambda e: self._confirm())

        self.wait_window()

    def _choose_color(self):
        """Open color chooser dialog."""
        color = colorchooser.askcolor(
            initialcolor=self._selected_color or "#ffffff",
            title="Choose Group Color"
        )
        if color and color[1]:  # color[1] is hex string
            self._selected_color = color[1]
            self._color_preview.configure(background=self._selected_color)

    def _clear_color(self):
        """Clear the selected color."""
        self._selected_color = None
        self._color_preview.configure(background="")

    def _confirm(self):
        """Create or update the group."""
        name = self._name_var.get().strip()
        if not name:
            name = "New Group"

        macro_editor = self.main_app.macro_editor

        if self.group_id:
            # Edit existing group
            macro_editor.update_group(
                self.group_id,
                name=name,
                color=self._selected_color
            )
            self.result_group_id = self.group_id
        else:
            # Create new group
            self.result_group_id = macro_editor.create_group(
                self.event_indices,
                name=name,
                color=self._selected_color
            )

        # Refresh editor
        editor = getattr(self.main_app, "event_editor", None)
        if editor:
            editor.refresh()

        self.destroy()
