from tkinter import BooleanVar, StringVar, DISABLED, NORMAL, LEFT, X, W
from tkinter.ttk import Frame, Label, Checkbutton, Spinbox, Separator


class QuickSettingsBar(Frame):
    """Compact inline panel exposing the most-used recording and playback settings."""

    def __init__(self, parent):
        super().__init__(parent, relief="groove", borderwidth=1)
        self.main_app = parent
        self._updating = False  # guard against recursive trace callbacks

        s = parent.settings
        u = s.settings_dict
        t = parent.text_content.get("quick_settings", {})

        # ── Recording ─────────────────────────────────────────────────
        rec = Frame(self)
        rec.pack(side=LEFT, padx=(10, 4), pady=5)

        Label(rec, text=t.get("record_label", "● REC"), anchor=W).pack(side=LEFT, padx=(0, 6))

        self._mouse_move = BooleanVar(value=u["Recordings"]["Mouse_Move"])
        Checkbutton(rec, text=t.get("mouse_move", "Mouse Move"),
                    variable=self._mouse_move,
                    command=lambda: self._toggle("Recordings", "Mouse_Move",
                                                 self._mouse_move, "mouseMove")
                    ).pack(side=LEFT, padx=3)

        self._mouse_click = BooleanVar(value=u["Recordings"]["Mouse_Click"])
        Checkbutton(rec, text=t.get("mouse_click", "Clicks"),
                    variable=self._mouse_click,
                    command=lambda: self._toggle("Recordings", "Mouse_Click",
                                                 self._mouse_click, "mouseClick")
                    ).pack(side=LEFT, padx=3)

        self._keyboard = BooleanVar(value=u["Recordings"]["Keyboard"])
        Checkbutton(rec, text=t.get("keyboard", "Keys"),
                    variable=self._keyboard,
                    command=lambda: self._toggle("Recordings", "Keyboard",
                                                 self._keyboard, "keyboardInput")
                    ).pack(side=LEFT, padx=3)

        Separator(self, orient="vertical").pack(side=LEFT, fill="y", padx=10, pady=5)

        # ── Playback ───────────────────────────────────────────────────
        play = Frame(self)
        play.pack(side=LEFT, padx=(4, 10), pady=5, fill=X, expand=True)

        Label(play, text=t.get("play_label", "▶ PLAY"), anchor=W).pack(side=LEFT, padx=(0, 6))

        # Speed
        Label(play, text=t.get("speed", "Speed")).pack(side=LEFT)
        self._speed_var = StringVar(value=f"{u['Playback']['Speed']:.1f}")
        self._speed_spin = Spinbox(
            play, from_=0.1, to=10.0, increment=0.1,
            textvariable=self._speed_var, width=5, format="%.1f",
        )
        self._speed_spin.pack(side=LEFT, padx=(3, 10))
        self._speed_var.trace_add("write", self._on_speed_change)

        Separator(play, orient="vertical").pack(side=LEFT, fill="y", padx=8, pady=2)

        # Repeat
        Label(play, text=t.get("repeat", "Repeat")).pack(side=LEFT, padx=(8, 0))
        self._repeat_var = StringVar(value=str(u["Playback"]["Repeat"]["Times"]))
        self._repeat_spin = Spinbox(
            play, from_=1, to=99999, increment=1,
            textvariable=self._repeat_var, width=6,
        )
        self._repeat_spin.pack(side=LEFT, padx=(3, 2))
        self._repeat_var.trace_add("write", self._on_repeat_change)

        self._infinite = BooleanVar(value=u["Playback"]["Repeat"].get("Infinite", False))
        Checkbutton(play, text=t.get("infinite", "∞ Infinite"),
                    variable=self._infinite,
                    command=self._on_infinite_toggle
                    ).pack(side=LEFT, padx=(2, 10))

        Separator(play, orient="vertical").pack(side=LEFT, fill="y", padx=8, pady=2)

        # Delay between repeats
        Label(play, text=t.get("delay", "Delay")).pack(side=LEFT, padx=(8, 0))
        self._delay_var = StringVar(value=f"{u['Playback']['Repeat']['Delay']:.1f}")
        Spinbox(
            play, from_=0.0, to=9999.0, increment=0.1,
            textvariable=self._delay_var, width=6, format="%.1f",
        ).pack(side=LEFT, padx=(3, 2))
        Label(play, text="s").pack(side=LEFT)
        self._delay_var.trace_add("write", self._on_delay_change)

        # Apply initial infinite state
        self._on_infinite_toggle()

    # ── Helpers ───────────────────────────────────────────────────────

    def _toggle(self, category, key, var, menu_attr):
        """Toggle a boolean recording setting and keep the menu in sync."""
        self.main_app.settings.change_settings(category, key)
        menu = getattr(self.main_app, "menu", None)
        if menu and hasattr(menu, menu_attr):
            getattr(menu, menu_attr).set(var.get())

    def _on_speed_change(self, *_):
        if self._updating:
            return
        try:
            val = float(self._speed_var.get())
            if 0.1 <= val <= 10.0:
                self.main_app.settings.settings_dict["Playback"]["Speed"] = round(val, 2)
                self.main_app.settings.update_settings()
        except ValueError:
            pass

    def _on_repeat_change(self, *_):
        if self._updating:
            return
        try:
            val = int(self._repeat_var.get())
            if val >= 1:
                self.main_app.settings.settings_dict["Playback"]["Repeat"]["Times"] = val
                self.main_app.settings.update_settings()
        except ValueError:
            pass

    def _on_infinite_toggle(self):
        val = self._infinite.get()
        self.main_app.settings.settings_dict["Playback"]["Repeat"]["Infinite"] = val
        self.main_app.settings.update_settings()
        self._repeat_spin.configure(state=DISABLED if val else NORMAL)

    def _on_delay_change(self, *_):
        if self._updating:
            return
        try:
            val = float(self._delay_var.get())
            if val >= 0:
                self.main_app.settings.settings_dict["Playback"]["Repeat"]["Delay"] = round(val, 2)
                self.main_app.settings.update_settings()
        except ValueError:
            pass
