from sys import platform
from tkinter import (
    ALL, BOTH, LEFT, NW, RIGHT, VERTICAL, W, X, Y,
    BooleanVar, Canvas, DoubleVar, IntVar, StringVar,
)
from tkinter.ttk import (
    Checkbutton, Combobox, Entry, Frame, Label, Scrollbar, Spinbox,
)

from windows.main.collapsible_section import CollapsibleSection
from windows.theme import COLORS


class Sidebar(Frame):
    """Scrollable sidebar with inline playback, recording, and after-playback options."""

    def __init__(self, main_app):
        super().__init__(main_app, width=290, style="Sidebar.TFrame")
        self.pack_propagate(False)  # Keep width stable during PanedWindow resize
        self.main_app = main_app
        self.settings = main_app.settings
        self.settings_dict = main_app.settings.settings_dict
        text = main_app.text_content

        self._scrollregion_pending = None

        # Scrollable container (Canvas is a tk widget — bg set directly)
        self.canvas = Canvas(
            self, borderwidth=0, highlightthickness=0,
            bg=COLORS["bg_secondary"],
        )
        self.scrollbar = Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.inner_frame = Frame(self.canvas, style="Sidebar.TFrame")

        self._canvas_window = self.canvas.create_window(
            (0, 0), window=self.inner_frame, anchor=NW
        )
        self.inner_frame.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        # Bind mousewheel
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        # ── Playback Section ─────────────────────────────────────────

        sidebar_text = text.get("sidebar", {})
        playback_text = text.get("options_menu", {}).get("playback_menu", {})

        self.playback_section = CollapsibleSection(
            self.inner_frame,
            sidebar_text.get("playback_section", "Playback"),
        )
        self.playback_section.pack(fill=X, padx=4, pady=2)
        pc = self.playback_section.content

        # Speed
        speed_frame = Frame(pc, style="SidebarContent.TFrame")
        speed_frame.pack(fill=X, pady=2)
        Label(speed_frame, text=sidebar_text.get("speed_label", "Speed") + ":",
              style="SidebarContent.TLabel").pack(side=LEFT, padx=(0, 4))
        self._speed_var = DoubleVar(value=self.settings_dict["Playback"]["Speed"])
        self._speed_spinbox = Spinbox(
            speed_frame,
            from_=0.1,
            to=10.0,
            increment=0.1,
            width=6,
            textvariable=self._speed_var,
            command=self._on_speed_change,
        )
        self._speed_spinbox.pack(side=LEFT)
        self._speed_spinbox.bind("<Return>", lambda e: self._on_speed_change())
        self._speed_spinbox.bind("<FocusOut>", lambda e: self._on_speed_change())

        # Repeat Times
        repeat_frame = Frame(pc, style="SidebarContent.TFrame")
        repeat_frame.pack(fill=X, pady=2)
        Label(repeat_frame, text=sidebar_text.get("repeat_label", "Repeat") + ":",
              style="SidebarContent.TLabel").pack(side=LEFT, padx=(0, 4))
        self._repeat_var = IntVar(value=self.settings_dict["Playback"]["Repeat"]["Times"])
        self._repeat_spinbox = Spinbox(
            repeat_frame,
            from_=1,
            to=100000000,
            width=8,
            textvariable=self._repeat_var,
            command=self._on_repeat_change,
        )
        self._repeat_spinbox.pack(side=LEFT)
        self._repeat_spinbox.bind("<Return>", lambda e: self._on_repeat_change())
        self._repeat_spinbox.bind("<FocusOut>", lambda e: self._on_repeat_change())

        # Infinite
        inf_frame = Frame(pc, style="SidebarContent.TFrame")
        inf_frame.pack(fill=X, pady=2)
        self._infinite_var = BooleanVar(
            value=self.settings_dict["Playback"]["Repeat"].get("Infinite", False)
        )
        Checkbutton(
            inf_frame,
            text=sidebar_text.get("infinite_label", "Infinite"),
            variable=self._infinite_var,
            command=self._on_infinite_change,
            style="SidebarContent.TCheckbutton",
        ).pack(side=LEFT)

        # Delay between repeats
        delay_frame = Frame(pc, style="SidebarContent.TFrame")
        delay_frame.pack(fill=X, pady=2)
        Label(delay_frame, text=sidebar_text.get("delay_label", "Delay (s)") + ":",
              style="SidebarContent.TLabel").pack(side=LEFT, padx=(0, 4))
        self._delay_var = IntVar(value=self.settings_dict["Playback"]["Repeat"]["Delay"])
        self._delay_spinbox = Spinbox(
            delay_frame,
            from_=0,
            to=100000000,
            width=8,
            textvariable=self._delay_var,
            command=self._on_delay_change,
        )
        self._delay_spinbox.pack(side=LEFT)
        self._delay_spinbox.bind("<Return>", lambda e: self._on_delay_change())
        self._delay_spinbox.bind("<FocusOut>", lambda e: self._on_delay_change())

        # Interval (H:M:S)
        self._build_time_row(
            pc,
            sidebar_text.get("interval_label", "Interval") + ":",
            "Interval",
        )

        # For duration (H:M:S)
        self._build_time_row(
            pc,
            sidebar_text.get("for_label", "For Duration") + ":",
            "For",
        )

        # Scheduled (H:M:S)
        self._build_time_row(
            pc,
            sidebar_text.get("scheduled_label", "Scheduled At") + ":",
            "Scheduled",
        )

        # ── Recording Section ────────────────────────────────────────

        self.recording_section = CollapsibleSection(
            self.inner_frame,
            sidebar_text.get("recording_section", "Recording"),
        )
        self.recording_section.pack(fill=X, padx=4, pady=2)
        rc = self.recording_section.content

        rec_text = text.get("options_menu", {}).get("recordings_menu", {})

        self._mouse_move_var = BooleanVar(
            value=self.settings_dict["Recordings"]["Mouse_Move"]
        )
        Checkbutton(
            rc,
            text=rec_text.get("mouse_movement_text", "Mouse Movement"),
            variable=self._mouse_move_var,
            command=lambda: self._toggle_setting("Recordings", "Mouse_Move"),
            style="SidebarContent.TCheckbutton",
        ).pack(fill=X, pady=1)

        self._mouse_click_var = BooleanVar(
            value=self.settings_dict["Recordings"]["Mouse_Click"]
        )
        Checkbutton(
            rc,
            text=rec_text.get("mouse_click_text", "Mouse Click"),
            variable=self._mouse_click_var,
            command=lambda: self._toggle_setting("Recordings", "Mouse_Click"),
            style="SidebarContent.TCheckbutton",
        ).pack(fill=X, pady=1)

        self._keyboard_var = BooleanVar(
            value=self.settings_dict["Recordings"]["Keyboard"]
        )
        Checkbutton(
            rc,
            text=rec_text.get("keyboard_text", "Keyboard"),
            variable=self._keyboard_var,
            command=lambda: self._toggle_setting("Recordings", "Keyboard"),
            style="SidebarContent.TCheckbutton",
        ).pack(fill=X, pady=1)

        # Mouse move resolution (pixels)
        res_frame = Frame(rc, style="SidebarContent.TFrame")
        res_frame.pack(fill=X, pady=(4, 1))
        Label(
            res_frame,
            text=sidebar_text.get("resolution_label", "Move resolution") + ":",
            style="SidebarContent.TLabel",
        ).pack(side=LEFT, padx=(0, 4))
        self._resolution_var = IntVar(
            value=self.settings_dict["Recordings"].get("Mouse_Move_Resolution", 1)
        )
        self._resolution_spinbox = Spinbox(
            res_frame,
            from_=1,
            to=100,
            width=4,
            textvariable=self._resolution_var,
            command=self._on_resolution_change,
        )
        self._resolution_spinbox.pack(side=LEFT)
        Label(res_frame, text="px", style="SidebarContent.TLabel").pack(
            side=LEFT, padx=(2, 0)
        )
        self._resolution_spinbox.bind("<Return>", lambda e: self._on_resolution_change())
        self._resolution_spinbox.bind("<FocusOut>", lambda e: self._on_resolution_change())

        # ── After Playback Section ───────────────────────────────────

        after_text = text.get("options_menu", {}).get("settings_menu", {}).get(
            "after_playback_settings", {}
        )

        self.after_section = CollapsibleSection(
            self.inner_frame,
            sidebar_text.get("after_playback_section", "After Playback"),
        )
        self.after_section.pack(fill=X, padx=4, pady=2)
        ac = self.after_section.content

        mode_options = [
            after_text.get("idle", "Idle"),
            after_text.get("quit_software", "Quit software"),
            after_text.get("standby", "Standby"),
            after_text.get("log_off_computer", "Log off computer"),
            after_text.get("turn_off_computer", "Turn off computer"),
            after_text.get("restart computer", "Restart computer"),
            after_text.get("hibernate_if_enabled", "Hibernate (if enabled)"),
        ]

        self._after_mode_var = StringVar(
            value=self.settings_dict["After_Playback"]["Mode"]
        )
        Label(ac, text=after_text.get("sub_text", "On playback complete") + ":",
              style="SidebarContent.TLabel").pack(fill=X, pady=(0, 2))
        self._after_combo = Combobox(
            ac,
            textvariable=self._after_mode_var,
            values=mode_options,
            state="readonly",
            width=22,
        )
        self._after_combo.pack(fill=X, pady=2)
        self._after_combo.bind("<<ComboboxSelected>>", self._on_after_mode_change)

    # ── Canvas / scrollregion helpers ────────────────────────────────

    def _on_canvas_configure(self, event):
        """Keep inner frame width in sync with canvas so content fills it."""
        self.canvas.itemconfigure(self._canvas_window, width=event.width)

    def _on_inner_configure(self, event=None):
        """Debounced scroll region update — avoids per-pixel recalc."""
        if self._scrollregion_pending is not None:
            self.after_cancel(self._scrollregion_pending)
        self._scrollregion_pending = self.after(
            20, self._update_scrollregion
        )

    def _update_scrollregion(self):
        self._scrollregion_pending = None
        self.canvas.configure(scrollregion=self.canvas.bbox(ALL))

    # ── Time Row Builder ─────────────────────────────────────────────

    def _build_time_row(self, parent, label_text, setting_key):
        """Build an H:M:S row for Interval/For/Scheduled settings."""
        total_seconds = self.settings_dict["Playback"]["Repeat"][setting_key]
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60

        frame = Frame(parent, style="SidebarContent.TFrame")
        frame.pack(fill=X, pady=2)
        Label(frame, text=label_text, style="SidebarContent.TLabel").pack(
            side=LEFT, padx=(0, 4)
        )

        h_var = IntVar(value=h)
        m_var = IntVar(value=m)
        s_var = IntVar(value=s)

        h_spin = Spinbox(frame, from_=0, to=24, width=3, textvariable=h_var)
        h_spin.pack(side=LEFT)
        Label(frame, text="h", style="SidebarContent.TLabel").pack(side=LEFT, padx=(0, 2))

        m_spin = Spinbox(frame, from_=0, to=59, width=3, textvariable=m_var)
        m_spin.pack(side=LEFT)
        Label(frame, text="m", style="SidebarContent.TLabel").pack(side=LEFT, padx=(0, 2))

        s_spin = Spinbox(frame, from_=0, to=59, width=3, textvariable=s_var)
        s_spin.pack(side=LEFT)
        Label(frame, text="s", style="SidebarContent.TLabel").pack(side=LEFT)

        def on_change(*_args):
            try:
                total = h_var.get() * 3600 + m_var.get() * 60 + s_var.get()
            except Exception:
                return
            self.settings.change_settings(
                "Playback", "Repeat", setting_key, total
            )

        for spin in (h_spin, m_spin, s_spin):
            spin.configure(command=on_change)
            spin.bind("<Return>", on_change)
            spin.bind("<FocusOut>", on_change)

        # Store references
        attr_prefix = f"_time_{setting_key.lower()}"
        setattr(self, f"{attr_prefix}_h", h_var)
        setattr(self, f"{attr_prefix}_m", m_var)
        setattr(self, f"{attr_prefix}_s", s_var)

    # ── Setting Callbacks ────────────────────────────────────────────

    def _on_speed_change(self):
        try:
            val = self._speed_var.get()
            if 0.1 <= val <= 10.0:
                self.settings.change_settings("Playback", "Speed", None, val)
        except Exception:
            pass

    def _on_repeat_change(self):
        try:
            val = self._repeat_var.get()
            if val >= 1:
                self.settings.change_settings("Playback", "Repeat", "Times", val)
        except Exception:
            pass

    def _on_infinite_change(self):
        self.settings.change_settings("Playback", "Repeat", "Infinite", self._infinite_var.get())

    def _on_delay_change(self):
        try:
            val = self._delay_var.get()
            if val >= 0:
                self.settings.change_settings("Playback", "Repeat", "Delay", val)
        except Exception:
            pass

    def _on_resolution_change(self):
        try:
            val = self._resolution_var.get()
            if 1 <= val <= 100:
                self.settings.change_settings(
                    "Recordings", "Mouse_Move_Resolution", None, val
                )
        except Exception:
            pass

    def _on_after_mode_change(self, event=None):
        self.settings.change_settings("After_Playback", "Mode", None, self._after_mode_var.get())

    def _toggle_setting(self, category, option):
        self.settings.change_settings(category, option)
        # Sync the menu bar checkbutton vars
        menu = self.main_app.menu
        if option == "Mouse_Move":
            menu.mouseMove.set(self.settings_dict["Recordings"]["Mouse_Move"])
        elif option == "Mouse_Click":
            menu.mouseClick.set(self.settings_dict["Recordings"]["Mouse_Click"])
        elif option == "Keyboard":
            menu.keyboardInput.set(self.settings_dict["Recordings"]["Keyboard"])

    # ── Mousewheel ───────────────────────────────────────────────────

    def _bind_mousewheel(self, event=None):
        if platform == "win32":
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        elif "darwin" in platform.lower():
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        else:
            self.canvas.bind_all("<Button-4>", self._on_mousewheel)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event=None):
        if platform == "win32":
            self.canvas.unbind_all("<MouseWheel>")
        elif "darwin" in platform.lower():
            self.canvas.unbind_all("<MouseWheel>")
        else:
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if platform == "win32":
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif "darwin" in platform.lower():
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

    # ── State Management ─────────────────────────────────────────────

    def update_state(self, state):
        """Enable/disable sidebar controls during recording/playback."""
        # Sidebar controls remain interactive in all states for now,
        # since settings changes during idle/has_recording are safe.
        pass

    def refresh_from_settings(self):
        """Re-read all settings and update sidebar widget values."""
        sd = self.settings_dict
        self._speed_var.set(sd["Playback"]["Speed"])
        self._repeat_var.set(sd["Playback"]["Repeat"]["Times"])
        self._infinite_var.set(sd["Playback"]["Repeat"].get("Infinite", False))
        self._delay_var.set(sd["Playback"]["Repeat"]["Delay"])
        self._after_mode_var.set(sd["After_Playback"]["Mode"])
        self._mouse_move_var.set(sd["Recordings"]["Mouse_Move"])
        self._mouse_click_var.set(sd["Recordings"]["Mouse_Click"])
        self._keyboard_var.set(sd["Recordings"]["Keyboard"])
        self._resolution_var.set(sd["Recordings"].get("Mouse_Move_Resolution", 1))
