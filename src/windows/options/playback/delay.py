from tkinter import BOTTOM, LEFT, TOP, StringVar, messagebox
from tkinter.ttk import Button, Frame, Label, Spinbox

from windows.popup import Popup


class Delay(Popup):
    def __init__(self, parent, main_app):
        super().__init__(main_app.text_content["options_menu"]["playback_menu"]["delay_settings"]["title"], 300, 150, parent)
        main_app.prevent_record = True
        self.settings = main_app.settings
        Label(self, text=main_app.text_content["options_menu"]["playback_menu"]["delay_settings"]["sub_text"]).pack(side=TOP, pady=10)
        userSettings = main_app.settings.settings_dict
        self._delay_val = StringVar(value=str(userSettings["Playback"]["Repeat"]["Delay"]))
        setNewDelayInput = Spinbox(self, from_=1, to=100000000, width=7,
                                   textvariable=self._delay_val)
        setNewDelayInput.pack(pady=20)
        buttonArea = Frame(self)
        Button(buttonArea, text=main_app.text_content["global"]["confirm_button"],
               command=lambda: self.setNewDelayNumber(setNewDelayInput.get(), main_app),
               style="Primary.TButton").pack(side=LEFT, padx=10)
        Button(buttonArea, text=main_app.text_content["global"]["cancel_button"], command=self.destroy).pack(side=LEFT, padx=10)
        buttonArea.pack(side=BOTTOM, pady=10)
        self.wait_window()
        main_app.prevent_record = False

    def setNewDelayNumber(self, val, main_app):
        """Function to set the new Delay numbers"""
        if float(val) < 0:
            messagebox.showerror(main_app.text_content["global"]["error"], main_app.text_content["options_menu"]["playback_menu"]["repeat_settings"]["error_new_value"])
        else:
            self.settings.change_settings("Playback", "Repeat", "Delay", float(val))
            self.destroy()
