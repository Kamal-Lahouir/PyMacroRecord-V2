from tkinter import Tk

from windows.theme import COLORS, apply_theme


class Window(Tk):
    def __init__(self, name, w, h, resizable_window=False, min_w=0, min_h=0):
        super().__init__()
        apply_theme(self)
        self.configure(bg=COLORS["bg_primary"])
        self.title(name)
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        if resizable_window:
            if min_w and min_h:
                self.minsize(min_w, min_h)
        else:
            self.resizable(False, False)
