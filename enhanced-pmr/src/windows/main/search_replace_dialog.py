from tkinter import BOTH, LEFT, W, X, BooleanVar, StringVar, messagebox
from tkinter.ttk import Button, Checkbutton, Combobox, Entry, Frame, Label, LabelFrame

from windows.popup import Popup


SEARCHABLE_FIELDS = [
    ("x", "X Coordinate"),
    ("y", "Y Coordinate"),
    ("key", "Keyboard Key"),
    ("label", "Label"),
    ("comment", "Comment"),
    ("timestamp", "Delay/Timestamp"),
]


class SearchReplaceDialog(Popup):
    """Dialog for finding and replacing field values across events."""

    def __init__(self, main_app):
        text = main_app.text_content.get("editor", {})
        super().__init__(
            text.get("search_replace_title", "Search & Replace"),
            450, 300, main_app
        )
        self.main_app = main_app

        # Field selector
        field_frame = LabelFrame(self, text="Field to Search")
        field_frame.pack(fill=X, padx=10, pady=(10, 4))

        self._field_var = StringVar(value=SEARCHABLE_FIELDS[0][0])
        self._field_combo = Combobox(
            field_frame,
            textvariable=self._field_var,
            values=[f[1] for f in SEARCHABLE_FIELDS],
            state="readonly",
            width=25,
        )
        self._field_combo.set(SEARCHABLE_FIELDS[0][1])
        self._field_combo.pack(padx=8, pady=6)

        # Find value
        find_frame = LabelFrame(self, text="Find Value")
        find_frame.pack(fill=X, padx=10, pady=4)

        self._find_var = StringVar()
        self._find_entry = Entry(find_frame, textvariable=self._find_var, width=35)
        self._find_entry.pack(padx=8, pady=6)
        self._find_entry.focus_set()

        # Replace value
        replace_frame = LabelFrame(self, text="Replace With")
        replace_frame.pack(fill=X, padx=10, pady=4)

        self._replace_var = StringVar()
        self._replace_entry = Entry(replace_frame, textvariable=self._replace_var, width=35)
        self._replace_entry.pack(padx=8, pady=6)

        # Options
        options_frame = Frame(self)
        options_frame.pack(fill=X, padx=10, pady=4)

        self._case_sensitive_var = BooleanVar(value=False)
        Checkbutton(
            options_frame,
            text="Case Sensitive",
            variable=self._case_sensitive_var
        ).pack(side=LEFT, padx=4)

        # Buttons
        btn_frame = Frame(self)
        btn_frame.pack(fill=X, padx=10, pady=(4, 10))

        Button(btn_frame, text="Find All", command=self._find_all).pack(side=LEFT, padx=4)
        Button(btn_frame, text="Replace All", command=self._replace_all,
               style="Primary.TButton").pack(side=LEFT, padx=4)
        Button(btn_frame, text="Close", command=self.destroy).pack(side=LEFT, padx=4)

    def _get_selected_field_key(self):
        """Get the field key from the selected label."""
        label = self._field_combo.get()
        for key, lbl in SEARCHABLE_FIELDS:
            if lbl == label:
                return key
        return SEARCHABLE_FIELDS[0][0]

    def _find_all(self):
        """Find all matching events and select them in the editor."""
        field = self._get_selected_field_key()
        find_value = self._find_var.get()

        if not find_value:
            messagebox.showwarning("Search & Replace", "Please enter a value to find.")
            return

        # Convert to appropriate type
        if field in ("x", "y"):
            try:
                find_value = int(find_value)
            except ValueError:
                messagebox.showerror("Search & Replace", "X and Y must be integers.")
                return
        elif field == "timestamp":
            try:
                find_value = float(find_value)
            except ValueError:
                messagebox.showerror("Search & Replace", "Timestamp must be a number.")
                return

        matches = self.main_app.macro_editor.find_events_by_field(
            field,
            find_value,
            case_sensitive=self._case_sensitive_var.get()
        )

        if not matches:
            messagebox.showinfo("Search & Replace", "No matches found.")
            return

        # Select matching events in editor
        editor = getattr(self.main_app, "event_editor", None)
        if editor:
            editor.tree.selection_remove(*editor.tree.selection())
            for idx in matches:
                iid = editor._index_to_iid.get(idx)
                if iid and editor.tree.exists(iid):
                    editor.tree.selection_add(iid)
            # Scroll to first match
            first_iid = editor._index_to_iid.get(matches[0])
            if first_iid:
                editor.tree.see(first_iid)

        messagebox.showinfo("Search & Replace", f"Found {len(matches)} match(es).")

    def _replace_all(self):
        """Replace all matching values."""
        field = self._get_selected_field_key()
        find_value = self._find_var.get()
        replace_value = self._replace_var.get()

        if not find_value:
            messagebox.showwarning("Search & Replace", "Please enter a value to find.")
            return

        # Convert to appropriate type
        if field in ("x", "y"):
            try:
                find_value = int(find_value)
                replace_value = int(replace_value)
            except ValueError:
                messagebox.showerror("Search & Replace", "X and Y must be integers.")
                return
        elif field == "timestamp":
            try:
                find_value = float(find_value)
                replace_value = float(replace_value)
            except ValueError:
                messagebox.showerror("Search & Replace", "Timestamp must be a number.")
                return

        matches = self.main_app.macro_editor.find_events_by_field(
            field,
            find_value,
            case_sensitive=self._case_sensitive_var.get()
        )

        if not matches:
            messagebox.showinfo("Search & Replace", "No matches found.")
            return

        count = self.main_app.macro_editor.replace_field_in_events(
            matches,
            field,
            replace_value
        )

        # Refresh editor
        editor = getattr(self.main_app, "event_editor", None)
        if editor:
            editor.refresh()

        messagebox.showinfo("Search & Replace", f"Replaced {count} value(s).")
