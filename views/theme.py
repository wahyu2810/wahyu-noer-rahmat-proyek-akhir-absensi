"""Palet warna & util tema bersama bergaya 'Coding / Teknik Informatika'.

Dipakai oleh halaman login dan dashboard agar tampilannya seragam.
"""
import tkinter as tk
from tkinter import ttk


# ---- Palet warna tema "Coding / Teknik Informatika" ----
COLOR_BG = "#0d1117"        # GitHub dark
COLOR_PANEL = "#161b22"     # panel editor
COLOR_ACCENT = "#2dd4bf"    # teal/cyan terminal
COLOR_ACCENT_DARK = "#14b8a6"
COLOR_CARD = "#0d1117"
COLOR_TEXT = "#e6edf3"
COLOR_MUTED = "#7d8590"
COLOR_FIELD = "#161b22"
COLOR_FIELD_FOCUS = "#1f2937"
COLOR_BORDER = "#30363d"

# Warna ala syntax highlighting
SYN_KEYWORD = "#ff7b72"     # merah - keyword
SYN_FUNC = "#d2a8ff"        # ungu - fungsi
SYN_STRING = "#a5d6ff"      # biru muda - string
SYN_COMMENT = "#8b949e"     # abu - komentar
SYN_NUMBER = "#79c0ff"      # biru - angka

MONO = "Consolas"


def center_window(window, width, height):
    """Posisikan window di tengah layar (sedikit ke atas)."""
    window.update_idletasks()
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 3
    window.geometry(f"{width}x{height}+{x}+{y}")


def make_title_bar(parent, filename):
    """Buat title-bar ala jendela editor: tiga titik + nama file."""
    bar = tk.Frame(parent, bg="#21262d", height=30)
    bar.pack(fill="x")
    bar.pack_propagate(False)
    for c in ("#ff5f56", "#ffbd2e", "#27c93f"):
        tk.Label(bar, text="●", font=("Segoe UI", 11), fg=c, bg="#21262d").pack(
            side="left", padx=(8, 0), pady=2
        )
    tk.Label(bar, text=filename, font=(MONO, 9), fg=COLOR_MUTED, bg="#21262d").pack(
        side="left", padx=10
    )
    return bar


def make_button(parent, text, command, primary=True):
    """Tombol bergaya terminal yang seragam dengan tombol login."""
    if primary:
        fg, bg, bg_hover = COLOR_BG, COLOR_ACCENT, COLOR_ACCENT_DARK
    else:
        fg, bg, bg_hover = COLOR_TEXT, COLOR_PANEL, COLOR_FIELD_FOCUS

    btn = tk.Button(
        parent, text=text, command=command,
        font=(MONO, 10, "bold"), fg=fg, bg=bg,
        activeforeground=fg, activebackground=bg_hover,
        relief="flat", cursor="hand2", bd=0, padx=14, pady=8,
    )
    if not primary:
        btn.config(highlightthickness=1, highlightbackground=COLOR_BORDER)
    btn.bind("<Enter>", lambda e: btn.config(bg=bg_hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def style_treeview(style_name="Coding.Treeview"):
    """Konfigurasi ttk.Treeview agar cocok dengan tema gelap. Sekali panggil."""
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        style_name,
        background=COLOR_PANEL,
        fieldbackground=COLOR_PANEL,
        foreground=COLOR_TEXT,
        rowheight=26,
        borderwidth=0,
        font=(MONO, 10),
    )
    style.map(
        style_name,
        background=[("selected", COLOR_ACCENT_DARK)],
        foreground=[("selected", COLOR_BG)],
    )
    style.configure(
        style_name + ".Heading",
        background="#21262d",
        foreground=COLOR_ACCENT,
        relief="flat",
        font=(MONO, 10, "bold"),
        padding=6,
    )
    style.map(
        style_name + ".Heading",
        background=[("active", "#2d333b")],
    )

    # Scrollbar gelap
    style.configure(
        "Coding.Vertical.TScrollbar",
        background=COLOR_PANEL,
        troughcolor=COLOR_BG,
        bordercolor=COLOR_BG,
        arrowcolor=COLOR_MUTED,
    )
    return style_name
