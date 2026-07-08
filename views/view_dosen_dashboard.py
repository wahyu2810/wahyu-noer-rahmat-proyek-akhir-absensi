import csv
import os
import sys
import tkinter as tk
from datetime import datetime
from tkinter import ttk, filedialog, messagebox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models.model_absensi import Absensi, STATUS_OPTIONS
from views import theme as T


class DosenDashboard:
    """Dashboard dosen: memantau rekap kehadiran seluruh mahasiswa."""

    FILTER_ALL = "Semua"

    def __init__(self, master=None, user=None, on_logout=None):
        self.master = master or tk.Tk()
        self.user = user or {}
        self.on_logout = on_logout

        self.master.title("Sistem Absensi  •  Dashboard Dosen  </>")
        self.master.configure(bg=T.COLOR_BG)
        self.master.resizable(False, False)
        T.center_window(self.master, 980, 600)

        Absensi.create_table()
        self._tree_style = T.style_treeview()
        self._combo_style = T.style_combobox(self.master)
        self._build_ui()
        self._load_absensi()

    # ------------------------------------------------------------------- build
    def _build_ui(self):
        container = tk.Frame(self.master, bg=T.COLOR_BG)
        container.pack(fill="both", expand=True, padx=24, pady=20)

        self._build_header(container)
        self._build_toolbar(container)
        self._build_table(container)
        self._build_footer(container)

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
            header, text="// Rekap & pantau kehadiran seluruh mahasiswa",
            font=(T.MONO, 10), fg=T.COLOR_MUTED, bg=T.COLOR_BG, anchor="w",
        ).pack(fill="x")

    def _build_toolbar(self, parent):
        toolbar = tk.Frame(parent, bg=T.COLOR_BG)
        toolbar.pack(fill="x", pady=(0, 10))

        tk.Label(
            toolbar, text="# status:", font=(T.MONO, 10),
            fg=T.COLOR_MUTED, bg=T.COLOR_BG,
        ).pack(side="left")

        self.filter_var = tk.StringVar(value=self.FILTER_ALL)
        self.filter_combo = ttk.Combobox(
            toolbar, values=[self.FILTER_ALL] + STATUS_OPTIONS,
            state="readonly", font=(T.MONO, 10), width=10,
            style=self._combo_style, textvariable=self.filter_var,
        )
        self.filter_combo.pack(side="left", padx=(8, 18))
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self._load_absensi())

        tk.Label(
            toolbar, text="# cari nama:", font=(T.MONO, 10),
            fg=T.COLOR_MUTED, bg=T.COLOR_BG,
        ).pack(side="left")

        self.search_var = tk.StringVar()
        search = tk.Entry(
            toolbar, textvariable=self.search_var, font=(T.MONO, 10), width=22,
            bg=T.COLOR_FIELD, fg=T.COLOR_TEXT, relief="flat", bd=0,
            insertbackground=T.COLOR_ACCENT,
            highlightthickness=1, highlightbackground=T.COLOR_BORDER,
            highlightcolor=T.COLOR_ACCENT,
        )
        search.pack(side="left", padx=(8, 0), ipady=4)
        self.search_var.trace_add("write", lambda *_: self._load_absensi())

        T.make_button(toolbar, "↻  refresh", self._load_absensi, primary=True).pack(side="right")
        T.make_button(toolbar, "⬇  ekspor CSV", self._export_csv, primary=False).pack(
            side="right", padx=(0, 8))

    def _build_table(self, parent):
        editor = tk.Frame(parent, bg=T.COLOR_BG, highlightthickness=1,
                          highlightbackground=T.COLOR_BORDER)
        editor.pack(fill="both", expand=True)

        T.make_title_bar(editor, "rekap_absensi.csv")

        table_frame = tk.Frame(editor, bg=T.COLOR_PANEL)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "nama", "kelas", "tanggal", "jam_masuk", "jam_keluar", "status", "keterangan", "koordinat")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            selectmode="browse", style=self._tree_style, height=11,
        )
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=100, anchor="w")
        self.tree.column("id", width=30, anchor="center")
        self.tree.column("status", width=80, anchor="center")
        self.tree.column("keterangan", width=140)
        self.tree.column("koordinat", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview,
            style="Coding.Vertical.TScrollbar",
        )
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)
        scrollbar.pack(side="right", fill="y")

        # Baris belang-seling + warna teks per status
        self.tree.tag_configure("odd", background=T.COLOR_PANEL)
        self.tree.tag_configure("even", background="#1b212a")
        for status, color in T.STATUS_COLORS.items():
            self.tree.tag_configure(f"st_{status}", foreground=color)

    def _build_footer(self, parent):
        footer = tk.Frame(parent, bg=T.COLOR_BG)
        footer.pack(fill="x", pady=(16, 0))

        self.summary_label = tk.Label(
            footer, text="", font=(T.MONO, 10, "bold"),
            fg=T.COLOR_TEXT, bg=T.COLOR_BG, justify="left",
        )
        self.summary_label.pack(side="left")

        self.count_label = tk.Label(
            footer, text="", font=(T.MONO, 10),
            fg=T.COLOR_MUTED, bg=T.COLOR_BG,
        )
        self.count_label.pack(side="right")

    # ------------------------------------------------------------------- logic
    def _load_absensi(self):
        Absensi.auto_update_absensi()
        for row in self.tree.get_children():
            self.tree.delete(row)

        selected = self.filter_var.get()
        keyword = self.search_var.get().strip().lower()
        records = Absensi.all()
        if selected != self.FILTER_ALL:
            records = [r for r in records if (r.status or "").capitalize() == selected]
        if keyword:
            records = [r for r in records if keyword in (r.nama or "").lower()]
        self._shown_records = records

        for idx, record in enumerate(records):
            bg_tag = "even" if idx % 2 == 0 else "odd"
            status = (record.status or "").capitalize()
            st_tag = f"st_{status}" if status in T.STATUS_COLORS else "odd"
            koordinat = f"{record.latitude}, {record.longitude}" if record.latitude and record.longitude else "—"
            
            # Tampilkan keterangan lokasi jika di luar kampus
            ket = record.keterangan or ""
            val_status = status
            if ket == "diluar area kampus":
                val_status = f"{status} (Luar Kampus)"

            self.tree.insert(
                "", "end",
                values=(
                    record.id, record.nama, record.kelas, record.tanggal,
                    record.jam_masuk, record.jam_keluar, val_status, record.keterangan, koordinat,
                ),
                tags=(bg_tag, st_tag),
            )

        self._update_summary(len(records))

    def _update_summary(self, shown):
        counts = Absensi.count_by_status()
        total = sum(counts.values())
        parts = "   ".join(f"{s}: {counts.get(s, 0)}" for s in STATUS_OPTIONS)
        self.summary_label.config(text=f"# {parts}")
        self.count_label.config(text=f"total: {total}   •   ditampilkan: {shown}")

    def _export_csv(self):
        """Ekspor data yang sedang ditampilkan ke berkas CSV."""
        records = getattr(self, "_shown_records", [])
        if not records:
            messagebox.showinfo("Ekspor CSV", "Tidak ada data untuk diekspor.")
            return

        default_name = f"rekap_absensi_{datetime.now():%Y%m%d}.csv"
        path = filedialog.asksaveasfilename(
            title="Simpan rekap absensi",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV", "*.csv"), ("Semua berkas", "*.*")],
        )
        if not path:
            return

        header = ["id", "nama", "kelas", "tanggal", "jam_masuk",
                  "jam_keluar", "status", "keterangan", "latitude", "longitude"]
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for r in records:
                    writer.writerow([
                        r.id, r.nama, r.kelas, r.tanggal, r.jam_masuk,
                        r.jam_keluar, (r.status or "").capitalize(), r.keterangan,
                        r.latitude, r.longitude
                    ])
        except OSError as exc:
            messagebox.showerror("Ekspor CSV", f"Gagal menyimpan berkas:\n{exc}")
            return

        messagebox.showinfo(
            "Ekspor CSV",
            f"{len(records)} baris berhasil diekspor ke:\n{os.path.basename(path)}",
        )

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
