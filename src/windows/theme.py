"""Centralized theme for PyMacroRecord.

Defines COLORS, FONTS, and apply_theme(root) to configure all ttk widget
styles in one place.  Call apply_theme() once right after the Tk root is
created (before any widgets are constructed).
"""

import sys
from tkinter.ttk import Style

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
COLORS = {
    # Backgrounds
    "bg_primary":       "#FFFFFF",
    "bg_secondary":     "#F5F6F8",
    "bg_tertiary":      "#EBEDF0",
    "bg_surface":       "#FFFFFF",

    # Borders & separators
    "border":           "#D1D5DB",
    "border_light":     "#E5E7EB",
    "separator":        "#D1D5DB",

    # Text
    "text_primary":     "#1F2937",
    "text_secondary":   "#6B7280",
    "text_disabled":    "#9CA3AF",
    "text_inverse":     "#FFFFFF",

    # Accent (blue)
    "accent":           "#2563EB",
    "accent_hover":     "#1D4ED8",
    "accent_light":     "#DBEAFE",
    "accent_muted":     "#93C5FD",

    # Semantic
    "success":          "#059669",
    "warning":          "#D97706",
    "error":            "#DC2626",

    # Treeview event tags
    "tag_mouse_move":       "#E0EAFF",
    "tag_mouse_click":      "#FFE4E6",
    "tag_scroll":           "#FEF3C7",
    "tag_keyboard":         "#D1FAE5",
    "tag_mouse_path_group": "#C7D2FE",

    # Treeview heading
    "heading_bg":       "#F3F4F6",
    "heading_fg":       "#374151",

    # Selection
    "select_bg":        "#DBEAFE",
    "select_fg":        "#1E3A5F",

    # Status bar
    "statusbar_bg":     "#F3F4F6",
    "statusbar_fg":     "#6B7280",

    # Hyperlink
    "link":             "#2563EB",
    "link_hover":       "#1D4ED8",

    # Collapsible section header
    "section_header_bg": "#F0F1F3",
    "section_header_fg": "#374151",
}

# ---------------------------------------------------------------------------
# Font definitions (platform-aware)
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    _FAMILY = "Segoe UI"
elif sys.platform == "darwin":
    _FAMILY = "SF Pro Text"
else:
    _FAMILY = "Noto Sans"

FONTS = {
    "default":          (_FAMILY, 10),
    "default_bold":     (_FAMILY, 10, "bold"),
    "small":            (_FAMILY, 9),
    "heading":          (_FAMILY, 11, "bold"),
    "title":            (_FAMILY, 12, "bold"),
    "monospace":        ("Consolas" if sys.platform == "win32" else "Menlo", 10),
    "section_header":   (_FAMILY, 10, "bold"),
    "hotkey_display":   (_FAMILY, 12),
    "status_bar":       (_FAMILY, 9),
}


