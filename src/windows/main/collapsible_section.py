from tkinter import BOTH, LEFT, RIGHT, X
from tkinter.ttk import Frame, Label


class CollapsibleSection(Frame):
    """A frame with a clickable header that toggles content visibility."""

    def __init__(self, parent, title, expanded=True):
        super().__init__(parent)
        self._title = title
        self._expanded = expanded

        # Header
        self.header = Frame(self)
        self.header.pack(fill=X)

        arrow = "\u25bc" if expanded else "\u25b6"
        self.toggle_label = Label(
            self.header,
            text=f" {arrow}  {title}",
            font=("TkDefaultFont", 10, "bold"),
            cursor="hand2",
        )
        self.toggle_label.pack(side=LEFT, fill=X, expand=True, pady=(4, 2))
        self.toggle_label.bind("<Button-1>", self._toggle)

        # Separator line under header
        self._sep = Frame(self, height=1)
        self._sep.pack(fill=X, padx=4)

        # Content frame — users add widgets to this
        self.content = Frame(self)
        if expanded:
            self.content.pack(fill=BOTH, padx=8, pady=(2, 6))

    def _toggle(self, event=None):
        if self._expanded:
            self.content.pack_forget()
            self.toggle_label.configure(text=f" \u25b6  {self._title}")
        else:
            self.content.pack(fill=BOTH, padx=8, pady=(2, 6))
            self.toggle_label.configure(text=f" \u25bc  {self._title}")
        self._expanded = not self._expanded

    def is_expanded(self):
        return self._expanded
