import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models.model_absensi import Absensi
from views import theme as T


class MahasiswaDashboard:
    """Dashboard mahasiswa bergaya 'coding' yang seragam dengan halaman login."""

    def __init__(self, master=None, user=None, on_logout=None):
        self.master = master or tk.Tk()
        self.user = user or {}
        self.on_logout = on_logout

        self.master.title("Sistem Absensi  •  Dashboard Mahasiswa  </>")
        self.master.configure(bg=T.COLOR_BG)
        self.master.resizable(False, False)
        T.center_window(self.master, 980, 640)

        Absensi.create_table()
        self.selected_id = None
        self.fields = {}

        self._tree_style = T.style_treeview()
        self._build_ui()
        self._load_absensi()

    # ------------------------------------------------------------------- build
    def _build_ui(self):
        container = tk.Frame(self.master, bg=T.COLOR_BG)
        container.pack(fill="both", expand=True, padx=24, pady=20)

        self._build_header(container)

        body = tk.Frame(container, bg=T.COLOR_BG)
        body.pack(fill="both", expand=True)

        self._build_table(body)
        self._build_form(body)
        self._build_buttons(container)

    def _build_header(self, parent):
        header = tk.Frame(parent, bg=T.COLOR_BG)
        header.pack(fill="x", pady=(0, 16))

        top = tk.Frame(header, bg=T.COLOR_BG)
        top.pack(fill="x")

        tk.Label(
            top, text="</>", font=(T.MONO, 22, "bold"),
            fg=T.COLOR_ACCENT, bg=T.COLOR_BG,
        ).pack(side="left")
        tk.Label(
            top, text="  Dashboard Mahasiswa", font=("Segoe UI", 17, "bold"),
            fg=T.COLOR_TEXT, bg=T.COLOR_BG,
        ).pack(side="left")

        T.make_button(top, "⏻  logout", self.logout, primary=False).pack(side="right")

        nama = self.user.get("nama") or self.user.get("username") or "Mahasiswa"
        tk.Label(
            header, text=f"$ whoami  →  {nama}", font=(T.MONO, 11),
            fg=T.COLOR_ACCENT, bg=T.COLOR_BG, anchor="w",
        ).pack(fill="x", pady=(14, 2))
        tk.Label(
            header, text="// Catat & kelola data kehadiran",
            font=(T.MONO, 10), fg=T.COLOR_MUTED, bg=T.COLOR_BG, anchor="w",
        ).pack(fill="x")

    def _build_table(self, parent):
        editor = tk.Frame(parent, bg=T.COLOR_BG, highlightthickness=1,
                          highlightbackground=T.COLOR_BORDER)
        editor.pack(fill="both", expand=True)

        T.make_title_bar(editor, "absensi.csv")

        tree_frame = tk.Frame(editor, bg=T.COLOR_PANEL)
        tree_frame.pack(fill="both", expand=True)

        columns = ("id", "nama", "kelas", "tanggal", "jam_masuk", "jam_keluar", "status", "keterangan")
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings",
            height=9, selectmode="browse", style=self._tree_style,
        )
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=110, anchor="w")
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("keterangan", width=150)
        self.tree.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview,
            style="Coding.Vertical.TScrollbar",
        )
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("odd", background=T.COLOR_PANEL)
        self.tree.tag_configure("even", background="#1b212a")

    def _build_form(self, parent):
        form_frame = tk.Frame(parent, bg=T.COLOR_BG, highlightthickness=1,
                              highlightbackground=T.COLOR_BORDER)
        form_frame.pack(fill="x", pady=(14, 0))

        tk.Label(
            form_frame, text="# form absensi", font=(T.MONO, 10, "bold"),
            fg=T.COLOR_ACCENT, bg=T.COLOR_BG, anchor="w",
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(12, 8))

        labels = [
            ("nama", "nama"),
            ("kelas", "kelas"),
            ("tanggal (YYYY-MM-DD)", "tanggal"),
            ("jam_masuk", "jam_masuk"),
            ("jam_keluar", "jam_keluar"),
            ("status", "status"),
            ("keterangan", "keterangan"),
        ]
        # Susun 2 kolom field per baris agar ringkas
        for idx, (label_text, field_name) in enumerate(labels):
            grid_row = 1 + idx // 2
            col_base = (idx % 2) * 2

            tk.Label(
                form_frame, text=label_text, font=(T.MONO, 9),
                fg=T.COLOR_MUTED, bg=T.COLOR_BG, anchor="w",
            ).grid(row=grid_row, column=col_base, padx=(14, 6), pady=5, sticky="w")

            entry = tk.Entry(
                form_frame, font=(T.MONO, 10), width=28,
                bg=T.COLOR_FIELD, fg=T.COLOR_TEXT, relief="flat", bd=0,
                insertbackground=T.COLOR_ACCENT,
                highlightthickness=1, highlightbackground=T.COLOR_BORDER,
                highlightcolor=T.COLOR_ACCENT,
            )
            entry.grid(row=grid_row, column=col_base + 1, padx=(0, 16), pady=5,
                       ipady=4, sticky="we")
            self.fields[field_name] = entry

        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)
        # Padding bawah
        tk.Frame(form_frame, bg=T.COLOR_BG, height=8).grid(row=5, column=0)

    def _build_buttons(self, parent):
        button_frame = tk.Frame(parent, bg=T.COLOR_BG)
        button_frame.pack(fill="x", pady=(14, 0))

        T.make_button(button_frame, "+ tambah", self._add_record, primary=True).pack(side="left", padx=(0, 8))
        T.make_button(button_frame, "✎ perbarui", self._update_record, primary=False).pack(side="left", padx=8)
        T.make_button(button_frame, "🗑 hapus", self._delete_record, primary=False).pack(side="left", padx=8)
        T.make_button(button_frame, "✕ bersihkan", self._clear_form, primary=False).pack(side="left", padx=8)
        T.make_button(button_frame, "↻ segarkan", self._load_absensi, primary=False).pack(side="right")

    # ------------------------------------------------------------------- logic
    def _load_absensi(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for idx, record in enumerate(Absensi.all()):
            tag = "even" if idx % 2 == 0 else "odd"
            self.tree.insert("", tk.END, values=(
                record.id,
                record.nama,
                record.kelas,
                record.tanggal,
                record.jam_masuk,
                record.jam_keluar,
                record.status,
                record.keterangan,
            ), tags=(tag,))

    def _get_form_data(self):
        return {name: entry.get().strip() for name, entry in self.fields.items()}

    def _clear_form(self):
        for entry in self.fields.values():
            entry.delete(0, tk.END)
        self.selected_id = None
        selection = self.tree.selection()
        if selection:
            self.tree.selection_remove(selection)

    def _on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        if not values:
            return
        self.selected_id = int(values[0])
        order = ["nama", "kelas", "tanggal", "jam_masuk", "jam_keluar", "status", "keterangan"]
        for i, field_name in enumerate(order):
            self.fields[field_name].delete(0, tk.END)
            self.fields[field_name].insert(0, values[i + 1])

    def _validate_form(self, data):
        if not data["nama"]:
            messagebox.showwarning("Validasi", "Nama tidak boleh kosong.")
            return False
        if not data["tanggal"]:
            messagebox.showwarning("Validasi", "Tanggal tidak boleh kosong.")
            return False
        return True

    def _add_record(self):
        data = self._get_form_data()
        if not self._validate_form(data):
            return
        record = Absensi(
            nama=data["nama"],
            kelas=data["kelas"],
            tanggal=data["tanggal"],
            jam_masuk=data["jam_masuk"],
            jam_keluar=data["jam_keluar"],
            status=data["status"],
            keterangan=data["keterangan"],
        )
        record.save()
        self._load_absensi()
        self._clear_form()

    def _update_record(self):
        if not self.selected_id:
            messagebox.showinfo("Informasi", "Pilih data absensi terlebih dahulu.")
            return
        data = self._get_form_data()
        if not self._validate_form(data):
            return
        record = Absensi.find_by_id(self.selected_id)
        if not record:
            messagebox.showerror("Kesalahan", "Data tidak ditemukan.")
            return
        record.nama = data["nama"]
        record.kelas = data["kelas"]
        record.tanggal = data["tanggal"]
        record.jam_masuk = data["jam_masuk"]
        record.jam_keluar = data["jam_keluar"]
        record.status = data["status"]
        record.keterangan = data["keterangan"]
        record.save()
        self._load_absensi()
        self._clear_form()

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showinfo("Informasi", "Pilih data absensi terlebih dahulu.")
            return
        if messagebox.askyesno("Konfirmasi", "Hapus data absensi yang dipilih?"):
            record = Absensi.find_by_id(self.selected_id)
            if record:
                record.delete()
            self._load_absensi()
            self._clear_form()

    def logout(self):
        if self.on_logout:
            self.on_logout()
        else:
            self.master.destroy()

    def run(self):
        self.master.mainloop()


if __name__ == "__main__":
    MahasiswaDashboard().run()