# ---------------------------------------------------------------------------
# apply_theme
# ---------------------------------------------------------------------------
def apply_theme(root):
    """Configure a modern ttk theme.  Call once after the Tk root is created."""

    style = Style(root)
    style.theme_use("clam")

    # ── Global defaults ──────────────────────────────────────────────
    style.configure(
        ".",
        font=FONTS["default"],
        background=COLORS["bg_primary"],
        foreground=COLORS["text_primary"],
        bordercolor=COLORS["border"],
        focuscolor=COLORS["accent"],
        darkcolor=COLORS["border"],
        lightcolor=COLORS["border"],
    )

    # ── TFrame ───────────────────────────────────────────────────────
    style.configure("TFrame", background=COLORS["bg_primary"])
    style.configure("Toolbar.TFrame", background=COLORS["bg_secondary"])
    style.configure("Sidebar.TFrame", background=COLORS["bg_secondary"])
    style.configure("SectionHeader.TFrame", background=COLORS["section_header_bg"])
    style.configure("SectionSep.TFrame", background=COLORS["border_light"])

    # ── TLabel ───────────────────────────────────────────────────────
    style.configure("TLabel",
                    background=COLORS["bg_primary"],
                    foreground=COLORS["text_primary"],
                    font=FONTS["default"])
    style.configure("Secondary.TLabel", foreground=COLORS["text_secondary"])
    style.configure("Heading.TLabel",
                    font=FONTS["heading"],
                    foreground=COLORS["text_primary"])
    style.configure("Title.TLabel",
                    font=FONTS["title"],
                    foreground=COLORS["text_primary"])
    style.configure("SectionHeader.TLabel",
                    font=FONTS["section_header"],
                    foreground=COLORS["section_header_fg"],
                    background=COLORS["section_header_bg"])
    style.configure("StatusBar.TLabel",
                    font=FONTS["status_bar"],
                    background=COLORS["statusbar_bg"],
                    foreground=COLORS["statusbar_fg"],
                    padding=(8, 4))
    style.configure("Sidebar.TLabel",
                    background=COLORS["bg_secondary"],
                    foreground=COLORS["text_primary"],
                    font=FONTS["default"])
    style.configure("Hyperlink.TLabel",
                    foreground=COLORS["link"])
    style.configure("HotkeyDisplay.TLabel",
                    font=FONTS["hotkey_display"])

    # ── TButton ──────────────────────────────────────────────────────
    style.configure("TButton",
                    font=FONTS["default"],
                    padding=(10, 4),
                    borderwidth=1,
                    relief="solid",
                    background=COLORS["bg_primary"],
                    foreground=COLORS["text_primary"])
    style.map("TButton",
              background=[("active", COLORS["bg_tertiary"]),
                          ("disabled", COLORS["bg_secondary"])],
              foreground=[("disabled", COLORS["text_disabled"])],
              bordercolor=[("active", COLORS["accent"]),
                           ("focus", COLORS["accent"])])

    # Primary action button (Confirm / Apply / Simplify)
    style.configure("Primary.TButton",
                    background=COLORS["accent"],
                    foreground=COLORS["text_inverse"],
                    borderwidth=0,
                    padding=(12, 5),
                    font=FONTS["default_bold"])
    style.map("Primary.TButton",
              background=[("active", COLORS["accent_hover"]),
                          ("disabled", COLORS["accent_muted"])],
              foreground=[("disabled", COLORS["text_inverse"])])

    # Toolbar icon button (transport: record / play / stop)
    style.configure("Toolbar.TButton",
                    padding=(4, 4),
                    borderwidth=0,
                    relief="flat",
                    background=COLORS["bg_secondary"])
    style.map("Toolbar.TButton",
              background=[("active", COLORS["bg_tertiary"]),
                          ("disabled", COLORS["bg_secondary"])],
              relief=[("active", "flat")])

    # Toolbar text button (Insert, Delete, Move Up/Down, Copy, Paste, …)
    style.configure("ToolbarText.TButton",
                    padding=(8, 3),
                    borderwidth=1,
                    relief="solid",
                    background=COLORS["bg_secondary"],
                    font=FONTS["default"])
    style.map("ToolbarText.TButton",
              background=[("active", COLORS["bg_tertiary"]),
                          ("disabled", COLORS["bg_secondary"])],
              foreground=[("disabled", COLORS["text_disabled"])],
              bordercolor=[("active", COLORS["accent"])])

    # ── TEntry ───────────────────────────────────────────────────────
    # In clam, "background" draws the outer area around the field; set it
    # to bordercolor so it merges into the border and looks clean on any
    # parent background (white or gray).
    _input_bg = COLORS["border"]
    style.configure("TEntry",
                    font=FONTS["default"],
                    padding=(4, 3),
                    borderwidth=1,
                    relief="solid",
                    background=_input_bg,
                    fieldbackground=COLORS["bg_primary"],
                    foreground=COLORS["text_primary"],
                    bordercolor=COLORS["border"],
                    lightcolor=COLORS["border"],
                    darkcolor=COLORS["border"])
    style.map("TEntry",
              bordercolor=[("focus", COLORS["accent"])],
              lightcolor=[("focus", COLORS["accent"])],
              darkcolor=[("focus", COLORS["accent"])],
              background=[("focus", COLORS["accent"])])

    # ── TSpinbox ─────────────────────────────────────────────────────
    style.configure("TSpinbox",
                    font=FONTS["default"],
                    padding=(4, 3),
                    borderwidth=1,
                    background=_input_bg,
                    fieldbackground=COLORS["bg_primary"],
                    foreground=COLORS["text_primary"],
                    bordercolor=COLORS["border"],
                    lightcolor=COLORS["border"],
                    darkcolor=COLORS["border"],
                    arrowsize=14)
    style.map("TSpinbox",
              bordercolor=[("focus", COLORS["accent"])],
              lightcolor=[("focus", COLORS["accent"])],
              darkcolor=[("focus", COLORS["accent"])],
              background=[("focus", COLORS["accent"])],
              fieldbackground=[("readonly", COLORS["bg_secondary"])])

    # ── TCombobox ────────────────────────────────────────────────────
    style.configure("TCombobox",
                    font=FONTS["default"],
                    padding=(4, 3),
                    borderwidth=1,
                    background=_input_bg,
                    fieldbackground=COLORS["bg_primary"],
                    foreground=COLORS["text_primary"],
                    bordercolor=COLORS["border"],
                    lightcolor=COLORS["border"],
                    darkcolor=COLORS["border"],
                    arrowsize=14)
    style.map("TCombobox",
              bordercolor=[("focus", COLORS["accent"])],
              lightcolor=[("focus", COLORS["accent"])],
              darkcolor=[("focus", COLORS["accent"])],
              background=[("focus", COLORS["accent"])],
              fieldbackground=[("readonly", COLORS["bg_primary"])])
    # Combobox dropdown listbox (tk, not ttk)
    root.option_add("*TCombobox*Listbox.font", FONTS["default"])
    root.option_add("*TCombobox*Listbox.background", COLORS["bg_primary"])
    root.option_add("*TCombobox*Listbox.foreground", COLORS["text_primary"])
    root.option_add("*TCombobox*Listbox.selectBackground", COLORS["accent"])
    root.option_add("*TCombobox*Listbox.selectForeground", COLORS["text_inverse"])

    # ── TCheckbutton ─────────────────────────────────────────────────
    style.configure("TCheckbutton",
                    font=FONTS["default"],
                    background=COLORS["bg_primary"],
                    foreground=COLORS["text_primary"],
                    indicatormargin=4)
    style.map("TCheckbutton",
              background=[("active", COLORS["bg_tertiary"])],
              indicatorcolor=[("selected", COLORS["accent"]),
                              ("!selected", COLORS["bg_primary"])])

    style.configure("Sidebar.TCheckbutton",
                    background=COLORS["bg_secondary"])
    style.map("Sidebar.TCheckbutton",
              background=[("active", COLORS["bg_tertiary"])],
              indicatorcolor=[("selected", COLORS["accent"]),
                              ("!selected", COLORS["bg_secondary"])])

    # Filter bar checkbutton (search & filter bar)
    style.configure("Filter.TCheckbutton",
                    background=COLORS["bg_secondary"],
                    font=FONTS["small"],
                    padding=(2, 1))
    style.map("Filter.TCheckbutton",
              background=[("active", COLORS["bg_tertiary"])],
              indicatorcolor=[("selected", COLORS["accent"]),
                              ("!selected", COLORS["bg_secondary"])])

    style.configure("FilterBar.TFrame", background=COLORS["bg_secondary"])
    style.configure("FilterBar.TLabel",
                    background=COLORS["bg_secondary"],
                    foreground=COLORS["text_secondary"],
                    font=FONTS["small"])

    # ── TScrollbar ───────────────────────────────────────────────────
    style.configure("TScrollbar",
                    background=COLORS["bg_secondary"],
                    troughcolor=COLORS["bg_primary"],
                    borderwidth=0,
                    arrowsize=14)
    style.map("TScrollbar",
              background=[("active", COLORS["border"]),
                          ("!active", COLORS["bg_tertiary"])])

    # ── TSeparator ───────────────────────────────────────────────────
    style.configure("TSeparator", background=COLORS["separator"])

    # ── TLabelframe ──────────────────────────────────────────────────
    style.configure("TLabelframe",
                    background=COLORS["bg_primary"],
                    foreground=COLORS["text_primary"],
                    bordercolor=COLORS["border_light"],
                    relief="solid",
                    borderwidth=1,
                    padding=6)
    style.configure("TLabelframe.Label",
                    font=FONTS["default_bold"],
                    foreground=COLORS["text_primary"],
                    background=COLORS["bg_primary"])

    # ── Treeview ─────────────────────────────────────────────────────
    style.configure("Treeview",
                    font=FONTS["default"],
                    background=COLORS["bg_primary"],
                    foreground=COLORS["text_primary"],
                    fieldbackground=COLORS["bg_primary"],
                    borderwidth=0,
                    rowheight=26)
    style.configure("Treeview.Heading",
                    font=FONTS["default_bold"],
                    background=COLORS["heading_bg"],
                    foreground=COLORS["heading_fg"],
                    borderwidth=1,
                    relief="solid",
                    padding=(6, 4))
    style.map("Treeview",
              background=[("selected", COLORS["select_bg"])],
              foreground=[("selected", COLORS["select_fg"])])
    style.map("Treeview.Heading",
              background=[("active", COLORS["bg_tertiary"])])

    # ── TScale ───────────────────────────────────────────────────────
    style.configure("Horizontal.TScale",
                    background=COLORS["bg_primary"],
                    troughcolor=COLORS["bg_tertiary"],
                    sliderlength=20,
                    borderwidth=1)
    style.map("Horizontal.TScale",
              background=[("active", COLORS["accent"])])

    # ── TPanedwindow ─────────────────────────────────────────────────
    style.configure("TPanedwindow",
                    background=COLORS["border_light"],
                    sashwidth=5,
                    sashrelief="flat")

    # ── TMenubutton (used by OptionMenu) ─────────────────────────────
    style.configure("TMenubutton",
                    font=FONTS["default"],
                    padding=(8, 4),
                    background=COLORS["bg_primary"],
                    foreground=COLORS["text_primary"],
                    bordercolor=COLORS["border"],
                    relief="solid",
                    borderwidth=1)
    style.map("TMenubutton",
              background=[("active", COLORS["bg_tertiary"])])


def get_menu_style():
    """Return a dict of keyword arguments to pass to tk.Menu() constructors."""
    return {
        "bg": COLORS["bg_primary"],
        "fg": COLORS["text_primary"],
        "activebackground": COLORS["accent"],
        "activeforeground": COLORS["text_inverse"],
        "font": FONTS["default"],
        "relief": "flat",
        "borderwidth": 0,
    }
