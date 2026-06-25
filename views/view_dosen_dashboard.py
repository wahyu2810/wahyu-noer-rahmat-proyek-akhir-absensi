import os
import sys
import tkinter as tk
from tkinter import ttk

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models.model_users import User
from views import theme as T


class DosenDashboard:
    """Dashboard dosen bergaya 'coding' yang seragam dengan halaman login."""

    def __init__(self, master=None, user=None, on_logout=None):
        self.master = master or tk.Tk()
        self.user = user or {}
        self.on_logout = on_logout

        self.master.title("Sistem Absensi  •  Dashboard Dosen  </>")
        self.master.configure(bg=T.COLOR_BG)
        self.master.resizable(False, False)
        T.center_window(self.master, 820, 560)

        self._tree_style = T.style_treeview()
        self._build_ui()
        self._load_mahasiswa()

    # ------------------------------------------------------------------- build
    def _build_ui(self):
        container = tk.Frame(self.master, bg=T.COLOR_BG)
        container.pack(fill="both", expand=True, padx=24, pady=20)

        self._build_header(container)
        self._build_table(container)
        self._build_footer(container)

    def _build_header(self, parent):
        header = tk.Frame(parent, bg=T.COLOR_BG)
        header.pack(fill="x", pady=(0, 16))

        # Baris logo + prompt + tombol logout
        top = tk.Frame(header, bg=T.COLOR_BG)
        top.pack(fill="x")

        tk.Label(
            top, text="</>", font=(T.MONO, 22, "bold"),
            fg=T.COLOR_ACCENT, bg=T.COLOR_BG,
        ).pack(side="left")
        tk.Label(
            top, text="  Dashboard Dosen", font=("Segoe UI", 17, "bold"),
            fg=T.COLOR_TEXT, bg=T.COLOR_BG,
        ).pack(side="left")

        T.make_button(top, "⏻  logout", self.logout, primary=False).pack(side="right")

        nama_dosen = self.user.get("nama") or self.user.get("username") or "Dosen"
        tk.Label(
            header, text=f"$ whoami  →  {nama_dosen}", font=(T.MONO, 11),
            fg=T.COLOR_ACCENT, bg=T.COLOR_BG, anchor="w",
        ).pack(fill="x", pady=(14, 2))
        tk.Label(
            header, text="// Daftar mahasiswa terdaftar dalam sistem",
            font=(T.MONO, 10), fg=T.COLOR_MUTED, bg=T.COLOR_BG, anchor="w",
        ).pack(fill="x")

    def _build_table(self, parent):
        # Wrapper ala jendela editor
        editor = tk.Frame(parent, bg=T.COLOR_BG, highlightthickness=1,
                          highlightbackground=T.COLOR_BORDER)
        editor.pack(fill="both", expand=True)

        T.make_title_bar(editor, "mahasiswa.csv")

        table_frame = tk.Frame(editor, bg=T.COLOR_PANEL)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "username", "nama", "role")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            selectmode="browse", style=self._tree_style,
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Username")
        self.tree.heading("nama", text="Nama")
        self.tree.heading("role", text="Role")

        self.tree.column("id", width=80, anchor="center")
        self.tree.column("username", width=200, anchor="w")
        self.tree.column("nama", width=300, anchor="w")
        self.tree.column("role", width=160, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview,
            style="Coding.Vertical.TScrollbar",
        )
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)
        scrollbar.pack(side="right", fill="y")

        # Baris belang-seling
        self.tree.tag_configure("odd", background=T.COLOR_PANEL)
        self.tree.tag_configure("even", background="#1b212a")

    def _build_footer(self, parent):
        footer = tk.Frame(parent, bg=T.COLOR_BG)
        footer.pack(fill="x", pady=(16, 0))

        self.count_label = tk.Label(
            footer, text="", font=(T.MONO, 10),
            fg=T.COLOR_MUTED, bg=T.COLOR_BG,
        )
        self.count_label.pack(side="left")

        T.make_button(footer, "↻  refresh", self._load_mahasiswa, primary=True).pack(side="right")

    # ------------------------------------------------------------------- logic
    def _load_mahasiswa(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        mahasiswa_list = User.get_all_mahasiswa()
        for idx, user in enumerate(mahasiswa_list):
            tag = "even" if idx % 2 == 0 else "odd"
            self.tree.insert(
                "", "end",
                values=(
                    user.get("id"),
                    user.get("username"),
                    user.get("nama"),
                    user.get("role"),
                ),
                tags=(tag,),
            )

        self.count_label.config(text=f"# total mahasiswa: {len(mahasiswa_list)}")

    def logout(self):
        if self.on_logout:
            self.on_logout()
        else:
            self.master.destroy()

    def run(self):
        self.master.mainloop()


if __name__ == "__main__":
    demo_user = {"username": "dosen_test", "nama": "Dosen Demo"}
    DosenDashboard(user=demo_user).run()
