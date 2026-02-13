from sys import argv
from tkinter import DISABLED, BooleanVar, Menu
from webbrowser import open as OpenUrl

from utils.record_file_management import RecordFileManagement
from windows.help.about import About
from windows.options.settings import Hotkeys, SelectLanguage
from windows.others.donors import Donors
from windows.others.timestamp import Timestamp
from windows.others.translators import Translators


class MenuBar(Menu):
    def __init__(self, parent):
        super().__init__(parent)

        settings = parent.settings
        userSettings = settings.settings_dict
        self.text_config = parent.text_content

        # Menu Setup
        my_menu = Menu(parent)
        parent.config(menu=my_menu)

        # ── File Menu ─────────────────────────────────────────────
        self.file_menu = Menu(my_menu, tearoff=0)
        my_menu.add_cascade(label=self.text_config["file_menu"]["file_text"], menu=self.file_menu)
        record_file_management = RecordFileManagement(parent, self)
        if len(argv) > 1:
            self.file_menu.add_command(label=self.text_config["file_menu"]["new_text"], accelerator="Ctrl+N", command=record_file_management.new_macro)
        else:
            self.file_menu.add_command(label=self.text_config["file_menu"]["new_text"], state=DISABLED, accelerator="Ctrl+N")
        self.file_menu.add_command(label=self.text_config["file_menu"]["load_text"], accelerator="Ctrl+L", command=record_file_management.load_macro)
        self.file_menu.add_separator()
        if len(argv) > 1:
            self.file_menu.add_command(label=self.text_config["file_menu"]["save_text"], accelerator="Ctrl+S", command=record_file_management.save_macro)
            self.file_menu.add_command(label=self.text_config["file_menu"]["save_as_text"], accelerator="Ctrl+Shift+S", command=record_file_management.save_macro_as)
        else:
            self.file_menu.add_command(label=self.text_config["file_menu"]["save_text"], accelerator="Ctrl+S", state=DISABLED)
            self.file_menu.add_command(label=self.text_config["file_menu"]["save_as_text"], accelerator="Ctrl+Shift+S", state=DISABLED)

        # ── Edit Menu ─────────────────────────────────────────────
        edit_text = self.text_config.get("edit_menu", {})
        editor_text = self.text_config.get("editor", {})
        self.edit_menu = Menu(my_menu, tearoff=0)
        my_menu.add_cascade(label=edit_text.get("edit_text", "Edit"), menu=self.edit_menu)

        self.edit_menu.add_command(
            label=editor_text.get("insert_event", "Insert Event"),
            accelerator="Ctrl+I",
            command=self._on_insert,
        )
        self.edit_menu.add_command(
            label=editor_text.get("delete_event", "Delete"),
            accelerator="Del",
            command=self._on_delete,
        )
        self.edit_menu.add_separator()
        self.edit_menu.add_command(
            label=editor_text.get("copy", "Copy"),
            accelerator="Ctrl+C",
            command=self._on_copy,
        )
        self.edit_menu.add_command(
            label=editor_text.get("paste", "Paste"),
            accelerator="Ctrl+V",
            command=self._on_paste,
        )
        self.edit_menu.add_separator()
        self.edit_menu.add_command(
            label=edit_text.get("select_all", "Select All"),
            accelerator="Ctrl+A",
            command=self._on_select_all,
        )
        self.edit_menu.add_separator()
        self.edit_menu.add_command(
            label=editor_text.get("simplify_path", "Simplify Path..."),
            command=self._on_simplify_path,
        )

        # ── View Menu ─────────────────────────────────────────────
        view_text = self.text_config.get("view_menu", {})
        self.view_menu = Menu(my_menu, tearoff=0)
        my_menu.add_cascade(label=view_text.get("view_text", "View"), menu=self.view_menu)
        self.view_menu.add_command(
            label=view_text.get("toggle_sidebar", "Toggle Sidebar"),
            command=self._toggle_sidebar,
        )

        # ── Options Menu (settings not in sidebar) ────────────────
        self.options_menu = Menu(my_menu, tearoff=0)
        my_menu.add_cascade(label=self.text_config["options_menu"]["options_text"], menu=self.options_menu)

        # Recordings Sub
        self.mouseMove = BooleanVar(value=userSettings["Recordings"]["Mouse_Move"])
        self.mouseClick = BooleanVar(value=userSettings["Recordings"]["Mouse_Click"])
        self.keyboardInput = BooleanVar(value=userSettings["Recordings"]["Keyboard"])
        recordings_sub = Menu(self.options_menu, tearoff=0)
        self.options_menu.add_cascade(label=self.text_config["options_menu"]["recordings_menu"]["recordings_text"], menu=recordings_sub)
        recordings_sub.add_checkbutton(label=self.text_config["options_menu"]["recordings_menu"]["mouse_movement_text"], variable=self.mouseMove,
                                       command=lambda: self._toggle_recording("Mouse_Move"))
        recordings_sub.add_checkbutton(label=self.text_config["options_menu"]["recordings_menu"]["mouse_click_text"], variable=self.mouseClick,
                                       command=lambda: self._toggle_recording("Mouse_Click"))
        recordings_sub.add_checkbutton(label=self.text_config["options_menu"]["recordings_menu"]["keyboard_text"], variable=self.keyboardInput,
                                       command=lambda: self._toggle_recording("Keyboard"))

        self.showEventsOnStatusBar = BooleanVar(value=userSettings["Recordings"]["Show_Events_On_Status_Bar"])
        recordings_sub.add_checkbutton(
            label=self.text_config["options_menu"]["recordings_menu"]["show_events_statut"],
            variable=self.showEventsOnStatusBar,
            command=lambda: settings.change_settings("Recordings", "Show_Events_On_Status_Bar"),
        )

        # Settings Sub
        self.options_sub = Menu(self.options_menu, tearoff=0)
        self.compactJson = BooleanVar(value=userSettings["Saving"]["Compact_json"])
        self.always_import_macro_settings = BooleanVar(value=userSettings["Loading"]["Always_import_macro_settings"])
        self.options_sub.add_checkbutton(label=self.text_config["options_menu"]["json_compact"], command=lambda: settings.change_settings("Saving", "Compact_json"), variable=self.compactJson)
        self.options_sub.add_checkbutton(label=self.text_config["options_menu"]["settings_menu"]["always_import_macro_settings"], command=lambda: settings.change_settings("Loading", "Always_import_macro_settings"), variable=self.always_import_macro_settings)
        self.options_menu.add_cascade(label=self.text_config["options_menu"]["settings_menu"]["settings_text"], menu=self.options_sub)
        self.options_sub.add_command(label=self.text_config["options_menu"]["settings_menu"]["hotkeys_text"], command=lambda: Hotkeys(self, parent))
        self.options_sub.add_command(label=self.text_config["options_menu"]["settings_menu"]["lang_text"], command=lambda: SelectLanguage(self, parent))

        minimization_sub = Menu(self.options_sub, tearoff=0)
        self.options_sub.add_cascade(label=self.text_config["options_menu"]["settings_menu"]["minimization_text"], menu=minimization_sub)
        self.minimization_playing = BooleanVar(value=userSettings["Minimization"]["When_Playing"])
        self.minimization_record = BooleanVar(value=userSettings["Minimization"]["When_Recording"])
        minimization_sub.add_checkbutton(label=self.text_config["options_menu"]["settings_menu"]["minimization_menu"]["minimization_when_playing_text"], variable=self.minimization_playing,
                                         command=lambda: settings.change_settings("Minimization", "When_Playing"))
        minimization_sub.add_checkbutton(label=self.text_config["options_menu"]["settings_menu"]["minimization_menu"]["minimization_when_recording_text"], variable=self.minimization_record,
                                         command=lambda: settings.change_settings("Minimization", "When_Recording"))

        # Others Sub
        self.others_sub = Menu(self.options_menu, tearoff=0)
        self.options_menu.add_cascade(label=self.text_config["options_menu"]["others_menu"]["others_text"], menu=self.others_sub)
        self.Check_update = BooleanVar(value=userSettings["Others"]["Check_update"])
        self.others_sub.add_checkbutton(label=self.text_config["options_menu"]["others_menu"]["check_update_text"], variable=self.Check_update, command=lambda: settings.change_settings("Others", "Check_update"))
        self.others_sub.add_command(label=self.text_config["options_menu"]["others_menu"]["reset_settings_text"], command=settings.reset_settings)
        self.others_sub.add_command(label=self.text_config["options_menu"]["others_menu"]["fixed_timestamp_text"], command=lambda: Timestamp(self, parent))

        # ── Help Section ──────────────────────────────────────────
        self.help_section = Menu(my_menu, tearoff=0)
        my_menu.add_cascade(label=self.text_config["help_menu"]["help_text"], menu=self.help_section)
        self.help_section.add_command(label=self.text_config["help_menu"]["tutorial_text"], command=lambda: OpenUrl("https://github.com/LOUDO56/PyMacroRecord/blob/main/TUTORIAL.md"))
        self.help_section.add_command(label=self.text_config["help_menu"]["website_text"],
                                      command=lambda: OpenUrl("https://www.pymacrorecord.com"))
        self.help_section.add_command(label=self.text_config["help_menu"]["about_text"], command=lambda: About(self, parent, parent.version.version, parent.version.update))

        # ── Other Section ─────────────────────────────────────────
        self.other_section = Menu(my_menu, tearoff=0)
        my_menu.add_cascade(label=self.text_config["others_menu"]["others_text"], menu=self.other_section)
        self.other_section.add_command(label=self.text_config["others_menu"]["donors_text"], command=lambda: Donors(self, parent))
        self.other_section.add_command(label=self.text_config["others_menu"]["translators_text"], command=lambda: Translators(self, parent))

    # ── Edit Menu Callbacks ───────────────────────────────────────

    def _on_insert(self):
        editor = getattr(self.master, "event_editor", None)
        if editor:
            editor.insert_event_at_selection()

    def _on_delete(self):
        editor = getattr(self.master, "event_editor", None)
        if editor:
            editor.delete_selected()

    def _on_copy(self):
        editor = getattr(self.master, "event_editor", None)
        if editor:
            editor.copy_selected()

    def _on_paste(self):
        editor = getattr(self.master, "event_editor", None)
        if editor:
            editor.paste_at_selection()

    def _on_select_all(self):
        editor = getattr(self.master, "event_editor", None)
        if editor:
            all_items = editor.tree.get_children()
            editor.tree.selection_set(all_items)

    def _on_simplify_path(self):
        editor = getattr(self.master, "event_editor", None)
        if editor:
            editor._on_simplify_path()

    def _toggle_sidebar(self):
        main_app = self.master
        try:
            main_app.main_paned.forget(main_app.sidebar)
        except Exception:
            main_app.main_paned.insert(0, main_app.sidebar, weight=0)

    def _toggle_recording(self, option):
        settings = self.master.settings
        settings.change_settings("Recordings", option)
        # Sync sidebar checkbuttons
        sidebar = getattr(self.master, "sidebar", None)
        if sidebar:
            sd = settings.settings_dict
            sidebar._mouse_move_var.set(sd["Recordings"]["Mouse_Move"])
            sidebar._mouse_click_var.set(sd["Recordings"]["Mouse_Click"])
            sidebar._keyboard_var.set(sd["Recordings"]["Keyboard"])
