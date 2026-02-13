from tkinter import BOTH, HORIZONTAL, LEFT, RIGHT, W, X, DoubleVar
from tkinter.ttk import Button, Frame, Label, LabelFrame, Scale

from macro.macro_editor import MacroEditor
from windows.popup import Popup


class SimplifyPathDialog(Popup):
    """Dialog for simplifying a mouse path using the RDP algorithm."""

    def __init__(self, main_app, start_idx, end_idx):
        text = main_app.text_content.get("editor", {})
        super().__init__(
            text.get("simplify_dialog_title", "Simplify Mouse Path"),
            400, 240, main_app,
        )
        self.main_app = main_app
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.original_count = end_idx - start_idx + 1

        # Extract points once for preview
        events = main_app.macro_editor.events
        self._points = [
            (events[i].get("x", 0), events[i].get("y", 0))
            for i in range(start_idx, end_idx + 1)
        ]

        # ── Path Info ────────────────────────────────────────────────
        info_frame = LabelFrame(
            self, text=text.get("simplify_original", "Original points")
        )
        info_frame.pack(fill=X, padx=10, pady=(10, 4))

        Label(
            info_frame,
            text=f"{self.original_count} mouse move events",
        ).pack(padx=8, pady=4)

        # ── Tolerance ────────────────────────────────────────────────
        tolerance_frame = LabelFrame(
            self, text=text.get("simplify_tolerance", "Tolerance (pixels)")
        )
        tolerance_frame.pack(fill=X, padx=10, pady=4)

        self._tolerance_var = DoubleVar(value=5.0)

        slider_row = Frame(tolerance_frame)
        slider_row.pack(fill=X, padx=8, pady=(4, 0))

        self._tolerance_label = Label(slider_row, text="5.0", width=5)
        self._tolerance_label.pack(side=RIGHT, padx=(4, 0))

        self._tolerance_scale = Scale(
            slider_row,
            from_=1.0,
            to=50.0,
            orient=HORIZONTAL,
            variable=self._tolerance_var,
            command=self._on_tolerance_change,
        )
        self._tolerance_scale.pack(fill=X, expand=True)

        # Preview result
        self._preview_label = Label(tolerance_frame, text="")
        self._preview_label.pack(padx=8, pady=(2, 6))

        # ── Buttons ──────────────────────────────────────────────────
        btn_frame = Frame(self)
        btn_frame.pack(fill=X, padx=10, pady=(4, 10))

        Button(
            btn_frame,
            text=text.get("simplify_button", "Simplify"),
            command=self._confirm,
        ).pack(side=LEFT, padx=4)

        Button(
            btn_frame,
            text=self.main_app.text_content.get("global", {}).get("cancel_button", "Cancel"),
            command=self.destroy,
        ).pack(side=LEFT, padx=4)

        # Initial preview
        self._update_preview()
        self.wait_window()

    def _on_tolerance_change(self, *args):
        val = self._tolerance_var.get()
        self._tolerance_label.configure(text=f"{val:.1f}")
        self._update_preview()

    def _update_preview(self):
        """Show how many points would remain at current tolerance."""
        tolerance = self._tolerance_var.get()
        keep = MacroEditor._rdp(self._points, tolerance)
        removed = self.original_count - len(keep)
        text = self.main_app.text_content.get("editor", {})
        result_label = text.get("simplify_result", "Result")
        self._preview_label.configure(
            text=f"{result_label}: {self.original_count} \u2192 {len(keep)} points "
                 f"({removed} removed)"
        )

    def _confirm(self):
        tolerance = self._tolerance_var.get()
        self.main_app.macro_editor.simplify_path(
            self.start_idx, self.end_idx, tolerance
        )
        editor = getattr(self.main_app, "event_editor", None)
        if editor:
            editor.refresh()
        self.destroy()
