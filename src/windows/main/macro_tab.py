class MacroTab:
    """Holds all per-tab state for one open macro."""

    def __init__(self, name, frame, editor):
        self.name = name
        self.frame = frame        # ttk.Frame inside Notebook
        self.editor = editor      # MacroEditor widget
        self.macro_events = {"events": []}
        self.macro_recorded = False
        self.macro_saved = False
        self.current_file = None
