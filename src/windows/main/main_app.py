import copy
import json
import sys
from json import load
from os import path
from sys import argv, platform
from threading import Thread
from time import time
from tkinter import (
    BOTH,
    BOTTOM,
    DISABLED,
    LEFT,
    Menu,
    RIGHT,
    SUNKEN,
    PhotoImage,
    W,
    X,
)
from tkinter.ttk import Button, Frame, Label, Notebook, Separator

from PIL import Image
from pystray import Icon, MenuItem

from hotkeys.hotkeys_manager import HotkeysManager
from macro import Macro
from utils.get_file import resource_path
from utils.not_windows import NotWindows
from utils.record_file_management import RecordFileManagement
from utils.user_settings import UserSettings
from utils.version import Version
from utils.warning_pop_up_save import confirm_save
from windows.editor.macro_editor import MacroEditor
from windows.main.macro_tab import MacroTab
from windows.main.quick_settings_bar import QuickSettingsBar
from windows.main.menu_bar import MenuBar
from windows.others.new_ver_avalaible import NewVerAvailable
from windows.window import Window


def deepcopy_dict_missing_entries(dst: dict, src: dict):
    # recursively copy entries that are in src but not in dst
    for k, v in src.items():
        if k not in dst:
            dst[k] = copy.deepcopy(v)
        elif isinstance(v, dict):
            deepcopy_dict_missing_entries(dst[k], v)

