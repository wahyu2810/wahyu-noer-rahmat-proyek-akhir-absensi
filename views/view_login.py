import os
import sys
import tkinter as tk
from tkinter import messagebox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models.model_users import User
from views import theme as T

# ---- Palet warna diambil dari tema bersama (views/theme.py) ----
COLOR_BG = T.COLOR_BG
COLOR_PANEL = T.COLOR_PANEL
COLOR_ACCENT = T.COLOR_ACCENT
COLOR_ACCENT_DARK = T.COLOR_ACCENT_DARK
COLOR_CARD = T.COLOR_CARD
COLOR_TEXT = T.COLOR_TEXT
COLOR_MUTED = T.COLOR_MUTED
COLOR_FIELD = T.COLOR_FIELD
COLOR_FIELD_FOCUS = T.COLOR_FIELD_FOCUS
COLOR_BORDER = T.COLOR_BORDER

# Warna ala syntax highlighting
SYN_KEYWORD = T.SYN_KEYWORD
SYN_FUNC = T.SYN_FUNC
SYN_STRING = T.SYN_STRING
SYN_COMMENT = T.SYN_COMMENT
SYN_NUMBER = T.SYN_NUMBER

MONO = T.MONO


class LoginView:
    def __init__(self, master=None, on_login_success=None):
        self.master = master or tk.Tk()
        self.on_login_success = on_login_success

        self.master.title("Sistem Absensi  •  Login  </>")
        self.master.configure(bg=COLOR_BG)
        self.master.resizable(False, False)
        self._center_window(820, 500)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self._password_hidden = True

        self._build_ui()

    # ------------------------------------------------------------------ utils
    def _center_window(self, width, height):
        T.center_window(self.master, width, height)

    # ------------------------------------------------------------------- build
    def _build_ui(self):
        container = tk.Frame(self.master, bg=COLOR_BG)
        container.pack(fill="both", expand=True)

        self._build_left_panel(container)
        self._build_right_panel(container)

    def _build_left_panel(self, parent):
        left = tk.Frame(parent, bg=COLOR_PANEL, width=400)
        left.pack(side="left", fill="both")
        left.pack_propagate(False)

        # --- Header logo IT ---
        header = tk.Frame(left, bg=COLOR_PANEL)
        header.pack(fill="x", padx=28, pady=(26, 0))

        tk.Label(
            header, text="</>", font=(MONO, 30, "bold"),
            fg=COLOR_ACCENT, bg=COLOR_PANEL,
        ).pack(side="left")
        tk.Label(
            header, text="  Informatika", font=("Segoe UI", 18, "bold"),
            fg=COLOR_TEXT, bg=COLOR_PANEL,
        ).pack(side="left")

        # --- Mock terminal / code editor ---
        editor = tk.Frame(left, bg=COLOR_BG, highlightthickness=1,
                          highlightbackground=COLOR_BORDER)
        editor.pack(fill="both", expand=True, padx=24, pady=24)

        # Title bar ala window
        bar = tk.Frame(editor, bg="#21262d", height=30)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        for c in ("#ff5f56", "#ffbd2e", "#27c93f"):
            tk.Label(bar, text="●", font=("Segoe UI", 11), fg=c, bg="#21262d").pack(side="left", padx=(8, 0), pady=2)
        tk.Label(bar, text="login.py", font=(MONO, 9), fg=COLOR_MUTED, bg="#21262d").pack(side="left", padx=10)

        code = tk.Frame(editor, bg=COLOR_BG)
        code.pack(fill="both", expand=True, padx=14, pady=12)

        # Baris kode bergaya syntax highlight: (nomor, [(teks, warna), ...])
        lines = [
            ("1", [("# Sistem Absensi Mahasiswa", SYN_COMMENT)]),
            ("2", [("class ", SYN_KEYWORD), ("Mahasiswa", SYN_FUNC), (":", COLOR_TEXT)]),
            ("3", [("    jurusan = ", COLOR_TEXT), ('"Teknik Informatika"', SYN_STRING)]),
            ("4", [("    semangat = ", COLOR_TEXT), ("100", SYN_NUMBER)]),
            ("5", [("", COLOR_TEXT)]),
            ("6", [("    def ", SYN_KEYWORD), ("hadir", SYN_FUNC), ("(", COLOR_TEXT),
                   ("self", SYN_KEYWORD), ("):", COLOR_TEXT)]),
            ("7", [("        return ", SYN_KEYWORD), ("True", SYN_NUMBER)]),
        ]
        for num, segments in lines:
            row = tk.Frame(code, bg=COLOR_BG)
            row.pack(fill="x", anchor="w")
            tk.Label(row, text=num, font=(MONO, 10), fg="#484f58", bg=COLOR_BG, width=2).pack(side="left")
            for text, color in segments:
                if not text:
                    tk.Label(row, text=" ", font=(MONO, 10), bg=COLOR_BG).pack(side="left")
                    continue
                tk.Label(row, text=text, font=(MONO, 10), fg=color, bg=COLOR_BG).pack(side="left")

        # Footer terminal
        tk.Label(
            left, text="$ python main.py  ▍", font=(MONO, 10),
            fg=COLOR_ACCENT, bg=COLOR_PANEL, anchor="w",
        ).pack(fill="x", padx=28, pady=(0, 22))

    def _build_right_panel(self, parent):
        right = tk.Frame(parent, bg=COLOR_CARD)
        right.pack(side="left", fill="both", expand=True)

        form = tk.Frame(right, bg=COLOR_CARD)
        form.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            form, text="$ login --user", font=(MONO, 11),
            fg=COLOR_ACCENT, bg=COLOR_CARD,
        ).pack(anchor="w")
        tk.Label(
            form, text="Selamat Datang, Coder!", font=("Segoe UI", 21, "bold"),
            fg=COLOR_TEXT, bg=COLOR_CARD,
        ).pack(anchor="w", pady=(6, 2))
        tk.Label(
            form, text="// Masuk untuk mulai mencatat kehadiran",
            font=(MONO, 10), fg=COLOR_MUTED, bg=COLOR_CARD,
        ).pack(anchor="w", pady=(0, 24))

        # --- Username ---
        self.username_entry = self._build_field(form, "username", self.username_var, prefix=">")

        # --- Password ---
        self.password_entry = self._build_field(
            form, "password", self.password_var, show="*", prefix="#"
        )

        # --- Tombol Login ---
        self.login_btn = tk.Button(
            form, text="▶  Run Login", command=self.login,
            font=(MONO, 12, "bold"), fg=COLOR_BG, bg=COLOR_ACCENT,
            activeforeground=COLOR_BG, activebackground=COLOR_ACCENT_DARK,
            relief="flat", cursor="hand2", bd=0, pady=10,
        )
        self.login_btn.pack(fill="x", pady=(28, 0))
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg=COLOR_ACCENT_DARK))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg=COLOR_ACCENT))

        tk.Label(
            form, text="# demo · mahasiswa1 / dosen1  —  pass: 123456",
            font=(MONO, 9), fg=COLOR_MUTED, bg=COLOR_CARD,
        ).pack(pady=(18, 2))
        tk.Label(
            form, text="</>  Teknik Informatika  •  Code & Coffee",
            font=(MONO, 9), fg=COLOR_MUTED, bg=COLOR_CARD,
        ).pack(pady=(0, 0))

        # Enter untuk login
        self.master.bind("<Return>", lambda e: self.login())
        self.username_entry.focus_set()

    def _build_field(self, parent, label, var, show=None, prefix=">"):
        tk.Label(
            parent, text=label, font=(MONO, 10, "bold"),
            fg=COLOR_ACCENT, bg=COLOR_CARD,
        ).pack(anchor="w", pady=(0, 4))

        wrapper = tk.Frame(parent, bg=COLOR_FIELD, highlightthickness=1,
                           highlightbackground=COLOR_BORDER, highlightcolor=COLOR_ACCENT)
        wrapper.pack(fill="x", ipady=2, pady=(0, 14))

        tk.Label(
            wrapper, text=prefix, font=(MONO, 12, "bold"),
            fg=COLOR_ACCENT, bg=COLOR_FIELD,
        ).pack(side="left", padx=(12, 4))

        entry = tk.Entry(
            wrapper, textvariable=var, font=(MONO, 12),
            bg=COLOR_FIELD, fg=COLOR_TEXT, relief="flat", bd=0,
            insertbackground=COLOR_ACCENT, width=24,
        )
        if show:
            entry.config(show=show)
        entry.pack(side="left", fill="x", expand=True, pady=8)

        def on_focus_in(_):
            wrapper.config(bg=COLOR_FIELD_FOCUS, highlightbackground=COLOR_ACCENT)
            entry.config(bg=COLOR_FIELD_FOCUS)
            for w in wrapper.winfo_children():
                if isinstance(w, tk.Label):
                    w.config(bg=COLOR_FIELD_FOCUS)

        def on_focus_out(_):
            wrapper.config(bg=COLOR_FIELD, highlightbackground=COLOR_BORDER)
            entry.config(bg=COLOR_FIELD)
            for w in wrapper.winfo_children():
                if isinstance(w, tk.Label):
                    w.config(bg=COLOR_FIELD)

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

        # Tombol show/hide untuk password
        if show:
            self.toggle_btn = tk.Label(
                wrapper, text="show", font=(MONO, 9, "bold"),
                fg=COLOR_ACCENT, bg=COLOR_FIELD, cursor="hand2",
            )
            self.toggle_btn.pack(side="right", padx=12)
            self.toggle_btn.bind("<Button-1>", lambda e: self._toggle_password(entry))

        return entry

    def _toggle_password(self, entry):
        self._password_hidden = not self._password_hidden
        entry.config(show="*" if self._password_hidden else "")
        self.toggle_btn.config(text="show" if self._password_hidden else "hide")

    # ------------------------------------------------------------------- logic
    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Peringatan", "Username dan password tidak boleh kosong.")
            return

        user = User.login(username, password)
        if user:
            messagebox.showinfo("Sukses", f"Selamat datang, {user.get('nama', username)}")
            self.master.unbind("<Return>")
            if self.on_login_success:
                self.on_login_success(user)
            else:
                self.master.destroy()
        else:
            messagebox.showerror("Gagal", "Username atau password salah.")

    def run(self):
        self.master.mainloop()


if __name__ == '__main__':
    LoginView().run()