class MainApp(Window):
    """Main windows of the application"""

    def __init__(self):
        super().__init__("PyMacroRecord", 980, 560)
        self.resizable(True, True)
        self.minsize(720, 420)
        self.attributes("-topmost", 1)
        if platform == "win32":
            self.iconbitmap(resource_path(path.join("assets", "logo.ico")))

        self.settings = UserSettings(self)

        self.load_language()

        self.prevent_record = False
        self._tabs = []          # list[MacroTab]
        self._tab_counter = 0    # for naming new tabs
        self._switching_tabs = False  # guard against reentrant tab-change

        self.version = Version(self.settings.settings_dict, self)

        self.menu = MenuBar(self)  # Menu Bar
        self.macro = Macro(self)

        from macro.macro_editor import MacroEditor as MacroEditorData
        self.macro_editor = MacroEditorData(self.macro)

        self.validate_cmd = self.register(self.validate_input)

        self.hotkeyManager = HotkeysManager(self)

        self.status_text = Label(self, text='', relief=SUNKEN, anchor=W)
        if self.settings.settings_dict["Recordings"]["Show_Events_On_Status_Bar"]:
            self.status_text.pack(side=BOTTOM, fill=X)

        # Load button images
        self.playImg = PhotoImage(file=resource_path(path.join("assets", "button", "play.png")))
        self.recordImg = PhotoImage(file=resource_path(path.join("assets", "button", "record.png")))
        self.stopImg = PhotoImage(file=resource_path(path.join("assets", "button", "stop.png")))

        # Toolbar
        toolbar = Frame(self)
        toolbar.pack(side="top", fill=X, padx=4, pady=2)

        t_ed = self.text_content.get("editor", {})

        self.playBtn = Button(toolbar, image=self.playImg, command=self.macro.start_playback,
                              state=DISABLED)
        self.playBtn.pack(side=LEFT, padx=2)

        self.recordBtn = Button(toolbar, image=self.recordImg, command=self.macro.start_record)
        self.recordBtn.pack(side=LEFT, padx=2)

        Separator(toolbar, orient="vertical").pack(side=LEFT, fill="y", padx=6)

        self.editBtn = Button(toolbar, text=t_ed.get("toolbar_edit", "Edit"),
                              command=self._toolbar_edit, state=DISABLED)
        self.editBtn.pack(side=LEFT, padx=2)

        self.deleteBtn = Button(toolbar, text=t_ed.get("toolbar_delete", "Delete"),
                                command=self._toolbar_delete, state=DISABLED)
        self.deleteBtn.pack(side=LEFT, padx=2)

        self.playFromBtn = Button(toolbar, text=t_ed.get("toolbar_play_from", "▶ From here"),
                                  command=self._toolbar_play_from_here, state=DISABLED)
        self.playFromBtn.pack(side=LEFT, padx=2)

        Separator(toolbar, orient="vertical").pack(side=LEFT, fill="y", padx=6)

        self.moveUpBtn = Button(toolbar, text=t_ed.get("toolbar_move_up", "▲ Up"),
                                command=lambda: self.editor.move_up(),
                                state=DISABLED)
        self.moveUpBtn.pack(side=LEFT, padx=2)

        self.moveDownBtn = Button(toolbar, text=t_ed.get("toolbar_move_down", "▼ Down"),
                                  command=lambda: self.editor.move_down(),
                                  state=DISABLED)
        self.moveDownBtn.pack(side=LEFT, padx=2)

        Separator(toolbar, orient="vertical").pack(side=LEFT, fill="y", padx=6)

        self.toggleBtn = Button(toolbar, text=t_ed.get("toolbar_toggle_enabled", "Enable/Disable"),
                                command=lambda: self.editor.toggle_enabled(),
                                state=DISABLED)
        self.toggleBtn.pack(side=LEFT, padx=2)

        self.addDelayBtn = Button(toolbar, text=t_ed.get("toolbar_add_delay", "Add Delay"),
                                  command=self._toolbar_add_delay, state=DISABLED)
        self.addDelayBtn.pack(side=LEFT, padx=2)

        self.findReplaceBtn = Button(toolbar, text=t_ed.get("toolbar_find_replace", "Find & Replace"),
                                     command=self._toolbar_find_replace, state=DISABLED)
        self.findReplaceBtn.pack(side=LEFT, padx=2)

        # Quick settings bar (recording options + playback speed/repeat/delay)
        self.quick_settings = QuickSettingsBar(self)
        self.quick_settings.pack(side="top", fill=X, padx=4, pady=(0, 2))

        # Notebook for multiple tabs
        self._notebook = Notebook(self)
        self._notebook.pack(expand=True, fill=BOTH)
        self._notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self._notebook.bind("<Button-3>", self._on_tab_right_click)

        # "+" placeholder tab — clicking it opens a new tab
        self._plus_frame = Frame(self._notebook)
        self._notebook.add(self._plus_frame, text=" + ")

        # Initial tab
        self._add_tab()

        # Import record if opened with .pmr extension
        if len(argv) > 1:
            with open(sys.argv[1], 'r') as record:
                loaded_content = load(record)
            self.macro.import_record(loaded_content)
            self._sync_tab_events()
            self.playBtn.configure(state="normal", command=self.macro.start_playback)
            self.macro_recorded = True
            self.macro_saved = True
            self.editor.refresh(self.macro.macro_events)
            self._set_edit_delete_state("normal")
            tab = self._get_active_tab()
            if tab:
                name = path.splitext(path.basename(argv[1]))[0]
                tab.name = name
                self._notebook.tab(tab.frame, text=name)

        record_management = RecordFileManagement(self, self.menu)

        self.bind('<Control-Shift-S>', record_management.save_macro_as)
        self.bind('<Control-s>', record_management.save_macro)
        self.bind('<Control-l>', record_management.load_macro)
        self.bind('<Control-n>', record_management.new_macro)
        self.bind('<Control-t>', lambda e: self._add_tab())
        self.bind('<Control-w>', lambda e: self._close_active_tab())

        self.protocol("WM_DELETE_WINDOW", self.quit_software)
        if platform.lower() != "darwin":
            Thread(target=self.systemTray).start()

        self.attributes("-topmost", 0)

        if platform != "win32" and self.settings.first_time:
            NotWindows(self)

        if self.settings.settings_dict["Others"]["Check_update"]:
            if self.version.new_version != "" and self.version.version != self.version.new_version:
                if time() > self.settings.settings_dict["Others"]["Remind_new_ver_at"]:
                    NewVerAvailable(self, self.version.new_version)
        self.mainloop()

    # ── Per-tab state properties ───────────────────────────────────────

    @property
    def editor(self):
        tab = self._get_active_tab()
        return tab.editor if tab else None

    @property
    def macro_recorded(self):
        tab = self._get_active_tab()
        return tab.macro_recorded if tab else False

    @macro_recorded.setter
    def macro_recorded(self, v):
        tab = self._get_active_tab()
        if tab:
            tab.macro_recorded = v

    @property
    def macro_saved(self):
        tab = self._get_active_tab()
        return tab.macro_saved if tab else False

    @macro_saved.setter
    def macro_saved(self, v):
        tab = self._get_active_tab()
        if tab:
            tab.macro_saved = v

    @property
    def current_file(self):
        tab = self._get_active_tab()
        return tab.current_file if tab else None

    @current_file.setter
    def current_file(self, v):
        tab = self._get_active_tab()
        if tab:
            tab.current_file = v

    # ── Tab management ─────────────────────────────────────────────────

    def _add_tab(self, name=None, macro_events=None):
        self._tab_counter += 1
        if name is None:
            name = f"Macro {self._tab_counter}"

        frame = Frame(self._notebook)
        editor = MacroEditor(frame, self.text_content, main_app=self)
        editor.pack(expand=True, fill=BOTH)

        # Insert before the "+" tab
        plus_idx = self._notebook.index(str(self._plus_frame))
        self._notebook.insert(plus_idx, frame, text=name)

        tab = MacroTab(name=name, frame=frame, editor=editor)
        if macro_events is not None:
            tab.macro_events = macro_events
        self._tabs.append(tab)

        # Select the new tab (triggers _on_tab_changed)
        self._notebook.select(frame)
        return tab

    def _get_active_tab(self):
        if not self._tabs:
            return None
        selected = self._notebook.select()
        for tab in self._tabs:
            if str(tab.frame) == selected:
                return tab
        return None

    def _get_tab_by_frame(self, frame_path):
        for tab in self._tabs:
            if str(tab.frame) == frame_path:
                return tab
        return None

    def _sync_tab_events(self):
        """Push macro.macro_events reference into the active tab."""
        tab = self._get_active_tab()
        if tab is not None:
            tab.macro_events = self.macro.macro_events

    def _update_active_tab_title(self):
        """Update active tab's notebook title from current_file or tab.name."""
        tab = self._get_active_tab()
        if tab is None:
            return
        if tab.current_file:
            title = path.splitext(path.basename(tab.current_file))[0]
        else:
            title = tab.name
        self._notebook.tab(tab.frame, text=title)

    def _on_tab_changed(self, event=None):
        if self._switching_tabs:
            return
        selected = self._notebook.select()

        # Clicked the "+" tab → create a new tab
        if selected == str(self._plus_frame):
            self._switching_tabs = True
            self._add_tab()
            self._switching_tabs = False
            return

        tab = self._get_tab_by_frame(selected)
        if tab is None:
            return

        # Sync macro engine to this tab's events
        self.macro.macro_events = tab.macro_events

        # Update toolbar state to reflect this tab
        if tab.macro_recorded:
            self._set_edit_delete_state("normal")
            self.playBtn.configure(state="normal", command=self.macro.start_playback)
        else:
            self._set_edit_delete_state(DISABLED)
            self.playBtn.configure(state=DISABLED)

    def _on_tab_right_click(self, event):
        try:
            nb_idx = self._notebook.index(f"@{event.x},{event.y}")
        except Exception:
            return
        tab_id = self._notebook.tabs()[nb_idx]
        if tab_id == str(self._plus_frame):
            return
        menu = Menu(self, tearoff=0)
        menu.add_command(label="Close Tab",
                         command=lambda: self._close_tab_at(nb_idx))
        menu.add_command(label="Close All Tabs",
                         command=self._close_all_tabs)
        menu.post(event.x_root, event.y_root)

    def _close_active_tab(self):
        tab = self._get_active_tab()
        if tab is None:
            return
        nb_idx = list(self._notebook.tabs()).index(str(tab.frame))
        self._close_tab_at(nb_idx)

    def _close_tab_at(self, nb_idx):
        tab_id = self._notebook.tabs()[nb_idx]
        tab = self._get_tab_by_frame(tab_id)
        if tab is None:
            return
        if not tab.macro_saved and tab.macro_recorded:
            # Temporarily select this tab so properties work correctly
            self._notebook.select(tab.frame)
            wantToSave = confirm_save(self)
            if wantToSave:
                RecordFileManagement(self, self.menu).save_macro()
            elif wantToSave is None:
                return
        self._notebook.forget(nb_idx)
        self._tabs.remove(tab)
        tab.frame.destroy()
        if not self._tabs:
            self._switching_tabs = True
            self._add_tab()
            self._switching_tabs = False

    def _close_all_tabs(self):
        for tab in list(self._tabs):
            nb_tabs = self._notebook.tabs()
            try:
                nb_idx = list(nb_tabs).index(str(tab.frame))
            except ValueError:
                continue
            self._close_tab_at(nb_idx)

    # ── Language / system tray ─────────────────────────────────────────

    def load_language(self):
        self.lang = self.settings.settings_dict["Language"]
        with open(resource_path(path.join('langs', self.lang + '.json')), encoding='utf-8') as f:
            self.text_content = json.load(f)
        self.text_content = self.text_content["content"]

        if self.lang != "en":
            with open(resource_path(path.join('langs', 'en.json')), encoding='utf-8') as f:
                en = json.load(f)
            deepcopy_dict_missing_entries(self.text_content, en["content"])

    def systemTray(self):
        """Just to show little icon on system tray"""
        image = Image.open(resource_path(path.join("assets", "logo.ico")))
        menu = (
            MenuItem('Show', action=self.deiconify, default=True),
        )
        self.icon = Icon("name", image, "PyMacroRecord", menu)
        self.icon.run()

    def validate_input(self, action, value_if_allowed):
        """Prevents from adding letters on an Entry label"""
        if action == "1":  # Insert
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        return True

    def quit_software(self, force=False):
        if not force:
            # Check all tabs for unsaved changes
            for tab in self._tabs:
                if not tab.macro_saved and tab.macro_recorded:
                    self._notebook.select(tab.frame)
                    wantToSave = confirm_save(self)
                    if wantToSave:
                        RecordFileManagement(self, self.menu).save_macro()
                    elif wantToSave is None:
                        return
        if platform.lower() != "darwin":
            self.icon.stop()
        if platform.lower() == "linux":
            self.destroy()
        self.quit()

    def on_version_checked(self):
        about = getattr(self, 'about_window', None)
        if about is not None:
            updated_text = (
                self.version.update
                if self.version.update
                else self.text_content["help_menu"]["about_settings"]["version_check_update_text"]["checking"]
            )
            about.update_status(updated_text)

        if self.settings.settings_dict["Others"]["Check_update"]:
            try:
                if self.version.new_version != "" and self.version.version != self.version.new_version:
                    if time() > self.settings.settings_dict["Others"]["Remind_new_ver_at"]:
                        NewVerAvailable(self, self.version.new_version)
            except Exception:
                pass

    def _set_edit_delete_state(self, state):
        for btn in (self.editBtn, self.deleteBtn, self.playFromBtn,
                    self.moveUpBtn, self.moveDownBtn, self.toggleBtn,
                    self.addDelayBtn, self.findReplaceBtn):
            btn.configure(state=state)

    def _toolbar_edit(self):
        gi = self.editor.get_selected_group_index()
        if gi is None:
            return
        from windows.editor.edit_event_popup import EditEventPopup
        EditEventPopup(self, self.editor, gi)

    def _toolbar_delete(self):
        gi = self.editor.get_selected_group_index()
        if gi is None:
            return
        group = self.editor._groups[gi]
        events = self.macro.macro_events.get("events", [])
        if group["kind"] == "move_group":
            del events[group["start"]:group["end"] + 1]
        else:
            del events[group["index"]]
        self.editor.refresh(self.macro.macro_events)

    def _toolbar_play_from_here(self):
        gi = self.editor.get_selected_group_index()
        if gi is None or not self._groups_available():
            return
        group = self.editor._groups[gi]
        start_idx = group["start"] if group["kind"] == "move_group" else group["index"]
        self.macro.start_playback(start_event_index=start_idx)

    def _groups_available(self):
        return bool(self.editor._groups)

    def _toolbar_add_delay(self):
        from windows.editor.insert_delay_popup import InsertDelayPopup
        InsertDelayPopup(self, self.editor)

    def _toolbar_find_replace(self):
        from windows.editor.search_replace_popup import SearchReplacePopup
        SearchReplacePopup(self, self.editor)
